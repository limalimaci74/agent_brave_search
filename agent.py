from __future__ import annotations
import os
from dataclasses import dataclass
from typing import Any

from httpx import AsyncClient
from pydantic_ai import Agent, RunContext, ModelRetry

@dataclass
class Deps:
    client: AsyncClient
    brave_api_key: str | None

agent = Agent(
    model_name='openai:gpt-4o',
    system_prompt='You are a helpful AI that can search the web for information using Brave Search API.',
    deps_type=Deps,
    retries=2,
)

@agent.tool
async def brave_search(ctx: RunContext[Deps], query: str) -> str:
    """Search the web using the Brave Search API.

    Args:
        ctx: The run context.
        query: The search query.
    """
    if ctx.deps.brave_api_key is None:
        return "Error: Brave API key is missing. Please provide a valid API key."

    headers = {
        'X-Subscription-Token': ctx.deps.brave_api_key,
        'Accept': 'application/json'
    }

    async with ctx.deps.client.get(
        'https://api.search.brave.com/res/v1/web/search',
        params={'q': query, 'count': '3'},
        headers=headers
    ) as response:
        response.raise_for_status()
        results = response.json().get('web', {}).get('results', [])

        if not results:
            return "No results found."

        output = "\n".join(f"Title: {result['title']}\nSummary: {result['description']}\nURL: {result['url']}"
                           for result in results)
        return output
