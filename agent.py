from __future__ import annotations

import streamlit as st
import pydantic_ai
from pydantic_ai.agent import Agent, RunContext   # sada importamo i RunContext
# ... ostali importi
import os
from dataclasses import dataclass
from typing import Any
import asyncio

from httpx import AsyncClient
from pydantic_ai.providers.openai import OpenAIProvider
from pydantic_ai.providers.openai import OpenAIProvider
from pydantic_ai import ModelRetry

# Debug log: potvrda da je modul učitan
st.write("✅ agent.py modul je učitan")

@dataclass
class Deps:
    client: AsyncClient
    brave_api_key: str | None

# Učitaj Streamlit secrets za OpenRouter i Brave Search API
openrouter_base = st.secrets["OPENROUTER_BASE_URL"]
openrouter_api_key = st.secrets["OPENROUTER_API_KEY"]
brave_api_key = st.secrets.get("BRAVE_API_KEY")  # može biti None ako ne postoji

# Postavi OPENAI_API_KEY environment var kako bi OpenAIProvider (AsyncOpenAI) prihvatio ključ
import os as _os
_os.environ["OPENAI_API_KEY"] = openrouter_api_key

# Debug: prije inicijalizacije agenta
st.write("🚀 Inicijalizacija agenta počinje...")
agent = Agent(
    model='gpt-4o',
    provider=OpenAIProvider(base_url=openrouter_base, api_key=openrouter_api_key),
    system_prompt='You are a helpful AI that can search the web for information using Brave Search API.',
    deps_type=Deps,
    retries=2,
),
    system_prompt='You are a helpful AI that can search the web for information using Brave Search API.',
    deps_type=Deps,
    retries=2,
),
    system_prompt='You are a helpful AI that can search the web for information using Brave Search API.',
    deps_type=Deps,
    retries=2,
)
# Debug: agent je inicijaliziran
st.write("✅ Agent je inicijaliziran")
st.write("✅ Agent je inicijaliziran")

@agent.tool
async def brave_search(ctx: RunContext[Deps], query: str) -> str:
    # Debug: ulazak u alat brave_search
    st.write(f"🔍 Pokreće se brave_search s query: {query}")
    if ctx.deps.brave_api_key is None:
        st.error("Error: Brave API key is missing. Please provide a valid API key.")
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
        # Debug: poslano HTTP zahtjev za Brave Search
        st.write("📡 HTTP zahtjev poslan, čeka se odgovor...")
        response.raise_for_status()
        results = response.json().get('web', {}).get('results', [])

        if not results:
            st.write("ℹ️ Nema rezultata za prikaz.")
            return "No results found."

        output = "\n".join(
            f"Title: {result['title']}\nSummary: {result['description']}\nURL: {result['url']}"
            for result in results
        )
        # Debug: vraćeni rezultati
        st.write(f"✅ brave_search vraća {len(results)} rezultata")
        return output

# ### Chat UI za korisnika
st.markdown("---")
st.markdown("## Chat s Agentom")

# Upiši pojam za pretraživanje
user_query = st.text_input("Unesi pojam za pretraživanje putem Brave Search:")

if st.button("Pretraži"):
    if not user_query:
        st.warning("Molim te unesi pojam prije pretraživanja.")
    else:
        st.write("🔄 Agent pretražuje...")
        # Pokrećemo agenta u async petlji
        try:
            result = asyncio.run(agent.run(user_query))
            st.write("### Rezultat pretraživanja:")
            st.write(result)
        except Exception as e:
            st.error(f"Greška kod izvođenja agenta: {e}")
