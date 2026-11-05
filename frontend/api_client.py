
import os

import requests
import streamlit as st
from dotenv import load_dotenv


load_dotenv()

API_URL = os.getenv(
    "API_BASE_URL",
    "http://127.0.0.1:8000"
).rstrip("/")


def get_api_key():
    """
    Read API key from Streamlit secrets or environment variables.
    """

    try:
        api_key = st.secrets.get("API_KEY", "")
    except Exception:
        api_key = ""

    return api_key or os.getenv("API_KEY", "")


def api_request(method, endpoint, **kwargs):
    """
    Centralized API request handler.
    Automatically attaches the API key to every request.
    """

    api_key = get_api_key()

    if not api_key:
        raise RuntimeError(
            "API_KEY is missing. Configure it in the frontend environment."
        )

    headers = kwargs.pop("headers", {})

    headers["X-API-Key"] = api_key

    headers.setdefault("Accept", "application/json")

    if "json" in kwargs:
        headers.setdefault("Content-Type", "application/json")

    url = f"{API_URL}/{endpoint.lstrip('/')}"

    return requests.request(
        method=method.upper(),
        url=url,
        headers=headers,
        timeout=kwargs.pop("timeout", 15),
        **kwargs
    )


def api_get(endpoint, **kwargs):
    return api_request("GET", endpoint, **kwargs)


def api_post(endpoint, **kwargs):
    return api_request("POST", endpoint, **kwargs)


def api_put(endpoint, **kwargs):
    return api_request("PUT", endpoint, **kwargs)


def api_patch(endpoint, **kwargs):
    return api_request("PATCH", endpoint, **kwargs)


def api_delete(endpoint, **kwargs):
    return api_request("DELETE", endpoint, **kwargs)
