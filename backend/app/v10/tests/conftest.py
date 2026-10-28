"""Pytest configuration for Version 10.0 AGEI tests.
Restricts anyio to asyncio backend only (trio not installed).
"""
import pytest


@pytest.fixture(params=["asyncio"])
def anyio_backend(request):
    return request.param
