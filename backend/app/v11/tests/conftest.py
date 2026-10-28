"""Pytest configuration for Version 11.0 Network tests.
Restricts anyio to asyncio backend only (trio not installed).
"""
import pytest


@pytest.fixture(params=["asyncio"])
def anyio_backend(request):
    return request.param
