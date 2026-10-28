"""Pytest configuration for Version 9.0 Universal Platform tests.

Configures anyio to run only with asyncio backend (trio not installed).
"""
import pytest


@pytest.fixture(params=["asyncio"])
def anyio_backend(request):
    return request.param
