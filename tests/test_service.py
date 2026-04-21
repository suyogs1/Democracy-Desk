import pytest
from unittest.mock import MagicMock, patch
from services.gemini_service import GeminiService

@pytest.fixture
def service():
    with patch('google.generativeai.configure'), \
         patch('google.generativeai.GenerativeModel'):
        return GeminiService()

@pytest.mark.asyncio
async def test_get_response_success(service):
    mock_response = MagicMock()
    mock_response.text = "Hello World"
    service.flash_model.generate_content.return_value = mock_response
    
    result = await service.get_response("test prompt")
    assert result == "Hello World"

@pytest.mark.asyncio
async def test_get_response_retry(service):
    mock_response = MagicMock()
    mock_response.text = "Success"
    
    # Fail twice, then succeed
    service.flash_model.generate_content.side_effect = [
        Exception("Fail"),
        Exception("Fail"),
        mock_response
    ]
    
    with patch('time.sleep'): # Avoid waiting during tests
        result = await service.get_response("test", retries=3)
    
    assert result == "Success"
    assert service.flash_model.generate_content.call_count == 3

@pytest.mark.asyncio
async def test_get_structured_response(service):
    mock_response = MagicMock()
    mock_response.text = '{"key": "value"}'
    service.flash_model.generate_content.return_value = mock_response
    
    result = await service.get_structured_response("test prompt")
    assert result == {"key": "value"}
