import pytest
from unittest.mock import patch, MagicMock
from google.genai.errors import ClientError
from translator.gemini import GeminiTranslatorProvider

@pytest.mark.asyncio
async def test_gemini_translator_success(translation_settings):
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.text = '["Translated A", "Translated B"]'
    mock_client.models.generate_content.return_value = mock_response
    
    with patch("google.genai.Client", return_value=mock_client):
        translator = GeminiTranslatorProvider(api_key="mock_key")
        results = await translator.translate_batch(
            ["name1", "name2"], "Auto Detect", "English", translation_settings
        )
        
    assert results == ["Translated A", "Translated B"]
    mock_client.models.generate_content.assert_called_once()

@pytest.mark.asyncio
async def test_gemini_translator_rate_limit_retry(translation_settings):
    mock_client = MagicMock()
    
    import requests
    # First attempt raises 429 ClientError, second succeeds
    error_response = MagicMock(spec=requests.Response)
    error_response.status_code = 429
    error_response.json.return_value = {
        "error": {
            "code": 429,
            "message": "Quota exceeded",
            "status": "RESOURCE_EXHAUSTED"
        }
    }
    rate_limit_error = ClientError(429, error_response)
    
    success_response = MagicMock()
    success_response.text = '["Translated A"]'
    
    mock_client.models.generate_content.side_effect = [rate_limit_error, success_response]
    
    # Patch asyncio.sleep so the rate limit backoff is instant in tests
    with patch("google.genai.Client", return_value=mock_client), \
         patch("asyncio.sleep", return_value=None) as mock_sleep:
        translator = GeminiTranslatorProvider(api_key="mock_key")
        results = await translator.translate_batch(
            ["name1"], "Auto Detect", "English", translation_settings
        )
        
    assert results == ["Translated A"]
    assert mock_client.models.generate_content.call_count == 2
    # Verify exponential backoff first sleep was 5.0 seconds
    mock_sleep.assert_called_once_with(5.0)

@pytest.mark.asyncio
async def test_gemini_translator_failure_propagates(translation_settings):
    mock_client = MagicMock()
    
    # Constant failures
    import requests
    error_response = MagicMock(spec=requests.Response)
    error_response.status_code = 429
    error_response.json.return_value = {
        "error": {
            "code": 429,
            "message": "Quota exceeded",
            "status": "RESOURCE_EXHAUSTED"
        }
    }
    rate_limit_error = ClientError(429, error_response)
    mock_client.models.generate_content.side_effect = [rate_limit_error] * 5
    
    with patch("google.genai.Client", return_value=mock_client), \
         patch("asyncio.sleep", return_value=None):
        translator = GeminiTranslatorProvider(api_key="mock_key")
        with pytest.raises(RuntimeError) as exc_info:
            await translator.translate_batch(
                ["name1"], "Auto Detect", "English", translation_settings
            )
            
    assert "Gemini translation failed" in str(exc_info.value)
