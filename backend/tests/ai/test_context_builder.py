import pytest
import json
import os
from unittest.mock import patch, MagicMock
from app.ai.context_builder import AIContextBuilder

@patch('app.ai.context_builder.subprocess.run')
def test_context_builder_success(mock_run):
    # Mock the subprocess output
    mock_result = MagicMock()
    mock_result.stdout = json.dumps({
        "page_title": "Test Title",
        "url": "https://test.com",
        "meta": {},
        "navigation": [],
        "buttons": [],
        "links": [],
        "forms": [],
        "inputs": [],
        "tables": [],
        "console_errors": [],
        "network_requests": [],
        "api_calls": [],
        "dom": {},
        "storage": {},
        "cookies": []
    })
    mock_run.return_value = mock_result
    
    builder = AIContextBuilder()
    
    # Ensure cache is clear for this URL (by removing it if exists)
    cache_path = builder._get_cache_path("https://test.com")
    if os.path.exists(cache_path):
        os.remove(cache_path)
        
    context = builder.build_context("https://test.com")
    
    assert context["page_title"] == "Test Title"
    assert context["url"] == "https://test.com"
    mock_run.assert_called_once()
    
    # Test Caching
    mock_run.reset_mock()
    context_cached = builder.build_context("https://test.com")
    assert context_cached["page_title"] == "Test Title"
    mock_run.assert_not_called() # Should hit cache
    
    # Clean up
    if os.path.exists(cache_path):
        os.remove(cache_path)
