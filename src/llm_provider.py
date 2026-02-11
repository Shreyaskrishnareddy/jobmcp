"""
Abstracted LLM Provider - Easy to swap between backends
Supports: groq, openai, ollama, custom
"""
import os
from dotenv import load_dotenv

load_dotenv()

LLM_PROVIDER = os.getenv("LLM_PROVIDER", "groq")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")

# Default models for each provider
MODELS = {
    "groq": "llama-3.1-8b-instant",
    "openai": "gpt-4o",
    "ollama": "llama3.1:8b"
}


def get_completion(prompt: str, max_tokens: int = 500, temperature: float = 0.5) -> str:
    """Get completion from configured LLM provider"""

    if LLM_PROVIDER == "groq":
        return _groq_completion(prompt, max_tokens, temperature)
    elif LLM_PROVIDER == "openai":
        return _openai_completion(prompt, max_tokens, temperature)
    elif LLM_PROVIDER == "ollama":
        return _ollama_completion(prompt, max_tokens, temperature)
    else:
        raise ValueError(f"Unknown LLM provider: {LLM_PROVIDER}")


def _groq_completion(prompt: str, max_tokens: int, temperature: float) -> str:
    """Groq API completion"""
    from groq import Groq

    client = Groq(api_key=GROQ_API_KEY)
    response = client.chat.completions.create(
        model=MODELS["groq"],
        messages=[{"role": "user", "content": prompt}],
        max_tokens=max_tokens,
        temperature=temperature
    )
    return response.choices[0].message.content


def _openai_completion(prompt: str, max_tokens: int, temperature: float) -> str:
    """OpenAI API completion"""
    from openai import OpenAI

    client = OpenAI(api_key=OPENAI_API_KEY)
    response = client.chat.completions.create(
        model=MODELS["openai"],
        messages=[{"role": "user", "content": prompt}],
        max_tokens=max_tokens,
        temperature=temperature
    )
    return response.choices[0].message.content


def _ollama_completion(prompt: str, max_tokens: int, temperature: float) -> str:
    """Ollama local completion"""
    import requests

    response = requests.post(
        f"{OLLAMA_HOST}/api/generate",
        json={
            "model": MODELS["ollama"],
            "prompt": prompt,
            "stream": False,
            "options": {
                "num_predict": max_tokens,
                "temperature": temperature
            }
        }
    )
    return response.json()["response"]
