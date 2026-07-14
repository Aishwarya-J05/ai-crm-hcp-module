from groq import Groq, GroqError

from app.core import get_settings


class LLMService:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.client = Groq(api_key=self.settings.groq_api_key) if self.settings.groq_api_key else None

    def complete(self, prompt: str) -> str:
        if not self.client:
            return self._fallback(prompt)

        try:
            response = self.client.chat.completions.create(
                model=self.settings.groq_model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert life-sciences CRM assistant for pharmaceutical field representatives.",
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0.2,
            )
            return response.choices[0].message.content or ""
        except GroqError as exc:
            return f"{self._fallback(prompt)} Groq fallback reason: {exc.__class__.__name__}."

    def _fallback(self, prompt: str) -> str:
        trimmed = " ".join(prompt.split())[:220]
        return f"AI draft based on provided interaction context: {trimmed}"
