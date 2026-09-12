from typing import AsyncGenerator, List, Dict, Any
from groq import AsyncGroq
from app.config import settings
from app.utils.logging import logger

# Max characters for the full prompt sent to Groq.
# groq/compound routes internally; keeping the prompt compact avoids 413 errors.
MAX_PROMPT_CHARS = 24000

SYSTEM_PROMPT_TEMPLATE = """You are a helpful AI assistant.

Answer the user's question using the provided context whenever relevant.

Context:
{context}

Conversation History:
{history}

User Question:
{question}

Rules:

1. Prefer information from the retrieved context.
2. Do not fabricate information.
3. If the answer cannot be determined from the available context, clearly say that you don't have enough information.
4. Keep answers concise for voice conversations.
5. For factual answers, prioritize retrieved information over assumptions."""


class GroqClient:
    """Async Groq LLM API client wrapper."""

    def __init__(self, api_key: str = None, model: str = None):
        self.api_key = api_key or settings.GROQ_API_KEY
        self.model = model or settings.GROQ_MODEL

        if not self.api_key or self.api_key == "your_groq_api_key_here":
            logger.warning("GROQ_API_KEY is not configured in .env!")

        self.client = AsyncGroq(api_key=self.api_key) if self.api_key else None

    def _truncate(self, text: str, max_chars: int) -> str:
        """Truncate text to max_chars, cutting at the last newline before the limit."""
        if len(text) <= max_chars:
            return text
        cut = text[:max_chars]
        last_nl = cut.rfind("\n")
        if last_nl > max_chars // 2:
            cut = cut[:last_nl]
        return cut + "\n[...truncated]"

    def build_prompt(self, question: str, context: str = "", history: str = "") -> str:
        ctx = context.strip() if context else "No relevant context found."
        hist = history.strip() if history else "None"

        # Reserve space for the template skeleton + question
        overhead = len(SYSTEM_PROMPT_TEMPLATE) + len(question) + 200
        budget = MAX_PROMPT_CHARS - overhead

        # Allocate 75% of budget to context, 25% to history
        ctx_budget = int(budget * 0.75)
        hist_budget = budget - ctx_budget

        ctx = self._truncate(ctx, ctx_budget)
        hist = self._truncate(hist, hist_budget)

        prompt = SYSTEM_PROMPT_TEMPLATE.format(
            context=ctx,
            history=hist,
            question=question
        )

        logger.info(f"Prompt length: {len(prompt)} chars (budget: {MAX_PROMPT_CHARS})")
        return prompt

    async def generate_response(self, question: str, context: str = "", history: str = "") -> str:
        if not self.client:
            raise ValueError("Groq API key is missing. Please set GROQ_API_KEY in your .env file.")

        prompt = self.build_prompt(question, context, history)
        logger.info(f"Sending LLM request to Groq (model={self.model})...")

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=1024
            )
            answer = response.choices[0].message.content or ""
            logger.info("Groq LLM request completed successfully.")
            return answer
        except Exception as e:
            logger.error(f"Groq API error: {e}")
            raise RuntimeError(f"Failed to generate response from Groq: {e}")

    async def generate_stream(self, question: str, context: str = "", history: str = "") -> AsyncGenerator[str, None]:
        if not self.client:
            raise ValueError("Groq API key is missing. Please set GROQ_API_KEY in your .env file.")

        prompt = self.build_prompt(question, context, history)
        logger.info(f"Starting streaming LLM request to Groq (model={self.model})...")

        try:
            stream = await self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=1024,
                stream=True
            )
            async for chunk in stream:
                if chunk.choices and chunk.choices[0].delta and chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
            logger.info("Groq LLM streaming completed.")
        except Exception as e:
            logger.error(f"Groq streaming API error: {e}")
            raise RuntimeError(f"Failed to stream response from Groq: {e}")
