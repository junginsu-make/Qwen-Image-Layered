"""
Quality Validator for AI-Generated Images.

Uses Vision LLMs (GPT-5.2, Claude, Gemini) to:
- Assess image quality
- Detect artifacts and issues
- Validate layer decomposition
- Rate generation results
- Provide improvement suggestions
"""

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple, Union
import json

try:
    from .logging_config import get_logger
    from .llm_client import LLMClient, LLMProvider, query_with_image
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
    query_with_image = _llm_client.query_with_image

logger = get_logger("quality_validator")


class QualityLevel(Enum):
    """Quality assessment levels."""
    EXCELLENT = "excellent"
    GOOD = "good"
    ACCEPTABLE = "acceptable"
    POOR = "poor"
    UNACCEPTABLE = "unacceptable"


class ArtifactType(Enum):
    """Types of image artifacts."""
    BLUR = "blur"
    NOISE = "noise"
    DISTORTION = "distortion"
    COLOR_BANDING = "color_banding"
    JPEG_ARTIFACTS = "jpeg_artifacts"
    ALIASING = "aliasing"
    MOIRE = "moire"
    HALO = "halo"
    EDGE_BLEEDING = "edge_bleeding"
    TRANSPARENCY_ISSUE = "transparency_issue"
    TEXT_CORRUPTION = "text_corruption"
    ANATOMICAL_ERROR = "anatomical_error"


@dataclass
class QualityScore:
    """Quality assessment result."""
    overall: float  # 0-1 score
    details: Dict[str, float] = field(default_factory=dict)
    issues: List[str] = field(default_factory=list)
    suggestions: List[str] = field(default_factory=list)
    level: QualityLevel = QualityLevel.ACCEPTABLE
    artifacts: List[Dict[str, Any]] = field(default_factory=list)
    prompt_alignment: float = 0.8  # How well image matches prompt

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "overall": self.overall,
            "details": self.details,
            "issues": self.issues,
            "suggestions": self.suggestions,
            "level": self.level.value,
            "artifacts": self.artifacts,
            "prompt_alignment": self.prompt_alignment,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "QualityScore":
        """Create from dictionary."""
        return cls(
            overall=data.get("overall", 0.5),
            details=data.get("details", {}),
            issues=data.get("issues", []),
            suggestions=data.get("suggestions", []),
            level=QualityLevel(data.get("level", "acceptable")),
            artifacts=data.get("artifacts", []),
            prompt_alignment=data.get("prompt_alignment", 0.8),
        )


@dataclass
class LayerValidation:
    """Validation result for layer decomposition."""
    is_valid: bool
    layer_count: int
    expected_count: Optional[int] = None
    quality_scores: List[float] = field(default_factory=list)
    issues: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    overall_quality: float = 0.8

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "is_valid": self.is_valid,
            "layer_count": self.layer_count,
            "expected_count": self.expected_count,
            "quality_scores": self.quality_scores,
            "issues": self.issues,
            "recommendations": self.recommendations,
            "overall_quality": self.overall_quality,
        }


# Quality assessment prompts
QUALITY_ASSESSMENT_PROMPT = """Analyze this image for quality and issues.

Rate the following aspects from 0-100:
1. Clarity (sharpness, focus)
2. Composition (framing, balance)
3. Color accuracy (natural colors, no banding)
4. Technical quality (no artifacts, proper exposure)
5. Overall aesthetic appeal

List any issues found:
- Blur or softness
- Noise or grain
- Color problems
- Artifacts
- Distortions
- Other issues

Respond in JSON format:
{
  "scores": {
    "clarity": 85,
    "composition": 90,
    "color": 80,
    "technical": 75,
    "aesthetic": 85
  },
  "overall": 83,
  "issues": ["slight blur in corners"],
  "suggestions": ["increase sharpness"]
}"""

PROMPT_ALIGNMENT_PROMPT = """Compare this image to the intended prompt: "{prompt}"

Rate how well the image matches the prompt on these aspects:
1. Subject accuracy (0-100)
2. Style match (0-100)
3. Detail accuracy (0-100)
4. Overall alignment (0-100)

Identify any mismatches or missing elements.

Respond in JSON format:
{
  "scores": {
    "subject": 90,
    "style": 85,
    "detail": 80,
    "alignment": 85
  },
  "mismatches": ["background color differs from prompt"],
  "missing": ["requested texture not visible"]
}"""

LAYER_VALIDATION_PROMPT = """Analyze these image layers for quality.

Check for:
1. Clean separation between layers
2. Proper alpha channel handling
3. Edge quality (no halos, bleeding)
4. Content completeness

Rate each layer's quality and identify any issues.

Respond in JSON format:
{
  "layer_quality": [85, 90, 75, 80],
  "issues": ["layer 3 has edge bleeding"],
  "recommendations": ["apply edge smoothing to layer 3"]
}"""


class QualityValidator:
    """
    Validates image quality using Vision LLMs.

    Usage:
        validator = QualityValidator()

        # Validate generation result
        score = validator.validate("generated.png", task="generation")
        print(f"Quality: {score.overall:.0%}")

        # Check prompt alignment
        alignment = validator.check_prompt_alignment(
            "generated.png",
            "A sunset over mountains"
        )

        # Detect artifacts
        artifacts = validator.detect_artifacts("image.png")
    """

    def __init__(self, use_llm: bool = True):
        """
        Initialize the validator.

        Args:
            use_llm: Whether to use Vision LLM for assessment
        """
        self.use_llm = use_llm
        self._llm_client = LLMClient() if use_llm else None

    def validate(
        self,
        image_path: str,
        task: str = "generation",
        prompt: Optional[str] = None,
    ) -> QualityScore:
        """
        Validate an image's quality.

        Args:
            image_path: Path to image file
            task: Type of task (generation, edit, decompose)
            prompt: Original prompt for alignment check

        Returns:
            QualityScore with assessment
        """
        # Check if file exists
        if not Path(image_path).exists():
            return self._create_mock_score(0.0, ["Image file not found"])

        if self.use_llm and self._llm_client:
            return self._llm_validate(image_path, task, prompt)
        else:
            return self._rule_based_validate(image_path, task)

    def _llm_validate(
        self,
        image_path: str,
        task: str,
        prompt: Optional[str] = None,
    ) -> QualityScore:
        """Use Vision LLM for quality assessment."""
        try:
            # Get quality assessment
            response = self._llm_client.query_with_image(
                prompt=QUALITY_ASSESSMENT_PROMPT,
                image_path=image_path,
                provider=LLMProvider.OPENAI,  # GPT-5.2 for vision
            )

            # Parse response
            content = response.content.strip()
            data = self._parse_json_response(content)

            scores = data.get("scores", {})
            overall = data.get("overall", 75) / 100

            # Determine quality level
            level = self._score_to_level(overall)

            # Build details
            details = {k: v / 100 for k, v in scores.items()}

            # Check prompt alignment if provided
            alignment = 0.8
            if prompt:
                alignment = self._check_alignment_score(image_path, prompt)

            return QualityScore(
                overall=overall,
                details=details,
                issues=data.get("issues", []),
                suggestions=data.get("suggestions", []),
                level=level,
                artifacts=[],
                prompt_alignment=alignment,
            )

        except Exception as e:
            logger.warning(f"LLM validation failed: {e}")
            return self._rule_based_validate(image_path, task)

    def _check_alignment_score(self, image_path: str, prompt: str) -> float:
        """Check how well image aligns with prompt."""
        try:
            response = self._llm_client.query_with_image(
                prompt=PROMPT_ALIGNMENT_PROMPT.format(prompt=prompt),
                image_path=image_path,
                provider=LLMProvider.OPENAI,
            )

            data = self._parse_json_response(response.content)
            scores = data.get("scores", {})
            return scores.get("alignment", 80) / 100

        except Exception:
            return 0.8  # Default

    def _rule_based_validate(
        self,
        image_path: str,
        task: str,
    ) -> QualityScore:
        """Rule-based quality assessment without LLM."""
        try:
            from PIL import Image
            img = Image.open(image_path)

            issues = []
            suggestions = []
            details = {}

            # Check dimensions
            width, height = img.size
            if width < 256 or height < 256:
                issues.append("Image resolution is very low")
                suggestions.append("Consider upscaling the image")
                details["resolution"] = 0.3
            elif width < 512 or height < 512:
                details["resolution"] = 0.6
            else:
                details["resolution"] = 0.9

            # Check mode
            if img.mode == "RGBA":
                details["transparency"] = 0.9
            elif img.mode == "RGB":
                details["transparency"] = 0.7
            else:
                details["transparency"] = 0.5
                issues.append(f"Unusual color mode: {img.mode}")

            # Check file size as proxy for quality
            file_size = Path(image_path).stat().st_size
            if file_size < 10000:  # < 10KB
                details["compression"] = 0.5
                issues.append("File size suggests heavy compression")
            else:
                details["compression"] = 0.8

            # Calculate overall
            overall = sum(details.values()) / len(details) if details else 0.5
            level = self._score_to_level(overall)

            return QualityScore(
                overall=overall,
                details=details,
                issues=issues,
                suggestions=suggestions,
                level=level,
            )

        except Exception as e:
            logger.error(f"Rule-based validation failed: {e}")
            return self._create_mock_score(0.5, [f"Validation error: {str(e)}"])

    def _score_to_level(self, score: float) -> QualityLevel:
        """Convert numeric score to quality level."""
        if score >= 0.9:
            return QualityLevel.EXCELLENT
        elif score >= 0.75:
            return QualityLevel.GOOD
        elif score >= 0.5:
            return QualityLevel.ACCEPTABLE
        elif score >= 0.3:
            return QualityLevel.POOR
        else:
            return QualityLevel.UNACCEPTABLE

    def _create_mock_score(
        self,
        score: float,
        issues: List[str],
    ) -> QualityScore:
        """Create a mock score for testing."""
        return QualityScore(
            overall=score,
            details={"mock": score},
            issues=issues,
            suggestions=[],
            level=self._score_to_level(score),
        )

    def _parse_json_response(self, content: str) -> Dict[str, Any]:
        """Parse JSON from LLM response."""
        try:
            # Try direct parse
            return json.loads(content)
        except json.JSONDecodeError:
            pass

        # Extract JSON from response
        import re
        match = re.search(r'\{.*\}', content, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except json.JSONDecodeError:
                pass

        return {}

    def detect_artifacts(self, image_path: str) -> List[Dict[str, Any]]:
        """
        Detect artifacts in an image.

        Args:
            image_path: Path to image

        Returns:
            List of detected artifacts
        """
        if not Path(image_path).exists():
            return []

        if self.use_llm and self._llm_client:
            return self._llm_detect_artifacts(image_path)
        else:
            return self._rule_based_detect_artifacts(image_path)

    def _llm_detect_artifacts(self, image_path: str) -> List[Dict[str, Any]]:
        """Use LLM to detect artifacts."""
        try:
            prompt = """Analyze this image for artifacts and quality issues.

List any artifacts found with:
- Type (blur, noise, distortion, banding, aliasing, halo, etc.)
- Location (center, edges, specific area)
- Severity (low, medium, high)

Respond in JSON format:
{
  "artifacts": [
    {"type": "blur", "location": "corners", "severity": "low"}
  ]
}"""

            response = self._llm_client.query_with_image(
                prompt=prompt,
                image_path=image_path,
                provider=LLMProvider.OPENAI,
            )

            data = self._parse_json_response(response.content)
            return data.get("artifacts", [])

        except Exception as e:
            logger.warning(f"LLM artifact detection failed: {e}")
            return []

    def _rule_based_detect_artifacts(self, image_path: str) -> List[Dict[str, Any]]:
        """Rule-based artifact detection."""
        artifacts = []

        try:
            from PIL import Image
            import numpy as np

            img = Image.open(image_path)
            arr = np.array(img)

            # Check for excessive noise (high variance in small patches)
            if len(arr.shape) >= 2:
                patch_var = np.var(arr[:32, :32])
                if patch_var > 2000:
                    artifacts.append({
                        "type": "noise",
                        "location": "overall",
                        "severity": "medium",
                    })

            # Check for banding (limited color range)
            unique_colors = len(np.unique(arr.flatten()))
            if unique_colors < 1000 and img.mode in ["RGB", "RGBA"]:
                artifacts.append({
                    "type": "color_banding",
                    "location": "gradients",
                    "severity": "low",
                })

        except Exception as e:
            logger.debug(f"Artifact detection error: {e}")

        return artifacts

    def validate_layers(
        self,
        layer_paths: List[str],
        expected_count: Optional[int] = None,
    ) -> LayerValidation:
        """
        Validate layer decomposition results.

        Args:
            layer_paths: Paths to layer images
            expected_count: Expected number of layers

        Returns:
            LayerValidation result
        """
        issues = []
        recommendations = []
        quality_scores = []

        # Check layer count
        actual_count = len(layer_paths)
        count_valid = True

        if expected_count is not None and actual_count != expected_count:
            issues.append(f"Expected {expected_count} layers, got {actual_count}")
            count_valid = False

        # Validate each layer
        for i, path in enumerate(layer_paths):
            if not Path(path).exists():
                issues.append(f"Layer {i + 1} file not found")
                quality_scores.append(0.0)
                continue

            score = self.validate(path, task="decompose")
            quality_scores.append(score.overall)

            if score.overall < 0.5:
                issues.append(f"Layer {i + 1} has quality issues")
                recommendations.append(f"Review layer {i + 1}: {', '.join(score.issues)}")

        # Calculate overall quality
        overall_quality = sum(quality_scores) / len(quality_scores) if quality_scores else 0.0

        is_valid = count_valid and all(s >= 0.5 for s in quality_scores)

        return LayerValidation(
            is_valid=is_valid,
            layer_count=actual_count,
            expected_count=expected_count,
            quality_scores=quality_scores,
            issues=issues,
            recommendations=recommendations,
            overall_quality=overall_quality,
        )

    def rate_generation(
        self,
        image_path: str,
        prompt: str,
        reference_path: Optional[str] = None,
    ) -> QualityScore:
        """
        Rate a generated image against its prompt.

        Args:
            image_path: Path to generated image
            prompt: Original generation prompt
            reference_path: Optional reference image

        Returns:
            QualityScore with generation-specific assessment
        """
        return self.validate(image_path, task="generation", prompt=prompt)


# Singleton instance
_validator: Optional[QualityValidator] = None


def _get_validator() -> QualityValidator:
    """Get or create validator instance."""
    global _validator
    if _validator is None:
        _validator = QualityValidator()
    return _validator


# Convenience functions
def validate_output(
    image_path: str,
    task: str = "generation",
    **kwargs
) -> QualityScore:
    """
    Validate an output image.

    Args:
        image_path: Path to image
        task: Task type
        **kwargs: Additional options

    Returns:
        QualityScore
    """
    return _get_validator().validate(image_path, task=task, **kwargs)


def rate_generation(
    image_path: str,
    prompt: str,
    **kwargs
) -> QualityScore:
    """
    Rate a generated image.

    Args:
        image_path: Path to image
        prompt: Original prompt
        **kwargs: Additional options

    Returns:
        QualityScore
    """
    return _get_validator().rate_generation(image_path, prompt, **kwargs)


def detect_artifacts(image_path: str) -> List[Dict[str, Any]]:
    """
    Detect artifacts in an image.

    Args:
        image_path: Path to image

    Returns:
        List of artifacts
    """
    return _get_validator().detect_artifacts(image_path)
