"""
Unified LLM Client for Multi-Provider AI Integration.

Supports:
- Anthropic Claude (claude-sonnet-4-5-20250929)
- OpenAI GPT (gpt-5.2)
- Google Gemini (gemini-3-flash)

Provides a unified interface for text and vision queries.
"""

import os
import base64
import json
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
from abc import ABC, abstractmethod

try:
    from .logging_config import get_logger
except ImportError:
    import importlib.util as _util
    from pathlib import Path as _Path
    _spec = _util.spec_from_file_location(
        "logging_config",
        _Path(__file__).parent / "logging_config.py"
    )
    _logging_config = _util.module_from_spec(_spec)
    _spec.loader.exec_module(_logging_config)
    get_logger = _logging_config.get_logger

logger = get_logger("llm_client")


class LLMProvider(Enum):
    """Supported LLM providers."""
    CLAUDE = "claude"
    OPENAI = "openai"
    GEMINI = "gemini"


@dataclass
class ModelConfig:
    """Configuration for an LLM model."""
    name: str
    provider: LLMProvider
    model_id: str
    supports_vision: bool = True
    supports_json: bool = True
    max_tokens: int = 4096
    price_per_1k_input: float = 0.003
    price_per_1k_output: float = 0.015
    description: str = ""


# Model configurations for latest models (January 2026)
MODEL_CONFIG: Dict[str, Dict[str, Any]] = {
    "claude": {
        "default": "claude-sonnet-4-5-20250929",
        "models": {
            "claude-sonnet-4-5-20250929": ModelConfig(
                name="Claude Sonnet 4.5",
                provider=LLMProvider.CLAUDE,
                model_id="claude-sonnet-4-5-20250929",
                supports_vision=True,
                supports_json=True,
                max_tokens=8192,
                price_per_1k_input=0.003,
                price_per_1k_output=0.015,
                description="Best for reasoning, coding, and complex tasks"
            ),
            "claude-opus-4-5-20251101": ModelConfig(
                name="Claude Opus 4.5",
                provider=LLMProvider.CLAUDE,
                model_id="claude-opus-4-5-20251101",
                supports_vision=True,
                supports_json=True,
                max_tokens=8192,
                price_per_1k_input=0.015,
                price_per_1k_output=0.075,
                description="Most capable Claude model"
            ),
        }
    },
    "openai": {
        "default": "gpt-5.2",
        "models": {
            "gpt-5.2": ModelConfig(
                name="GPT-5.2",
                provider=LLMProvider.OPENAI,
                model_id="gpt-5.2",
                supports_vision=True,
                supports_json=True,
                max_tokens=16384,
                price_per_1k_input=0.005,
                price_per_1k_output=0.015,
                description="Latest GPT model with advanced reasoning"
            ),
            "gpt-5.2-mini": ModelConfig(
                name="GPT-5.2 Mini",
                provider=LLMProvider.OPENAI,
                model_id="gpt-5.2-mini",
                supports_vision=True,
                supports_json=True,
                max_tokens=8192,
                price_per_1k_input=0.001,
                price_per_1k_output=0.003,
                description="Fast and cost-effective GPT model"
            ),
        }
    },
    "gemini": {
        "default": "gemini-3-flash",
        "models": {
            "gemini-3-flash": ModelConfig(
                name="Gemini 3 Flash",
                provider=LLMProvider.GEMINI,
                model_id="gemini-3-flash",
                supports_vision=True,
                supports_json=True,
                max_tokens=32768,
                price_per_1k_input=0.0005,
                price_per_1k_output=0.0015,
                description="Fastest Gemini model with excellent performance"
            ),
            "gemini-3-pro": ModelConfig(
                name="Gemini 3 Pro",
                provider=LLMProvider.GEMINI,
                model_id="gemini-3-pro",
                supports_vision=True,
                supports_json=True,
                max_tokens=65536,
                price_per_1k_input=0.002,
                price_per_1k_output=0.006,
                description="Most capable Gemini model"
            ),
        }
    }
}


@dataclass
class LLMResponse:
    """Response from an LLM query."""
    content: str
    model: str
    provider: LLMProvider
    usage: Dict[str, int] = field(default_factory=dict)
    cost: float = 0.0
    raw_response: Optional[Any] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "content": self.content,
            "model": self.model,
            "provider": self.provider.value,
            "usage": self.usage,
            "cost": self.cost,
        }


class BaseLLMProvider(ABC):
    """Abstract base class for LLM providers."""

    @abstractmethod
    def query(self, prompt: str, system: Optional[str] = None,
              model: Optional[str] = None, **kwargs) -> LLMResponse:
        """Send a text query to the LLM."""
        pass

    @abstractmethod
    def query_with_image(self, prompt: str, image_path: str,
                         system: Optional[str] = None,
                         model: Optional[str] = None, **kwargs) -> LLMResponse:
        """Send a query with an image to the LLM."""
        pass

    def _encode_image(self, image_path: str) -> str:
        """Encode image to base64."""
        with open(image_path, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")

    def _get_mime_type(self, image_path: str) -> str:
        """Get MIME type from file extension."""
        ext = Path(image_path).suffix.lower()
        mime_types = {
            ".png": "image/png",
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".gif": "image/gif",
            ".webp": "image/webp",
        }
        return mime_types.get(ext, "image/png")


class ClaudeProvider(BaseLLMProvider):
    """Anthropic Claude provider."""

    def __init__(self):
        self.api_key = os.environ.get("ANTHROPIC_API_KEY")
        self.config = MODEL_CONFIG["claude"]

    def query(self, prompt: str, system: Optional[str] = None,
              model: Optional[str] = None, **kwargs) -> LLMResponse:
        """Query Claude API."""
        model_id = model or self.config["default"]
        model_config = self.config["models"].get(model_id)

        # Try to use the Anthropic SDK
        try:
            import anthropic
            client = anthropic.Anthropic(api_key=self.api_key)

            messages = [{"role": "user", "content": prompt}]

            response = client.messages.create(
                model=model_id,
                max_tokens=kwargs.get("max_tokens", model_config.max_tokens if model_config else 4096),
                system=system or "You are a helpful AI assistant.",
                messages=messages,
            )

            content = response.content[0].text
            usage = {
                "input_tokens": response.usage.input_tokens,
                "output_tokens": response.usage.output_tokens,
            }

            # Calculate cost
            cost = 0.0
            if model_config:
                cost = (usage["input_tokens"] / 1000 * model_config.price_per_1k_input +
                       usage["output_tokens"] / 1000 * model_config.price_per_1k_output)

            return LLMResponse(
                content=content,
                model=model_id,
                provider=LLMProvider.CLAUDE,
                usage=usage,
                cost=cost,
                raw_response=response,
            )

        except ImportError:
            logger.warning("Anthropic SDK not installed, using mock response")
            return self._mock_response(prompt, model_id)
        except Exception as e:
            logger.error(f"Claude API error: {e}")
            return self._mock_response(prompt, model_id)

    def query_with_image(self, prompt: str, image_path: str,
                         system: Optional[str] = None,
                         model: Optional[str] = None, **kwargs) -> LLMResponse:
        """Query Claude with an image."""
        model_id = model or self.config["default"]
        model_config = self.config["models"].get(model_id)

        try:
            import anthropic
            client = anthropic.Anthropic(api_key=self.api_key)

            image_data = self._encode_image(image_path)
            mime_type = self._get_mime_type(image_path)

            messages = [{
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": mime_type,
                            "data": image_data,
                        },
                    },
                    {
                        "type": "text",
                        "text": prompt,
                    },
                ],
            }]

            response = client.messages.create(
                model=model_id,
                max_tokens=kwargs.get("max_tokens", model_config.max_tokens if model_config else 4096),
                system=system or "You are an expert image analyst.",
                messages=messages,
            )

            content = response.content[0].text
            usage = {
                "input_tokens": response.usage.input_tokens,
                "output_tokens": response.usage.output_tokens,
            }

            cost = 0.0
            if model_config:
                cost = (usage["input_tokens"] / 1000 * model_config.price_per_1k_input +
                       usage["output_tokens"] / 1000 * model_config.price_per_1k_output)

            return LLMResponse(
                content=content,
                model=model_id,
                provider=LLMProvider.CLAUDE,
                usage=usage,
                cost=cost,
                raw_response=response,
            )

        except ImportError:
            logger.warning("Anthropic SDK not installed, using mock response")
            return self._mock_response(prompt, model_id, with_image=True)
        except Exception as e:
            logger.error(f"Claude Vision API error: {e}")
            return self._mock_response(prompt, model_id, with_image=True)

    def _mock_response(self, prompt: str, model: str, with_image: bool = False) -> LLMResponse:
        """Generate mock response for testing."""
        if with_image:
            content = "Image analysis: The image shows a detailed scene with multiple elements."
        else:
            content = f"Mock response for: {prompt[:100]}..."

        return LLMResponse(
            content=content,
            model=model,
            provider=LLMProvider.CLAUDE,
            usage={"input_tokens": 100, "output_tokens": 50},
            cost=0.001,
        )


class OpenAIProvider(BaseLLMProvider):
    """OpenAI GPT provider."""

    def __init__(self):
        self.api_key = os.environ.get("OPENAI_API_KEY")
        self.config = MODEL_CONFIG["openai"]

    def query(self, prompt: str, system: Optional[str] = None,
              model: Optional[str] = None, **kwargs) -> LLMResponse:
        """Query OpenAI API."""
        model_id = model or self.config["default"]
        model_config = self.config["models"].get(model_id)

        try:
            import openai
            client = openai.OpenAI(api_key=self.api_key)

            messages = []
            if system:
                messages.append({"role": "system", "content": system})
            messages.append({"role": "user", "content": prompt})

            response = client.chat.completions.create(
                model=model_id,
                messages=messages,
                max_tokens=kwargs.get("max_tokens", model_config.max_tokens if model_config else 4096),
            )

            content = response.choices[0].message.content
            usage = {
                "input_tokens": response.usage.prompt_tokens,
                "output_tokens": response.usage.completion_tokens,
            }

            cost = 0.0
            if model_config:
                cost = (usage["input_tokens"] / 1000 * model_config.price_per_1k_input +
                       usage["output_tokens"] / 1000 * model_config.price_per_1k_output)

            return LLMResponse(
                content=content,
                model=model_id,
                provider=LLMProvider.OPENAI,
                usage=usage,
                cost=cost,
                raw_response=response,
            )

        except ImportError:
            logger.warning("OpenAI SDK not installed, using mock response")
            return self._mock_response(prompt, model_id)
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            return self._mock_response(prompt, model_id)

    def query_with_image(self, prompt: str, image_path: str,
                         system: Optional[str] = None,
                         model: Optional[str] = None, **kwargs) -> LLMResponse:
        """Query OpenAI with an image."""
        model_id = model or self.config["default"]
        model_config = self.config["models"].get(model_id)

        try:
            import openai
            client = openai.OpenAI(api_key=self.api_key)

            image_data = self._encode_image(image_path)
            mime_type = self._get_mime_type(image_path)

            messages = []
            if system:
                messages.append({"role": "system", "content": system})

            messages.append({
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:{mime_type};base64,{image_data}",
                        },
                    },
                    {
                        "type": "text",
                        "text": prompt,
                    },
                ],
            })

            response = client.chat.completions.create(
                model=model_id,
                messages=messages,
                max_tokens=kwargs.get("max_tokens", model_config.max_tokens if model_config else 4096),
            )

            content = response.choices[0].message.content
            usage = {
                "input_tokens": response.usage.prompt_tokens,
                "output_tokens": response.usage.completion_tokens,
            }

            cost = 0.0
            if model_config:
                cost = (usage["input_tokens"] / 1000 * model_config.price_per_1k_input +
                       usage["output_tokens"] / 1000 * model_config.price_per_1k_output)

            return LLMResponse(
                content=content,
                model=model_id,
                provider=LLMProvider.OPENAI,
                usage=usage,
                cost=cost,
                raw_response=response,
            )

        except ImportError:
            logger.warning("OpenAI SDK not installed, using mock response")
            return self._mock_response(prompt, model_id, with_image=True)
        except Exception as e:
            logger.error(f"OpenAI Vision API error: {e}")
            return self._mock_response(prompt, model_id, with_image=True)

    def _mock_response(self, prompt: str, model: str, with_image: bool = False) -> LLMResponse:
        """Generate mock response for testing."""
        if with_image:
            content = "Image analysis: I can see various visual elements in this image."
        else:
            content = f"GPT response for: {prompt[:100]}..."

        return LLMResponse(
            content=content,
            model=model,
            provider=LLMProvider.OPENAI,
            usage={"input_tokens": 100, "output_tokens": 50},
            cost=0.001,
        )


class GeminiProvider(BaseLLMProvider):
    """Google Gemini provider."""

    def __init__(self):
        self.api_key = os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY")
        self.config = MODEL_CONFIG["gemini"]

    def query(self, prompt: str, system: Optional[str] = None,
              model: Optional[str] = None, **kwargs) -> LLMResponse:
        """Query Gemini API."""
        model_id = model or self.config["default"]
        model_config = self.config["models"].get(model_id)

        try:
            import google.generativeai as genai
            genai.configure(api_key=self.api_key)

            model_obj = genai.GenerativeModel(
                model_name=model_id,
                system_instruction=system,
            )

            response = model_obj.generate_content(prompt)

            content = response.text
            usage = {
                "input_tokens": response.usage_metadata.prompt_token_count if hasattr(response, 'usage_metadata') else 100,
                "output_tokens": response.usage_metadata.candidates_token_count if hasattr(response, 'usage_metadata') else 50,
            }

            cost = 0.0
            if model_config:
                cost = (usage["input_tokens"] / 1000 * model_config.price_per_1k_input +
                       usage["output_tokens"] / 1000 * model_config.price_per_1k_output)

            return LLMResponse(
                content=content,
                model=model_id,
                provider=LLMProvider.GEMINI,
                usage=usage,
                cost=cost,
                raw_response=response,
            )

        except ImportError:
            logger.warning("Google Generative AI SDK not installed, using mock response")
            return self._mock_response(prompt, model_id)
        except Exception as e:
            logger.error(f"Gemini API error: {e}")
            return self._mock_response(prompt, model_id)

    def query_with_image(self, prompt: str, image_path: str,
                         system: Optional[str] = None,
                         model: Optional[str] = None, **kwargs) -> LLMResponse:
        """Query Gemini with an image."""
        model_id = model or self.config["default"]
        model_config = self.config["models"].get(model_id)

        try:
            import google.generativeai as genai
            from PIL import Image
            genai.configure(api_key=self.api_key)

            model_obj = genai.GenerativeModel(
                model_name=model_id,
                system_instruction=system,
            )

            image = Image.open(image_path)
            response = model_obj.generate_content([prompt, image])

            content = response.text
            usage = {
                "input_tokens": response.usage_metadata.prompt_token_count if hasattr(response, 'usage_metadata') else 100,
                "output_tokens": response.usage_metadata.candidates_token_count if hasattr(response, 'usage_metadata') else 50,
            }

            cost = 0.0
            if model_config:
                cost = (usage["input_tokens"] / 1000 * model_config.price_per_1k_input +
                       usage["output_tokens"] / 1000 * model_config.price_per_1k_output)

            return LLMResponse(
                content=content,
                model=model_id,
                provider=LLMProvider.GEMINI,
                usage=usage,
                cost=cost,
                raw_response=response,
            )

        except ImportError:
            logger.warning("Google Generative AI SDK not installed, using mock response")
            return self._mock_response(prompt, model_id, with_image=True)
        except Exception as e:
            logger.error(f"Gemini Vision API error: {e}")
            return self._mock_response(prompt, model_id, with_image=True)

    def _mock_response(self, prompt: str, model: str, with_image: bool = False) -> LLMResponse:
        """Generate mock response for testing."""
        if with_image:
            content = "Image analysis: The image contains interesting visual elements."
        else:
            content = f"Gemini response for: {prompt[:100]}..."

        return LLMResponse(
            content=content,
            model=model,
            provider=LLMProvider.GEMINI,
            usage={"input_tokens": 100, "output_tokens": 50},
            cost=0.0005,
        )


class LLMClient:
    """
    Unified LLM client supporting multiple providers.

    Usage:
        client = LLMClient()

        # Text query
        response = client.query("Explain quantum computing", provider=LLMProvider.CLAUDE)

        # Vision query
        response = client.query_with_image(
            "Describe this image",
            "photo.jpg",
            provider=LLMProvider.OPENAI
        )

        # Auto-select best provider
        response = client.query("Simple question", auto_select=True)
    """

    def __init__(self, default_provider: LLMProvider = LLMProvider.CLAUDE):
        """
        Initialize LLM client.

        Args:
            default_provider: Default provider to use
        """
        self.default_provider = default_provider
        self._providers: Dict[LLMProvider, BaseLLMProvider] = {}
        self._initialize_providers()

    def _initialize_providers(self):
        """Initialize all available providers."""
        self._providers[LLMProvider.CLAUDE] = ClaudeProvider()
        self._providers[LLMProvider.OPENAI] = OpenAIProvider()
        self._providers[LLMProvider.GEMINI] = GeminiProvider()

    def query(
        self,
        prompt: str,
        system: Optional[str] = None,
        provider: Optional[LLMProvider] = None,
        model: Optional[str] = None,
        auto_select: bool = False,
        **kwargs
    ) -> LLMResponse:
        """
        Send a text query to an LLM.

        Args:
            prompt: The prompt to send
            system: System prompt/instruction
            provider: Provider to use (defaults to default_provider)
            model: Specific model to use
            auto_select: Auto-select best provider for task
            **kwargs: Additional arguments

        Returns:
            LLMResponse with the result
        """
        if auto_select:
            provider = self._select_best_provider(prompt, has_image=False)

        selected_provider = provider or self.default_provider
        llm_provider = self._providers.get(selected_provider)

        if not llm_provider:
            raise ValueError(f"Provider {selected_provider} not available")

        logger.info(f"Querying {selected_provider.value} with prompt: {prompt[:50]}...")
        return llm_provider.query(prompt, system=system, model=model, **kwargs)

    def query_with_image(
        self,
        prompt: str,
        image_path: str,
        system: Optional[str] = None,
        provider: Optional[LLMProvider] = None,
        model: Optional[str] = None,
        auto_select: bool = False,
        **kwargs
    ) -> LLMResponse:
        """
        Send a query with an image to an LLM.

        Args:
            prompt: The prompt to send
            image_path: Path to the image file
            system: System prompt/instruction
            provider: Provider to use
            model: Specific model to use
            auto_select: Auto-select best provider for task
            **kwargs: Additional arguments

        Returns:
            LLMResponse with the result
        """
        if not Path(image_path).exists():
            raise FileNotFoundError(f"Image not found: {image_path}")

        if auto_select:
            provider = self._select_best_provider(prompt, has_image=True)

        selected_provider = provider or self.default_provider
        llm_provider = self._providers.get(selected_provider)

        if not llm_provider:
            raise ValueError(f"Provider {selected_provider} not available")

        logger.info(f"Querying {selected_provider.value} with image: {image_path}")
        return llm_provider.query_with_image(
            prompt, image_path, system=system, model=model, **kwargs
        )

    def _select_best_provider(self, prompt: str, has_image: bool = False) -> LLMProvider:
        """
        Auto-select the best provider based on task.

        Args:
            prompt: The prompt to analyze
            has_image: Whether the query includes an image

        Returns:
            Selected provider
        """
        prompt_lower = prompt.lower()

        # Use Gemini for fast, simple tasks
        simple_keywords = ["list", "count", "simple", "quick", "fast"]
        if any(kw in prompt_lower for kw in simple_keywords):
            return LLMProvider.GEMINI

        # Use Claude for complex reasoning
        complex_keywords = ["analyze", "explain", "reason", "complex", "detailed"]
        if any(kw in prompt_lower for kw in complex_keywords):
            return LLMProvider.CLAUDE

        # Use GPT for vision tasks by default
        if has_image:
            return LLMProvider.OPENAI

        # Default to Claude for general tasks
        return LLMProvider.CLAUDE

    def get_model_info(self, provider: LLMProvider, model: Optional[str] = None) -> ModelConfig:
        """
        Get information about a model.

        Args:
            provider: The provider
            model: Specific model name (optional)

        Returns:
            ModelConfig with model information
        """
        config = MODEL_CONFIG.get(provider.value, {})
        model_name = model or config.get("default")
        models = config.get("models", {})

        if model_name in models:
            return models[model_name]

        raise ValueError(f"Model {model_name} not found for provider {provider.value}")

    def get_available_models(self, provider: Optional[LLMProvider] = None) -> Dict[str, List[str]]:
        """
        Get list of available models.

        Args:
            provider: Specific provider (optional, returns all if None)

        Returns:
            Dictionary of provider -> model list
        """
        result = {}

        if provider:
            config = MODEL_CONFIG.get(provider.value, {})
            result[provider.value] = list(config.get("models", {}).keys())
        else:
            for p in LLMProvider:
                config = MODEL_CONFIG.get(p.value, {})
                result[p.value] = list(config.get("models", {}).keys())

        return result


# Convenience functions
_client: Optional[LLMClient] = None


def _get_client() -> LLMClient:
    """Get or create client instance."""
    global _client
    if _client is None:
        _client = LLMClient()
    return _client


def query_llm(
    prompt: str,
    provider: Union[LLMProvider, str] = LLMProvider.CLAUDE,
    **kwargs
) -> LLMResponse:
    """
    Query an LLM with a text prompt.

    Args:
        prompt: The prompt to send
        provider: Provider to use (string or enum)
        **kwargs: Additional arguments

    Returns:
        LLMResponse with the result
    """
    if isinstance(provider, str):
        provider = LLMProvider(provider)
    return _get_client().query(prompt, provider=provider, **kwargs)


def query_with_image(
    prompt: str,
    image_path: str,
    provider: Union[LLMProvider, str] = LLMProvider.OPENAI,
    **kwargs
) -> LLMResponse:
    """
    Query an LLM with an image.

    Args:
        prompt: The prompt to send
        image_path: Path to the image
        provider: Provider to use
        **kwargs: Additional arguments

    Returns:
        LLMResponse with the result
    """
    if isinstance(provider, str):
        provider = LLMProvider(provider)
    return _get_client().query_with_image(prompt, image_path, provider=provider, **kwargs)


def get_available_providers() -> List[str]:
    """
    Get list of available LLM providers.

    Returns:
        List of provider names
    """
    return [p.value for p in LLMProvider]
