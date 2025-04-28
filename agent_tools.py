from httpx import AsyncClient
from pydantic_ai import tool
from agent import Deps

async def create_client() -> AsyncClient:
    """Create an HTTP client for making API requests."""
    return AsyncClient()

@tool
async def search_using_brave_api(ctx: RunContext[Deps], query: str) -> str:
    """Wrapper to call the Brave Search tool."""
    client = await create_client()
    ctx.deps.client = client
    result = await ctx.agent.run(query, deps=ctx.deps)
    await client.aclose()  # Close the HTTP client when done
    return result.output
