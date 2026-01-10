"""
Prompt Optimizer for Image Generation.

Uses LLMs to enhance, score, and generate variations of prompts
for better image generation results.

Features:
- Prompt enhancement (vague → detailed)
- Quality scoring (0-1)
- Variation generation
- Style inference from context
"""

import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum

try:
    from .logging_config import get_logger
    from .llm_client import LLMClient, LLMProvider, query_llm
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

    _spec = _util.spec_from_file_location(
        "llm_client",
        _Path(__file__).parent / "llm_client.py"
    )
    _llm_client = _util.module_from_spec(_spec)
    _spec.loader.exec_module(_llm_client)
    LLMClient = _llm_client.LLMClient
    LLMProvider = _llm_client.LLMProvider
    query_llm = _llm_client.query_llm

logger = get_logger("prompt_optimizer")


class PromptStyle(Enum):
    """Predefined prompt styles."""
    PHOTOREALISTIC = "photorealistic"
    ARTISTIC = "artistic"
    ILLUSTRATION = "illustration"
    ABSTRACT = "abstract"
    MINIMALIST = "minimalist"
    CINEMATIC = "cinematic"
    ANIME = "anime"
    VINTAGE = "vintage"


@dataclass
class PromptAnalysis:
    """Analysis result for a prompt."""
    original: str
    score: float
    issues: List[str] = field(default_factory=list)
    strengths: List[str] = field(default_factory=list)
    suggestions: List[str] = field(default_factory=list)
    detected_style: Optional[PromptStyle] = None
    word_count: int = 0
    has_style_keywords: bool = False
    has_quality_keywords: bool = False
    has_composition_keywords: bool = False


# Quality keywords that improve prompt effectiveness
QUALITY_KEYWORDS = [
    "high quality", "detailed", "professional", "masterpiece",
    "8k", "4k", "hdr", "ultra", "sharp", "crisp"
]

STYLE_KEYWORDS = {
    PromptStyle.PHOTOREALISTIC: ["realistic", "photo", "photograph", "lifelike"],
    PromptStyle.ARTISTIC: ["artistic", "painted", "brush strokes", "fine art"],
    PromptStyle.ILLUSTRATION: ["illustration", "illustrated", "drawing", "sketch"],
    PromptStyle.ABSTRACT: ["abstract", "geometric", "shapes", "non-representational"],
    PromptStyle.MINIMALIST: ["minimal", "minimalist", "simple", "clean"],
    PromptStyle.CINEMATIC: ["cinematic", "movie", "dramatic lighting", "film"],
    PromptStyle.ANIME: ["anime", "manga", "japanese", "cel shaded"],
    PromptStyle.VINTAGE: ["vintage", "retro", "old", "classic", "nostalgic"],
}

COMPOSITION_KEYWORDS = [
    "foreground", "background", "centered", "rule of thirds",
    "symmetrical", "close-up", "wide shot", "portrait", "landscape"
]

# Enhancement templates
ENHANCEMENT_TEMPLATES = {
    "general": [
        "high quality, detailed, professional",
        "sharp focus, good lighting",
        "vibrant colors, well composed",
    ],
    "portrait": [
        "professional lighting, soft shadows",
        "detailed facial features, expressive",
        "studio quality, bokeh background",
    ],
    "landscape": [
        "dramatic lighting, golden hour",
        "sweeping vista, atmospheric",
        "high dynamic range, vivid colors",
    ],
    "product": [
        "product photography, studio lighting",
        "clean background, professional",
        "high detail, commercial quality",
    ],
}

# System prompts for LLM enhancement
ENHANCE_SYSTEM_PROMPT = """You are an expert prompt engineer for AI image generation.
Your task is to enhance user prompts to produce better image results.

Guidelines:
1. Add specific visual details (colors, lighting, composition)
2. Include quality modifiers (detailed, high quality, professional)
3. Specify artistic style if appropriate
4. Keep the core intent of the original prompt
5. Make the prompt 2-4 sentences maximum
6. Use descriptive adjectives and concrete nouns

Return ONLY the enhanced prompt, nothing else."""

VARIATION_SYSTEM_PROMPT = """You are an expert prompt engineer for AI image generation.
Generate variations of the given prompt that explore different interpretations.

Guidelines:
1. Keep the core subject/theme
2. Vary the style, mood, or setting
3. Each variation should be distinct but related
4. Maintain similar quality level
5. Return as a JSON array of strings

Return ONLY a JSON array like: ["variation 1", "variation 2", "variation 3"]"""


class PromptOptimizer:
    """
    Optimizes prompts for better image generation.

    Usage:
        optimizer = PromptOptimizer()

        # Enhance a prompt
        enhanced = optimizer.enhance("pretty flower")
        # Returns: "A beautiful flower with delicate petals, soft natural lighting..."

        # Score a prompt
        score = optimizer.score_prompt("A detailed landscape")
        # Returns: 0.75

        # Generate variations
        variations = optimizer.generate_variations("sunset beach", count=3)
    """

    def __init__(self, use_llm: bool = True):
        """
        Initialize the optimizer.

        Args:
            use_llm: Whether to use LLM for enhancement (False = rule-based only)
        """
        self.use_llm = use_llm
        self._llm_client = LLMClient() if use_llm else None

    def enhance(
        self,
        prompt: str,
        style: Optional[PromptStyle] = None,
        context: Optional[str] = None,
        use_llm: Optional[bool] = None
    ) -> str:
        """
        Enhance a prompt for better generation results.

        Args:
            prompt: Original prompt to enhance
            style: Desired style (optional)
            context: Additional context about the image
            use_llm: Override instance setting for LLM usage

        Returns:
            Enhanced prompt string
        """
        should_use_llm = use_llm if use_llm is not None else self.use_llm

        # Analyze the prompt first
        analysis = self.analyze(prompt)

        # If already good quality, return with minor enhancements
        if analysis.score > 0.8:
            return self._minor_enhance(prompt, style)

        if should_use_llm and self._llm_client:
            return self._llm_enhance(prompt, style, context)
        else:
            return self._rule_based_enhance(prompt, style, analysis)

    def _llm_enhance(
        self,
        prompt: str,
        style: Optional[PromptStyle] = None,
        context: Optional[str] = None
    ) -> str:
        """Use LLM to enhance the prompt."""
        try:
            user_prompt = f"Enhance this image generation prompt: '{prompt}'"
            if style:
                user_prompt += f"\nDesired style: {style.value}"
            if context:
                user_prompt += f"\nContext: {context}"

            response = self._llm_client.query(
                prompt=user_prompt,
                system=ENHANCE_SYSTEM_PROMPT,
                provider=LLMProvider.GEMINI,  # Use Gemini for speed
            )

            enhanced = response.content.strip()
            # Remove quotes if present
            enhanced = enhanced.strip('"\'')

            logger.info(f"Enhanced prompt: {prompt[:30]}... → {enhanced[:50]}...")
            return enhanced

        except Exception as e:
            logger.warning(f"LLM enhancement failed: {e}, falling back to rules")
            return self._rule_based_enhance(prompt, style, self.analyze(prompt))

    def _rule_based_enhance(
        self,
        prompt: str,
        style: Optional[PromptStyle] = None,
        analysis: Optional[PromptAnalysis] = None
    ) -> str:
        """Enhance prompt using rules."""
        enhanced_parts = [prompt]

        # Add style keywords if not present
        if style:
            style_words = STYLE_KEYWORDS.get(style, [])
            if style_words and not any(w in prompt.lower() for w in style_words):
                enhanced_parts.append(style_words[0])

        # Add quality keywords if missing
        if analysis and not analysis.has_quality_keywords:
            enhanced_parts.append("high quality, detailed")

        # Add composition keywords for short prompts
        if analysis and analysis.word_count < 5:
            enhanced_parts.append("well composed, professional")

        # Detect subject type and add relevant enhancements
        prompt_lower = prompt.lower()
        if any(word in prompt_lower for word in ["person", "portrait", "face", "man", "woman"]):
            enhanced_parts.extend(ENHANCEMENT_TEMPLATES["portrait"][:1])
        elif any(word in prompt_lower for word in ["landscape", "mountain", "ocean", "sky"]):
            enhanced_parts.extend(ENHANCEMENT_TEMPLATES["landscape"][:1])
        elif any(word in prompt_lower for word in ["product", "item", "object"]):
            enhanced_parts.extend(ENHANCEMENT_TEMPLATES["product"][:1])
        else:
            enhanced_parts.extend(ENHANCEMENT_TEMPLATES["general"][:1])

        return ", ".join(enhanced_parts)

    def _minor_enhance(self, prompt: str, style: Optional[PromptStyle] = None) -> str:
        """Apply minor enhancements to already good prompts."""
        if style and style.value not in prompt.lower():
            return f"{prompt}, {style.value} style"
        return prompt

    def analyze(self, prompt: str) -> PromptAnalysis:
        """
        Analyze a prompt for quality and characteristics.

        Args:
            prompt: Prompt to analyze

        Returns:
            PromptAnalysis with detailed breakdown
        """
        prompt_lower = prompt.lower()
        words = prompt.split()

        # Detect characteristics
        has_quality = any(kw in prompt_lower for kw in QUALITY_KEYWORDS)
        has_composition = any(kw in prompt_lower for kw in COMPOSITION_KEYWORDS)

        # Detect style
        detected_style = None
        for style, keywords in STYLE_KEYWORDS.items():
            if any(kw in prompt_lower for kw in keywords):
                detected_style = style
                break

        has_style = detected_style is not None

        # Calculate issues and suggestions
        issues = []
        suggestions = []
        strengths = []

        if len(words) < 3:
            issues.append("Prompt is too short")
            suggestions.append("Add more descriptive details")

        if len(words) > 50:
            issues.append("Prompt may be too long")
            suggestions.append("Consider condensing to key details")

        if not has_quality:
            suggestions.append("Add quality modifiers like 'detailed' or 'high quality'")
        else:
            strengths.append("Contains quality keywords")

        if not has_style:
            suggestions.append("Consider specifying an artistic style")
        else:
            strengths.append(f"Clear style: {detected_style.value}")

        if not has_composition:
            suggestions.append("Add composition details (close-up, wide shot, etc.)")
        else:
            strengths.append("Good composition guidance")

        # Calculate score (0-1)
        score = self._calculate_score(
            word_count=len(words),
            has_quality=has_quality,
            has_style=has_style,
            has_composition=has_composition,
            issues=issues,
        )

        return PromptAnalysis(
            original=prompt,
            score=score,
            issues=issues,
            strengths=strengths,
            suggestions=suggestions,
            detected_style=detected_style,
            word_count=len(words),
            has_style_keywords=has_style,
            has_quality_keywords=has_quality,
            has_composition_keywords=has_composition,
        )

    def _calculate_score(
        self,
        word_count: int,
        has_quality: bool,
        has_style: bool,
        has_composition: bool,
        issues: List[str],
    ) -> float:
        """Calculate prompt quality score."""
        score = 0.0

        # Word count contribution (0-0.3)
        if 5 <= word_count <= 30:
            score += 0.3
        elif 3 <= word_count < 5 or 30 < word_count <= 50:
            score += 0.15
        elif word_count >= 3:
            score += 0.05

        # Quality keywords (0-0.25)
        if has_quality:
            score += 0.25

        # Style keywords (0-0.25)
        if has_style:
            score += 0.25

        # Composition keywords (0-0.2)
        if has_composition:
            score += 0.2

        # Penalty for issues
        score -= len(issues) * 0.05

        return max(0.0, min(1.0, score))

    def score_prompt(self, prompt: str) -> float:
        """
        Score a prompt's quality (0-1).

        Args:
            prompt: Prompt to score

        Returns:
            Quality score between 0 and 1
        """
        analysis = self.analyze(prompt)
        return analysis.score

    def generate_variations(
        self,
        prompt: str,
        count: int = 3,
        use_llm: Optional[bool] = None
    ) -> List[str]:
        """
        Generate variations of a prompt.

        Args:
            prompt: Base prompt
            count: Number of variations to generate
            use_llm: Override instance setting for LLM usage

        Returns:
            List of prompt variations
        """
        should_use_llm = use_llm if use_llm is not None else self.use_llm

        if should_use_llm and self._llm_client:
            return self._llm_variations(prompt, count)
        else:
            return self._rule_based_variations(prompt, count)

    def _llm_variations(self, prompt: str, count: int) -> List[str]:
        """Generate variations using LLM."""
        try:
            user_prompt = f"Generate {count} variations of this image prompt: '{prompt}'"

            response = self._llm_client.query(
                prompt=user_prompt,
                system=VARIATION_SYSTEM_PROMPT,
                provider=LLMProvider.GEMINI,
            )

            # Parse JSON response
            import json
            content = response.content.strip()

            # Handle various response formats
            if content.startswith("["):
                variations = json.loads(content)
            else:
                # Extract JSON array from response
                match = re.search(r'\[.*\]', content, re.DOTALL)
                if match:
                    variations = json.loads(match.group())
                else:
                    # Fallback: split by newlines
                    variations = [line.strip().strip('"\'') for line in content.split('\n')
                                 if line.strip() and not line.startswith('#')]

            return variations[:count]

        except Exception as e:
            logger.warning(f"LLM variation generation failed: {e}")
            return self._rule_based_variations(prompt, count)

    def _rule_based_variations(self, prompt: str, count: int) -> List[str]:
        """Generate variations using rules."""
        variations = []

        # Style variations
        styles = [PromptStyle.PHOTOREALISTIC, PromptStyle.ARTISTIC,
                 PromptStyle.CINEMATIC, PromptStyle.MINIMALIST]

        for i, style in enumerate(styles[:count]):
            style_keywords = STYLE_KEYWORDS.get(style, [])
            if style_keywords:
                variation = f"{prompt}, {style_keywords[0]} style"
                variations.append(variation)

        # If we need more variations, add quality modifiers
        while len(variations) < count:
            modifiers = ["vibrant and detailed", "soft and ethereal",
                        "dramatic lighting", "warm tones"]
            idx = len(variations) % len(modifiers)
            variations.append(f"{prompt}, {modifiers[idx]}")

        return variations[:count]

    def suggest_improvements(self, prompt: str) -> List[str]:
        """
        Get specific improvement suggestions.

        Args:
            prompt: Prompt to analyze

        Returns:
            List of improvement suggestions
        """
        analysis = self.analyze(prompt)
        return analysis.suggestions

    def infer_style(self, prompt: str) -> Optional[PromptStyle]:
        """
        Infer the intended style from a prompt.

        Args:
            prompt: Prompt to analyze

        Returns:
            Detected style or None
        """
        analysis = self.analyze(prompt)
        return analysis.detected_style


# Singleton instance
_optimizer: Optional[PromptOptimizer] = None


def _get_optimizer() -> PromptOptimizer:
    """Get or create optimizer instance."""
    global _optimizer
    if _optimizer is None:
        _optimizer = PromptOptimizer()
    return _optimizer


# Convenience functions
def enhance_prompt(
    prompt: str,
    style: Optional[PromptStyle] = None,
    **kwargs
) -> str:
    """
    Enhance a prompt for better generation.

    Args:
        prompt: Original prompt
        style: Desired style
        **kwargs: Additional options

    Returns:
        Enhanced prompt
    """
    return _get_optimizer().enhance(prompt, style=style, **kwargs)


def generate_variations(prompt: str, count: int = 3) -> List[str]:
    """
    Generate variations of a prompt.

    Args:
        prompt: Base prompt
        count: Number of variations

    Returns:
        List of variations
    """
    return _get_optimizer().generate_variations(prompt, count)


def score_prompt(prompt: str) -> float:
    """
    Score a prompt's quality.

    Args:
        prompt: Prompt to score

    Returns:
        Score between 0 and 1
    """
    return _get_optimizer().score_prompt(prompt)
