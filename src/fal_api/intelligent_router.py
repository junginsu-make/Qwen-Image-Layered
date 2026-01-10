"""
Intelligent Task Router for Natural Language Processing.

Uses LLMs to:
- Parse user intent from natural language
- Decompose complex tasks into steps
- Select appropriate skills
- Generate execution plans

Supports Korean and English natural language input.
"""

import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Any, Tuple

try:
    from .logging_config import get_logger
    from .llm_client import LLMClient, LLMProvider, query_llm
    from .model_selector import ModelSelector, select_model
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

    _spec = _util.spec_from_file_location(
        "model_selector",
        _Path(__file__).parent / "model_selector.py"
    )
    _model_selector = _util.module_from_spec(_spec)
    _spec.loader.exec_module(_model_selector)
    ModelSelector = _model_selector.ModelSelector
    select_model = _model_selector.select_model

logger = get_logger("intelligent_router")


class Intent(Enum):
    """User intent categories."""
    GENERATE = "generate"
    EDIT = "edit"
    DECOMPOSE = "decompose"
    REMOVE_BACKGROUND = "remove_background"
    EXTRACT_TEXT = "extract_text"
    TRANSLATE = "translate"
    UPSCALE = "upscale"
    STYLE_TRANSFER = "style_transfer"
    EXTRACT_COLORS = "extract_colors"
    ADD_TEXT = "add_text"
    REMOVE_TEXT = "remove_text"
    REPLACE_TEXT = "replace_text"
    EXPORT = "export"
    ANALYZE = "analyze"
    BATCH_PROCESS = "batch_process"
    UNKNOWN = "unknown"


@dataclass
class ExecutionStep:
    """A single step in an execution plan."""
    order: int
    skill: str
    intent: Intent
    parameters: Dict[str, Any] = field(default_factory=dict)
    depends_on: List[int] = field(default_factory=list)
    estimated_cost: float = 0.0
    estimated_time: float = 5.0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "order": self.order,
            "skill": self.skill,
            "intent": self.intent.value,
            "parameters": self.parameters,
            "depends_on": self.depends_on,
            "estimated_cost": self.estimated_cost,
            "estimated_time": self.estimated_time,
        }


@dataclass
class RoutingResult:
    """Result of routing a request."""
    intents: List[Intent]
    skills: List[str]
    execution_plan: List[ExecutionStep]
    estimated_cost: float
    estimated_time: float
    confidence: float
    model_recommendation: Optional[Dict[str, Any]] = None
    warnings: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "intents": [i.value for i in self.intents],
            "skills": self.skills,
            "execution_plan": [s.to_dict() for s in self.execution_plan],
            "estimated_cost": self.estimated_cost,
            "estimated_time": self.estimated_time,
            "confidence": self.confidence,
            "model_recommendation": self.model_recommendation,
            "warnings": self.warnings,
        }


# Intent detection patterns (Korean + English)
INTENT_PATTERNS = {
    Intent.GENERATE: [
        r"생성|만들어|그려|create|generate|make|draw",
        r"이미지.*생성|새.*이미지|new image",
    ],
    Intent.EDIT: [
        r"편집|수정|변경|바꿔|edit|modify|change|alter",
        r"고쳐|fix|adjust",
    ],
    Intent.DECOMPOSE: [
        r"분해|분리|레이어|decompose|separate|layer|split",
        r"추출|extract layers",
    ],
    Intent.REMOVE_BACKGROUND: [
        r"배경.*제거|배경.*삭제|누끼|remove background|background removal",
        r"투명.*배경|transparent background",
    ],
    Intent.EXTRACT_TEXT: [
        r"텍스트.*추출|글자.*추출|ocr|extract text|read text",
        r"문자.*인식|text recognition",
    ],
    Intent.TRANSLATE: [
        r"번역|translate|변환.*언어",
    ],
    Intent.UPSCALE: [
        r"업스케일|확대|해상도.*높|upscale|enlarge|enhance resolution",
        r"고해상도|high resolution|hd|4k",
    ],
    Intent.STYLE_TRANSFER: [
        r"스타일|화풍|style|artistic|watercolor|oil paint",
        r"수채화|유화|anime|cartoon",
    ],
    Intent.EXTRACT_COLORS: [
        r"색상.*추출|팔레트|color|palette|색깔",
        r"컬러.*분석|color analysis",
    ],
    Intent.ADD_TEXT: [
        r"텍스트.*추가|글자.*추가|워터마크|add text|watermark|overlay",
        r"문구.*삽입|insert text",
    ],
    Intent.REMOVE_TEXT: [
        r"텍스트.*제거|글자.*제거|글씨.*삭제|remove text|erase text",
        r"문자.*지우",
    ],
    Intent.REPLACE_TEXT: [
        r"텍스트.*교체|글자.*바꿔|replace text|change text",
        r"문구.*변경",
    ],
    Intent.EXPORT: [
        r"내보내기|저장|export|save|download",
        r"pptx|psd|zip|파일.*저장",
    ],
    Intent.ANALYZE: [
        r"분석|설명|describe|analyze|what is",
        r"뭐야|무엇|어떤",
    ],
    Intent.BATCH_PROCESS: [
        r"일괄|배치|여러|batch|multiple|all|bulk",
        r"대량|모든.*이미지",
    ],
}

# Skill mapping for each intent
INTENT_TO_SKILL = {
    Intent.GENERATE: "nano-banana-generate",
    Intent.EDIT: "nano-banana-edit",
    Intent.DECOMPOSE: "image-decompose",
    Intent.REMOVE_BACKGROUND: "background-remove",
    Intent.EXTRACT_TEXT: "text-extract",
    Intent.TRANSLATE: "text-translate",
    Intent.UPSCALE: "smart-upscale",
    Intent.STYLE_TRANSFER: "style-transfer",
    Intent.EXTRACT_COLORS: "color-palette",
    Intent.ADD_TEXT: "text-overlay",
    Intent.REMOVE_TEXT: "text-remove",
    Intent.REPLACE_TEXT: "text-replace",
    Intent.EXPORT: "layer-export",
    Intent.ANALYZE: "image-decompose",  # Analysis through decomposition
    Intent.BATCH_PROCESS: None,  # Meta-intent, not a direct skill
}

# Estimated costs per skill
SKILL_COSTS = {
    "nano-banana-generate": 0.039,
    "nano-banana-pro-generate": 0.15,
    "nano-banana-edit": 0.039,
    "nano-banana-pro-edit": 0.15,
    "image-decompose": 0.05,
    "background-remove": 0.03,
    "text-extract": 0.01,
    "text-translate": 0.005,
    "smart-upscale": 0.02,
    "style-transfer": 0.03,
    "color-palette": 0.01,
    "text-overlay": 0.01,
    "text-remove": 0.02,
    "text-replace": 0.03,
    "layer-export": 0.0,  # Free (local operation)
}

# System prompt for LLM routing
ROUTING_SYSTEM_PROMPT = """You are an intelligent task router for an image processing system.
Your job is to understand user requests and identify the required operations.

Available operations:
- generate: Create new images from text
- edit: Modify existing images
- decompose: Split image into layers
- remove_background: Remove image background
- extract_text: OCR - extract text from images
- translate: Translate text
- upscale: Increase image resolution
- style_transfer: Apply artistic styles
- extract_colors: Get color palette
- add_text: Add text overlay
- remove_text: Erase text from images
- replace_text: Replace text in images
- export: Save/export results

Analyze the user request and return a JSON object with:
{
  "intents": ["intent1", "intent2"],
  "order": ["intent1", "intent2"],
  "confidence": 0.95
}

Consider Korean and English inputs.
Return ONLY the JSON, no explanations."""


class TaskRouter:
    """
    Intelligent task router for natural language requests.

    Usage:
        router = TaskRouter()

        # Route a request
        result = router.route_request("Remove background and change colors")
        print(f"Skills needed: {result['skills']}")
        print(f"Estimated cost: ${result['estimated_cost']}")

        # Parse intent only
        intents = router.parse_intent("Generate a beautiful sunset")
        print(f"Detected intents: {intents}")
    """

    def __init__(self, use_llm: bool = True):
        """
        Initialize the router.

        Args:
            use_llm: Whether to use LLM for complex parsing
        """
        self.use_llm = use_llm
        self._llm_client = LLMClient() if use_llm else None
        self._model_selector = ModelSelector()

    def parse_intent(self, request: str) -> List[Intent]:
        """
        Parse intents from a request.

        Args:
            request: User request string

        Returns:
            List of detected intents
        """
        request_lower = request.lower()
        detected = []

        # Check each intent pattern
        for intent, patterns in INTENT_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, request_lower):
                    if intent not in detected:
                        detected.append(intent)
                    break

        # If nothing detected, try LLM
        if not detected and self.use_llm and self._llm_client:
            detected = self._llm_parse_intent(request)

        # Default to unknown if still nothing
        if not detected:
            detected = [Intent.UNKNOWN]

        return detected

    def _llm_parse_intent(self, request: str) -> List[Intent]:
        """Use LLM to parse intent."""
        try:
            response = self._llm_client.query(
                prompt=f"Parse this image processing request: '{request}'",
                system=ROUTING_SYSTEM_PROMPT,
                provider=LLMProvider.GEMINI,
            )

            # Parse JSON response
            import json
            content = response.content.strip()

            # Extract JSON
            if "{" in content:
                start = content.index("{")
                end = content.rindex("}") + 1
                json_str = content[start:end]
                data = json.loads(json_str)

                intents = []
                for intent_str in data.get("intents", []):
                    try:
                        intents.append(Intent(intent_str))
                    except ValueError:
                        pass

                return intents if intents else [Intent.UNKNOWN]

        except Exception as e:
            logger.warning(f"LLM intent parsing failed: {e}")

        return [Intent.UNKNOWN]

    def route_request(
        self,
        request: str,
        budget: Optional[float] = None,
        prefer_quality: bool = False,
    ) -> Dict[str, Any]:
        """
        Route a request to appropriate skills.

        Args:
            request: User request
            budget: Optional budget constraint
            prefer_quality: Prefer high-quality models

        Returns:
            Routing result dictionary
        """
        # Parse intents
        intents = self.parse_intent(request)

        # Map intents to skills
        skills = []
        for intent in intents:
            skill = INTENT_TO_SKILL.get(intent)
            if skill and skill not in skills:
                skills.append(skill)

        # Generate execution plan
        execution_plan = self._generate_execution_plan(intents, skills, request)

        # Calculate totals
        total_cost = sum(step.estimated_cost for step in execution_plan)
        total_time = sum(step.estimated_time for step in execution_plan)

        # Get model recommendation for primary task
        model_rec = None
        if intents and intents[0] in [Intent.GENERATE, Intent.EDIT]:
            model_rec = self._model_selector.select_model(
                task=request,
                budget=budget,
                prefer_quality=prefer_quality,
            )

        # Check warnings
        warnings = []
        if budget is not None and total_cost > budget:
            warnings.append(f"Estimated cost ${total_cost:.3f} exceeds budget ${budget:.2f}")

        if len(intents) > 3:
            warnings.append("Complex request - consider breaking into smaller tasks")

        # Calculate confidence
        confidence = 0.9 if intents[0] != Intent.UNKNOWN else 0.5
        confidence -= 0.1 * max(0, len(intents) - 2)  # Reduce for complex requests

        result = RoutingResult(
            intents=intents,
            skills=skills,
            execution_plan=execution_plan,
            estimated_cost=total_cost,
            estimated_time=total_time,
            confidence=confidence,
            model_recommendation=model_rec,
            warnings=warnings,
        )

        logger.info(f"Routed request: {request[:50]}... → {len(skills)} skills")
        return result.to_dict()

    def _generate_execution_plan(
        self,
        intents: List[Intent],
        skills: List[str],
        request: str,
    ) -> List[ExecutionStep]:
        """Generate ordered execution plan."""
        plan = []

        for i, (intent, skill) in enumerate(zip(intents, skills)):
            if not skill:
                continue

            # Determine dependencies
            depends_on = [i - 1] if i > 0 else []

            # Get cost estimate
            cost = SKILL_COSTS.get(skill, 0.02)

            # Estimate time based on operation type
            if "generate" in skill or "edit" in skill:
                time = 10.0
            elif "decompose" in skill:
                time = 15.0
            elif "upscale" in skill:
                time = 8.0
            else:
                time = 3.0

            step = ExecutionStep(
                order=i + 1,
                skill=skill,
                intent=intent,
                parameters=self._extract_parameters(request, intent),
                depends_on=depends_on,
                estimated_cost=cost,
                estimated_time=time,
            )
            plan.append(step)

        return plan

    def _extract_parameters(self, request: str, intent: Intent) -> Dict[str, Any]:
        """Extract relevant parameters from request."""
        params = {}

        # Extract numbers (for layer count, resolution, etc.)
        numbers = re.findall(r'\d+', request)
        if numbers:
            if intent == Intent.DECOMPOSE:
                params["layer_count"] = min(int(numbers[0]), 10)
            elif intent == Intent.UPSCALE:
                scale = int(numbers[0])
                params["scale"] = min(scale, 4) if scale <= 4 else 2

        # Extract quality preferences
        if any(kw in request.lower() for kw in ["high quality", "고품질", "4k", "pro"]):
            params["quality"] = "high"
        elif any(kw in request.lower() for kw in ["fast", "quick", "빠르게", "preview"]):
            params["quality"] = "fast"

        # Extract style for style transfer
        if intent == Intent.STYLE_TRANSFER:
            styles = ["watercolor", "oil", "anime", "cartoon", "sketch", "수채화", "유화"]
            for style in styles:
                if style in request.lower():
                    params["style"] = style
                    break

        # Extract format for export
        if intent == Intent.EXPORT:
            formats = ["pptx", "psd", "zip", "png"]
            for fmt in formats:
                if fmt in request.lower():
                    params["format"] = fmt
                    break

        return params

    def get_execution_plan(self, request: str) -> List[Dict[str, Any]]:
        """
        Get just the execution plan for a request.

        Args:
            request: User request

        Returns:
            List of execution steps
        """
        result = self.route_request(request)
        return result["execution_plan"]

    def explain_routing(self, request: str) -> str:
        """
        Get human-readable explanation of routing.

        Args:
            request: User request

        Returns:
            Explanation string
        """
        result = self.route_request(request)

        lines = [
            f"Request: {request}",
            f"",
            f"Detected intents: {', '.join(result['intents'])}",
            f"Required skills: {', '.join(result['skills'])}",
            f"",
            f"Execution plan:",
        ]

        for step in result["execution_plan"]:
            lines.append(f"  {step['order']}. {step['skill']} (${step['estimated_cost']:.3f})")

        lines.extend([
            f"",
            f"Total estimated cost: ${result['estimated_cost']:.3f}",
            f"Total estimated time: {result['estimated_time']:.1f}s",
            f"Confidence: {result['confidence']:.0%}",
        ])

        if result["warnings"]:
            lines.append(f"")
            lines.append("Warnings:")
            for warning in result["warnings"]:
                lines.append(f"  ⚠ {warning}")

        return "\n".join(lines)


# Singleton instance
_router: Optional[TaskRouter] = None


def _get_router() -> TaskRouter:
    """Get or create router instance."""
    global _router
    if _router is None:
        _router = TaskRouter()
    return _router


# Convenience functions
def route_request(request: str, **kwargs) -> Dict[str, Any]:
    """
    Route a request to appropriate skills.

    Args:
        request: User request
        **kwargs: Additional options

    Returns:
        Routing result
    """
    return _get_router().route_request(request, **kwargs)


def parse_intent(request: str) -> List[Intent]:
    """
    Parse intents from a request.

    Args:
        request: User request

    Returns:
        List of intents
    """
    return _get_router().parse_intent(request)


def get_execution_plan(request: str) -> List[Dict[str, Any]]:
    """
    Get execution plan for a request.

    Args:
        request: User request

    Returns:
        List of execution steps
    """
    return _get_router().get_execution_plan(request)
