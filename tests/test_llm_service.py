
from backend.services.llm_service import get_llm_service


def test_gemini_connection():

    llm = get_llm_service()

    try:
        response = llm.generate_response(
            prompt="Reply with exactly: Gemini connection successful."
        )

        assert response
        print(response)

    finally:
        llm.close()


if __name__ == "__main__":
    test_gemini_connection()
