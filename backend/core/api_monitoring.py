from datetime import datetime, timezone, timedelta
from time import perf_counter

from sqlalchemy import desc, func
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

from backend.database.connection import SessionLocal
from backend.database.tables import APIMonitorLog


class APIMonitor:

    def record_request(
        self,
        method,
        endpoint,
        status_code,
        response_time_ms,
        error=None
    ):

        db = SessionLocal()

        try:
            log = APIMonitorLog(
                method=method,
                endpoint=endpoint,
                status_code=status_code,
                response_time_ms=round(response_time_ms, 2),
                error=error
            )

            db.add(log)
            db.commit()

        except Exception as db_error:
            db.rollback()
            print(f"API monitoring database error: {db_error}")

        finally:
            db.close()

    def get_summary(self):

        db = SessionLocal()

        try:
            total_records = db.query(
                func.count(APIMonitorLog.id)
            ).scalar() or 0

            records = (
                db.query(APIMonitorLog)
                .order_by(desc(APIMonitorLog.created_at))
                .limit(5000)
                .all()
            )

            total = len(records)

            successful = sum(
                1 for item in records
                if 200 <= item.status_code < 400
            )

            failed = sum(
                1 for item in records
                if item.status_code >= 400
            )

            other = total - successful - failed

            average_response_time = (
                sum(item.response_time_ms for item in records) / total
                if total else 0
            )

            endpoint_stats = {}

            for item in records:

                endpoint = item.endpoint

                if endpoint not in endpoint_stats:
                    endpoint_stats[endpoint] = {
                        "request_count": 0,
                        "successful": 0,
                        "failed": 0,
                        "total_response_time": 0
                    }

                stats = endpoint_stats[endpoint]

                stats["request_count"] += 1
                stats["total_response_time"] += item.response_time_ms

                if 200 <= item.status_code < 400:
                    stats["successful"] += 1

                elif item.status_code >= 400:
                    stats["failed"] += 1

            endpoints = []

            for endpoint, stats in endpoint_stats.items():

                count = stats["request_count"]

                endpoints.append({
                    "endpoint": endpoint,
                    "request_count": count,
                    "successful": stats["successful"],
                    "failed": stats["failed"],
                    "average_response_time_ms": round(
                        stats["total_response_time"] / count, 2
                    )
                })

            endpoints.sort(
                key=lambda item: item["request_count"],
                reverse=True
            )

            slow_requests = [
                item for item in records
                if item.response_time_ms >= 1000
            ]

            errors = [
                item for item in records
                if item.status_code >= 400
            ]

            recent_requests = [
                self._serialize(item) for item in records[:50]
            ]

            recent_errors = [
                self._serialize(item) for item in errors[:20]
            ]

            slow_requests = [
                self._serialize(item) for item in slow_requests[:20]
            ]

            seven_days_ago = datetime.now(timezone.utc) - timedelta(days=7)

            daily_records = (
                db.query(APIMonitorLog)
                .filter(APIMonitorLog.created_at >= seven_days_ago)
                .order_by(APIMonitorLog.created_at.asc())
                .all()
            )

            daily_stats = {}

            for item in daily_records:

                date_key = item.created_at.date().isoformat()

                if date_key not in daily_stats:
                    daily_stats[date_key] = {
                        "date": date_key,
                        "requests": 0,
                        "failed": 0
                    }

                daily_stats[date_key]["requests"] += 1

                if item.status_code >= 400:
                    daily_stats[date_key]["failed"] += 1

            return {
                "total_requests": total_records,
                "records_analyzed": total,
                "successful_requests": successful,
                "failed_requests": failed,
                "other_requests": other,
                "average_response_time_ms": round(
                    average_response_time, 2
                ),
                "endpoint_statistics": endpoints,
                "slow_requests": slow_requests,
                "recent_errors": recent_errors,
                "recent_requests": recent_requests,
                "daily_statistics": list(daily_stats.values())
            }

        finally:
            db.close()

    @staticmethod
    def _serialize(item):

        return {
            "id": item.id,
            "timestamp": (
                item.created_at.isoformat()
                if item.created_at else None
            ),
            "method": item.method,
            "endpoint": item.endpoint,
            "status_code": item.status_code,
            "response_time_ms": item.response_time_ms,
            "error": item.error
        }


api_monitor = APIMonitor()


class APIMonitoringMiddleware(BaseHTTPMiddleware):

    async def dispatch(self, request: Request, call_next):

        start_time = perf_counter()
        status_code = 500
        error_message = None

        try:
            response = await call_next(request)
            status_code = response.status_code

            if status_code >= 400:
                error_message = f"HTTP {status_code}"

            return response

        except Exception as error:
            error_message = str(error)
            raise

        finally:

            response_time_ms = (
                perf_counter() - start_time
            ) * 1000

            self_path = request.url.path

            api_monitor.record_request(
                method=request.method,
                endpoint=self_path,
                status_code=status_code,
                response_time_ms=response_time_ms,
                error=error_message
            )