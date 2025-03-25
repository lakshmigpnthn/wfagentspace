import unittest
from unittest.mock import patch, MagicMock, AsyncMock
import json
import sys
import asyncio
from io import StringIO
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../src'))

# Import the module to test
import mcp_integration

class TestMCPURLFetchAgentWithGemini(unittest.TestCase):
    """Test cases for the MCP URL fetch agent application with Gemini LLM."""

    def setUp(self):
        """Set up test environment before each test."""
        # Create mock objects for all the dependencies
        self.mock_app = MagicMock()
        self.mock_agent = MagicMock()
        self.mock_llm = MagicMock()
        self.mock_logger = MagicMock()
        self.mock_context = MagicMock()
        
        # Set up the context with config including Gemini settings
        self.mock_context.config.model_dump.return_value = {
            "execution_engine": "asyncio",
            "logger": {"type": "file", "level": "debug"},
            "mcp": {
                "servers": {
                    "fetch": {
                        "command": "uvx",
                        "args": ["mcp-server-fetch"]
                    }
                }
            },
            "openai": {
                "api_key": "mocked-openai-key",
                "default_model": "gpt-4o-mini"
            },
            "gemini": {
                "api_key": "mocked-gemini-key",
                "default_model": "gemini-1.5-pro"
            }
        }
        
        # Connect the mock app to context and logger
        self.mock_app.context = self.mock_context
        self.mock_app.logger = self.mock_logger
        
        # Configure AsyncMock for the Agent methods
        self.mock_agent.list_tools = AsyncMock()
        self.mock_agent.attach_llm = AsyncMock()
        self.mock_agent.__aenter__ = AsyncMock()
        self.mock_agent.__aexit__ = AsyncMock()
        
        # Configure the LLM mock
        self.mock_llm.generate_str = AsyncMock()
        
        # Create a mock for the GeminiAugmentedLLM class
        self.mock_gemini_llm_class = MagicMock()
        self.mock_gemini_llm_instance = MagicMock()
        self.mock_gemini_llm_instance.generate_str = AsyncMock()
        
        # Sample JSON response that would be fetched from the URL
        self.sample_json_response = {
            "applications": [
                {
                    "name": "mortgagelending",
                    "status": "error",
                    "issue": "Memory leak in user session handling",
                    "details": "Application crashes when user load exceeds 500 concurrent users"
                },
                {
                    "name": "payment",
                    "status": "degraded",
                    "issue": "Slow response times",
                    "details": "Average response time increased from 200ms to 1.2s"
                }
            ]
        }

    @patch('mcp_integration.MCPApp')
    @patch('mcp_integration.Agent')
    async def test_url_fetch_with_gemini_llm(self, mock_agent_class, mock_app_class):
        """Test URL fetch using Gemini LLM."""
        # Configure mocks
        mock_app_class.return_value = self.mock_app
        self.mock_app.run.return_value.__aenter__.return_value = self.mock_app
        
        mock_agent_class.return_value = self.mock_agent
        
        # Mock the tool listing response
        tools_response = MagicMock()
        tools_response.model_dump.return_value = {
            "tools": [
                {
                    "name": "fetch_url",
                    "description": "Fetches content from a URL"
                }
            ]
        }
        self.mock_agent.list_tools.return_value = tools_response
        
        # Create a mock for GeminiAugmentedLLM
        mock_gemini_llm_class = MagicMock()
        mock_gemini_llm_instance = MagicMock()
        mock_gemini_llm_instance.generate_str = AsyncMock()
        expected_response = "According to the data, the mortgagelending application has a memory leak in user session handling, causing it to crash when there are more than 500 concurrent users."
        mock_gemini_llm_instance.generate_str.return_value = expected_response
        
        # Mock the LLM attachment to return Gemini instance
        self.mock_agent.attach_llm.return_value = mock_gemini_llm_instance
        
        # Create modified version of the URL fetch function that uses Gemini
        async def url_fetch_with_gemini():
            async with self.mock_app.run() as agent_app:
                logger = agent_app.logger
                context = agent_app.context
                
                logger.info("Current config:", data=context.config.model_dump())
                
                finder_agent = self.mock_agent
                
                async with finder_agent:
                    logger.info("finder: Connected to server, calling list_tools...")
                    result = await finder_agent.list_tools()
                    logger.info("Tools available:", data=result.model_dump())
                    
                    # Use Gemini instead of OpenAI
                    llm = await finder_agent.attach_llm(mock_gemini_llm_class)
                    
                    result = await llm.generate_str(
                        message="What is the issue with mortgagelending application?",
                        request_params=mcp_integration.RequestParams(
                            modelPreferences=mcp_integration.ModelPreferences(
                                costPriority=0.1, speedPriority=0.2, intelligencePriority=0.7
                            ),
                        ),
                    )
                    logger.info(f"Paragraph as a tweet: {result}")
                    return result
        
        # Execute the modified function
        result = await url_fetch_with_gemini()
        
        # Assertions
        mock_app_class.assert_called_once()
        self.mock_app.run.assert_called_once()
        self.mock_agent.__aenter__.assert_called_once()
        self.mock_agent.list_tools.assert_called_once()
        self.mock_agent.attach_llm.assert_called_once_with(mock_gemini_llm_class)
        mock_gemini_llm_instance.generate_str.assert_called_once()
        self.assertEqual(result, expected_response)

    @patch('mcp_integration.MCPApp')
    @patch('mcp_integration.Agent')
    async def test_gemini_llm_error_handling(self, mock_agent_class, mock_app_class):
        """Test error handling when Gemini LLM encounters an error."""
        # Configure mocks
        mock_app_class.return_value = self.mock_app
        self.mock_app.run.return_value.__aenter__.return_value = self.mock_app
        
        mock_agent_class.return_value = self.mock_agent
        
        # Mock the tool listing response
        tools_response = MagicMock()
        tools_response.model_dump.return_value = {
            "tools": [
                {
                    "name": "fetch_url",
                    "description": "Fetches content from a URL"
                }
            ]
        }
        self.mock_agent.list_tools.return_value = tools_response
        
        # Create a mock for GeminiAugmentedLLM
        mock_gemini_llm_class = MagicMock()
        mock_gemini_llm_instance = MagicMock()
        mock_gemini_llm_instance.generate_str = AsyncMock()
        mock_gemini_llm_instance.generate_str.side_effect = Exception("Gemini API rate limit exceeded")
        
        # Mock the LLM attachment to return Gemini instance
        self.mock_agent.attach_llm.return_value = mock_gemini_llm_instance
        
        # Create modified version of the URL fetch function that uses Gemini
        async def url_fetch_with_gemini_error():
            async with self.mock_app.run() as agent_app:
                logger = agent_app.logger
                context = agent_app.context
                
                logger.info("Current config:", data=context.config.model_dump())
                
                finder_agent = self.mock_agent
                
                async with finder_agent:
                    logger.info("finder: Connected to server, calling list_tools...")
                    result = await finder_agent.list_tools()
                    logger.info("Tools available:", data=result.model_dump())
                    
                    # Use Gemini instead of OpenAI
                    llm = await finder_agent.attach_llm(mock_gemini_llm_class)
                    
                    result = await llm.generate_str(
                        message="What is the issue with mortgagelending application?",
                        request_params=mcp_integration.RequestParams(
                            modelPreferences=mcp_integration.ModelPreferences(
                                costPriority=0.1, speedPriority=0.2, intelligencePriority=0.7
                            ),
                        ),
                    )
                    logger.info(f"Paragraph as a tweet: {result}")
                    return result
        
        # Execute the modified function and expect an exception
        with self.assertRaises(Exception) as context:
            await url_fetch_with_gemini_error()
        
        # Assertions
        self.assertTrue("Gemini API rate limit exceeded" in str(context.exception))
        mock_app_class.assert_called_once()
        self.mock_agent.__aenter__.assert_called_once()
        self.mock_agent.list_tools.assert_called_once()
        self.mock_agent.attach_llm.assert_called_once_with(mock_gemini_llm_class)
        mock_gemini_llm_instance.generate_str.assert_called_once()

    @patch('mcp_integration.MCPApp')
    @patch('mcp_integration.Agent')
    async def test_llm_fallback_from_gemini_to_openai(self, mock_agent_class, mock_app_class):
        """Test fallback behavior from Gemini to OpenAI when Gemini fails."""
        # Configure mocks
        mock_app_class.return_value = self.mock_app
        self.mock_app.run.return_value.__aenter__.return_value = self.mock_app
        
        mock_agent_class.return_value = self.mock_agent
        
        # Mock the tool listing response
        tools_response = MagicMock()
        tools_response.model_dump.return_value = {
            "tools": [
                {
                    "name": "fetch_url",
                    "description": "Fetches content from a URL"
                }
            ]
        }
        self.mock_agent.list_tools.return_value = tools_response
        
        # Create a mock for GeminiAugmentedLLM
        mock_gemini_llm_class = MagicMock()
        mock_gemini_llm_instance = MagicMock()
        mock_gemini_llm_instance.generate_str = AsyncMock()
        mock_gemini_llm_instance.generate_str.side_effect = Exception("Gemini API error")
        
        # Create a mock for OpenAIAugmentedLLM (fallback)
        mock_openai_llm_class = MagicMock()
        mock_openai_llm_instance = MagicMock()
        mock_openai_llm_instance.generate_str = AsyncMock()
        expected_response = "OpenAI fallback response: The mortgagelending application has a memory leak."
        mock_openai_llm_instance.generate_str.return_value = expected_response
        
        # Mock attachment behavior for both LLMs
        self.mock_agent.attach_llm = AsyncMock(side_effect=[
            mock_gemini_llm_instance,  # First call returns Gemini
            mock_openai_llm_instance   # Second call returns OpenAI
        ])
        
        # Create modified version of the URL fetch function with fallback
        async def url_fetch_with_fallback():
            async with self.mock_app.run() as agent_app:
                logger = agent_app.logger
                context = agent_app.context
                
                logger.info("Current config:", data=context.config.model_dump())
                
                finder_agent = self.mock_agent
                
                async with finder_agent:
                    logger.info("finder: Connected to server, calling list_tools...")
                    result = await finder_agent.list_tools()
                    logger.info("Tools available:", data=result.model_dump())
                    
                    # Try Gemini first
                    try:
                        llm = await finder_agent.attach_llm(mock_gemini_llm_class)
                        result = await llm.generate_str(
                            message="What is the issue with mortgagelending application?",
                            request_params=mcp_integration.RequestParams(
                                modelPreferences=mcp_integration.ModelPreferences(
                                    costPriority=0.1, speedPriority=0.2, intelligencePriority=0.7
                                ),
                            ),
                        )
                    except Exception as e:
                        logger.info(f"Gemini LLM failed with error: {str(e)}, falling back to OpenAI")
                        # Fallback to OpenAI
                        llm = await finder_agent.attach_llm(mock_openai_llm_class)
                        result = await llm.generate_str(
                            message="What is the issue with mortgagelending application?",
                            request_params=mcp_integration.RequestParams(
                                modelPreferences=mcp_integration.ModelPreferences(
                                    costPriority=0.1, speedPriority=0.2, intelligencePriority=0.7
                                ),
                            ),
                        )
                    
                    logger.info(f"Final response: {result}")
                    return result
        
        # Execute the function with fallback
        result = await url_fetch_with_fallback()
        
        # Assertions
        mock_app_class.assert_called_once()
        self.mock_agent.__aenter__.assert_called_once()
        self.mock_agent.list_tools.assert_called_once()
        self.assertEqual(self.mock_agent.attach_llm.call_count, 2)  # Called twice for both LLMs
        mock_gemini_llm_instance.generate_str.assert_called_once()
        mock_openai_llm_instance.generate_str.assert_called_once()
        self.assertEqual(result, expected_response)

    @patch('mcp_integration.MCPApp')
    @patch('mcp_integration.Agent')
    async def test_gemini_with_different_model_version(self, mock_agent_class, mock_app_class):
        """Test using a different Gemini model version."""
        # Configure mocks
        mock_app_class.return_value = self.mock_app
        self.mock_app.run.return_value.__aenter__.return_value = self.mock_app
        
        mock_agent_class.return_value = self.mock_agent
        
        # Mock the tool listing response
        tools_response = MagicMock()
        tools_response.model_dump.return_value = {
            "tools": [
                {
                    "name": "fetch_url",
                    "description": "Fetches content from a URL"
                }
            ]
        }
        self.mock_agent.list_tools.return_value = tools_response
        
        # Create a mock for GeminiAugmentedLLM with specific model
        mock_gemini_llm_class = MagicMock()
        mock_gemini_llm_instance = MagicMock()
        mock_gemini_llm_instance.generate_str = AsyncMock()
        mock_gemini_llm_instance.model_name = "gemini-1.5-flash"  # Different model version
        expected_response = "Gemini Flash model response: The mortgagelending application has memory issues."
        mock_gemini_llm_instance.generate_str.return_value = expected_response
        
        # Mock the LLM attachment to return Gemini instance
        self.mock_agent.attach_llm.return_value = mock_gemini_llm_instance
        
        # Create modified version of the URL fetch function with model params
        async def url_fetch_with_gemini_model():
            async with self.mock_app.run() as agent_app:
                logger = agent_app.logger
                context = agent_app.context
                
                logger.info("Current config:", data=context.config.model_dump())
                
                finder_agent = self.mock_agent
                
                async with finder_agent:
                    logger.info("finder: Connected to server, calling list_tools...")
                    result = await finder_agent.list_tools()
                    logger.info("Tools available:", data=result.model_dump())
                    
                    # Use specific Gemini model
                    llm = await finder_agent.attach_llm(mock_gemini_llm_class, model_name="gemini-1.5-flash")
                    
                    result = await llm.generate_str(
                        message="What is the issue with mortgagelending application?",
                        request_params=mcp_integration.RequestParams(
                            modelPreferences=mcp_integration.ModelPreferences(
                                costPriority=0.3, speedPriority=0.6, intelligencePriority=0.1  # Prioritize speed
                            ),
                        ),
                    )
                    logger.info(f"Gemini Flash response: {result}")
                    return result
        
        # Execute the function
        result = await url_fetch_with_gemini_model()
        
        # Assertions
        mock_app_class.assert_called_once()
        self.mock_agent.__aenter__.assert_called_once()
        self.mock_agent.list_tools.assert_called_once()
        self.mock_agent.attach_llm.assert_called_once_with(mock_gemini_llm_class, model_name="gemini-1.5-flash")
        mock_gemini_llm_instance.generate_str.assert_called_once()
        self.assertEqual(result, expected_response)


# Helper function to run async tests
def run_async_test(coro):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


if __name__ == '__main__':
    # Make unittest discover and run async tests
    for method_name in dir(TestMCPURLFetchAgentWithGemini):
        if method_name.startswith('test_') and asyncio.iscoroutinefunction(getattr(TestMCPURLFetchAgentWithGemini, method_name)):
            old_method = getattr(TestMCPURLFetchAgentWithGemini, method_name)
            
            def wrapper(old_method=old_method):
                def wrapped_test(self):
                    return run_async_test(old_method(self))
                return wrapped_test
            
            setattr(TestMCPURLFetchAgentWithGemini, method_name, wrapper())
    
    unittest.main()