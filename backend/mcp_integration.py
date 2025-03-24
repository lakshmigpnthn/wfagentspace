import asyncio
import time

from mcp_agent.app import MCPApp
from mcp_agent.config import (
    Settings,
    LoggerSettings,
    MCPSettings,
    MCPServerSettings,
    OpenAISettings,
    AnthropicSettings,
)
from mcp_agent.agents.agent import Agent
from mcp_agent.workflows.llm.augmented_llm import RequestParams
from mcp_agent.workflows.llm.llm_selector import ModelPreferences
from mcp_agent.workflows.llm.augmented_llm_anthropic import AnthropicAugmentedLLM
from mcp_agent.workflows.llm.augmented_llm_openai import OpenAIAugmentedLLM


settings = Settings(
    execution_engine="asyncio",
    logger=LoggerSettings(type="file", level="debug"),
    mcp=MCPSettings(
        servers={
            "fetch": MCPServerSettings(
                command="uvx",
                args=["mcp-server-fetch"],
            )
        }
    ),
    openai=OpenAISettings(
        api_key="to be filled",
        default_model="gpt-4o-mini",
    )
)

app = MCPApp(name="mcp_url_fetch_agent", settings=settings)


async def url_fetch_usage():
    """
    Demonstrates the usage of the MCPApp and an agent to fetch and process content from URLs.

    This function initializes an MCP application, connects to a server, and uses an agent to 
    fetch tools and attach an LLM (Large Language Model). It performs a multi-turn conversation 
    to process a user query about application issues based on JSON content fetched from a URL.

    Steps:
    1. Initializes the MCP application and logs the current configuration.
    2. Creates an agent with instructions to fetch and process content from URLs.
    3. Connects the agent to a server and lists available tools.
    4. Attaches an OpenAI-based LLM to the agent.
    5. Uses the LLM to generate a response to a user query.

    Example Query:
    - "What is the issue with mortgagelending application?"

    Returns:
        None
    """
    async with app.run() as agent_app:
        logger = agent_app.logger
        context = agent_app.context

        logger.info("Current config:", data=context.config.model_dump())

        finder_agent = Agent(
            name="finder",
            instruction="""You are an agent with access to fetch content from the URLs. Your job is to identify the closest match to a user's request, make the appropriate tool calls, 
            and return the CONTENTS of the closest match.
            Read the content of https://storage.googleapis.com/store-anything/app-err-output.json which is in json format and answer the user query.
            The user's query will be about the applications and their issues mentioned in this json.""",
            server_names=["fetch"],
        )

        async with finder_agent:
            logger.info("finder: Connected to server, calling list_tools...")
            result = await finder_agent.list_tools()
            logger.info("Tools available:", data=result.model_dump())

            llm = await finder_agent.attach_llm(OpenAIAugmentedLLM)

            # Multi-turn conversations
            result = await llm.generate_str(
                message="What is the issue with mortgagelending application?",
                request_params=RequestParams(
                    modelPreferences=ModelPreferences(
                        costPriority=0.1, speedPriority=0.2, intelligencePriority=0.7
                    ),
                ),
            )
            logger.info(f"Paragraph as a tweet: {result}")


if __name__ == "__main__":
    start = time.time()
    asyncio.run(url_fetch_usage())
    end = time.time()
    t = end - start

    print(f"Total run time: {t:.2f}s")
