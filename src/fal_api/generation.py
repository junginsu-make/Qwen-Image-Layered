"""
Generation Module - Text-to-Image and Image Editing with Fal AI

This module provides unified interfaces for image generation and editing
using various Fal AI models, including Nano Banana and Nano Banana Pro.

Usage:
    from src.fal_api.generation import generate_image, edit_image

    # Generate an image
    result = generate_image(
        prompt="a beautiful sunset",
        model="nano-banana-pro"
    )

    # Edit an image
    result = edit_image(
        image_path="photo.png",
        prompt="change the sky to purple",
        model="nano-banana-edit"
    )
"""

import os
import time
import base64
from pathlib import Path
from typing import Optional, Dict, Any, List, Union
from datetime import datetime

# Optional imports with graceful fallback
try:
    import fal_client
    FAL_AVAILABLE = True
except ImportError:
    FAL_AVAILABLE = False

try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

# Import model_registry with fallback for direct loading
try:
    from .model_registry import ModelRegistry, get_model, ModelType, select_best_model
except ImportError:
    # Direct import when module is loaded standalone
    import sys as _sys
    if 'src.fal_api.model_registry' in _sys.modules:
        _model_registry = _sys.modules['src.fal_api.model_registry']
        ModelRegistry = _model_registry.ModelRegistry
        get_model = _model_registry.get_model
        ModelType = _model_registry.ModelType
        select_best_model = _model_registry.select_best_model
    else:
        # Fallback: load from same directory
        from pathlib import Path as _Path
        import importlib.util as _importlib_util
        _mr_path = _Path(__file__).parent / "model_registry.py"
        _spec = _importlib_util.spec_from_file_location("model_registry", _mr_path)
        _model_registry = _importlib_util.module_from_spec(_spec)
        _spec.loader.exec_module(_model_registry)
        ModelRegistry = _model_registry.ModelRegistry
        get_model = _model_registry.get_model
        ModelType = _model_registry.ModelType
        select_best_model = _model_registry.select_best_model


# =============================================================================
# Configuration
# =============================================================================

DEFAULT_OUTPUT_DIR = "./output/generated"
DEFAULT_MODEL_GENERATE = "nano-banana"
DEFAULT_MODEL_EDIT = "nano-banana-edit"


# =============================================================================
# Helper Functions
# =============================================================================

def _ensure_output_dir(output_dir: str) -> Path:
    """Ensure output directory exists."""
    path = Path(output_dir)
    path.mkdir(parents=True, exist_ok=True)
    return path


def _generate_output_filename(prefix: str = "generated", ext: str = "png") -> str:
    """Generate unique output filename with timestamp."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{prefix}_{timestamp}.{ext}"


def _image_to_data_url(image_path: str) -> str:
    """Convert image file to data URL for API."""
    path = Path(image_path)
    if not path.exists():
        raise FileNotFoundError(f"Image not found: {image_path}")

    with open(path, "rb") as f:
        data = base64.b64encode(f.read()).decode("utf-8")

    # Determine MIME type
    ext = path.suffix.lower()
    mime_types = {
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".webp": "image/webp",
        ".gif": "image/gif"
    }
    mime = mime_types.get(ext, "image/png")

    return f"data:{mime};base64,{data}"


def _upload_image(image_path: str) -> str:
    """Upload image to Fal storage and return URL."""
    if not FAL_AVAILABLE:
        raise RuntimeError("fal_client not available. Install with: pip install fal-client")

    path = Path(image_path)
    if not path.exists():
        raise FileNotFoundError(f"Image not found: {image_path}")

    # Upload to Fal storage
    url = fal_client.upload_file(str(path))
    return url


def _download_image(url: str, output_path: str) -> str:
    """Download image from URL and save to path."""
    import urllib.request

    urllib.request.urlretrieve(url, output_path)
    return output_path


def _validate_api_key() -> bool:
    """Check if FAL_KEY is configured."""
    return bool(os.environ.get("FAL_KEY"))


# =============================================================================
# Main Generation Functions
# =============================================================================

def generate_image(
    prompt: str,
    model: str = DEFAULT_MODEL_GENERATE,
    aspect_ratio: str = "1:1",
    resolution: str = "2k",
    num_images: int = 1,
    output_dir: str = DEFAULT_OUTPUT_DIR,
    output_filename: Optional[str] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Generate image(s) from text prompt using specified model.

    Args:
        prompt: Text description of the image to generate
        model: Model to use (nano-banana, nano-banana-pro, flux-dev, etc.)
        aspect_ratio: Image aspect ratio (1:1, 16:9, 9:16, 4:3, 3:4)
        resolution: Output resolution for pro models (2k, 4k)
        num_images: Number of images to generate (1-4)
        output_dir: Directory to save generated images
        output_filename: Custom output filename (auto-generated if not provided)
        **kwargs: Additional model-specific parameters

    Returns:
        Dictionary with generation results:
        {
            "success": bool,
            "generated_images": List[str],  # paths to generated images
            "model_used": str,
            "generation_time": float,
            "cost": float,
            "prompt_used": str
        }
    """
    start_time = time.time()

    # Validate inputs
    if not prompt or not prompt.strip():
        return {
            "success": False,
            "error": "Prompt cannot be empty",
            "generated_images": []
        }

    # Check API availability
    if not FAL_AVAILABLE:
        return {
            "success": False,
            "error": "fal_client not installed. Run: pip install fal-client",
            "generated_images": [],
            "mock_mode": True
        }

    if not _validate_api_key():
        return {
            "success": False,
            "error": "FAL_KEY not configured. Set FAL_KEY environment variable.",
            "generated_images": []
        }

    # Get model info
    model_info = get_model(model)
    if not model_info:
        # Fallback to default
        model_info = get_model(DEFAULT_MODEL_GENERATE)
        model = DEFAULT_MODEL_GENERATE

    # Ensure output directory
    output_path = _ensure_output_dir(output_dir)

    # Clamp num_images
    num_images = max(1, min(4, num_images))

    # Build API parameters
    api_params = {
        "prompt": prompt,
        "num_images": num_images
    }

    # Add model-specific parameters
    if "nano-banana" in model:
        api_params["aspect_ratio"] = aspect_ratio
        if "pro" in model:
            api_params["output_resolution"] = resolution

    # Add any extra parameters
    api_params.update(kwargs)

    try:
        # Call Fal AI API
        result = fal_client.subscribe(
            model_info.endpoint,
            arguments=api_params,
            with_logs=False
        )

        # Process results
        generated_images = []
        images = result.get("images", [])

        for i, img_data in enumerate(images):
            img_url = img_data.get("url", "")
            if img_url:
                if output_filename and len(images) == 1:
                    filename = output_filename
                else:
                    filename = _generate_output_filename(f"gen_{model}_{i+1}")

                save_path = str(output_path / filename)
                _download_image(img_url, save_path)
                generated_images.append(save_path)

        generation_time = time.time() - start_time
        cost = model_info.price_per_image * num_images
        if resolution == "4k" and model_info.supports_4k:
            cost *= 2  # 4K doubles the price

        return {
            "success": True,
            "generated_images": generated_images,
            "model_used": model,
            "endpoint": model_info.endpoint,
            "generation_time": round(generation_time, 2),
            "cost": round(cost, 4),
            "prompt_used": prompt,
            "aspect_ratio": aspect_ratio,
            "resolution": resolution if "pro" in model else "standard",
            "num_requested": num_images,
            "num_generated": len(generated_images)
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "generated_images": [],
            "model_used": model,
            "generation_time": round(time.time() - start_time, 2)
        }


def edit_image(
    image_path: str,
    prompt: str,
    model: str = DEFAULT_MODEL_EDIT,
    resolution: str = "2k",
    output_path: Optional[str] = None,
    output_dir: str = DEFAULT_OUTPUT_DIR,
    **kwargs
) -> Dict[str, Any]:
    """
    Edit an existing image using natural language prompt.

    Args:
        image_path: Path to the input image
        prompt: Description of the desired edit
        model: Model to use (nano-banana-edit, nano-banana-pro-edit)
        resolution: Output resolution for pro models (2k, 4k)
        output_path: Custom output path (auto-generated if not provided)
        output_dir: Directory for auto-generated output
        **kwargs: Additional model-specific parameters

    Returns:
        Dictionary with edit results:
        {
            "success": bool,
            "edited_image": str,  # path to edited image
            "model_used": str,
            "edit_time": float,
            "cost": float
        }
    """
    start_time = time.time()

    # Validate inputs
    if not prompt or not prompt.strip():
        return {
            "success": False,
            "error": "Edit prompt cannot be empty"
        }

    if not Path(image_path).exists():
        return {
            "success": False,
            "error": f"Input image not found: {image_path}"
        }

    # Check API availability
    if not FAL_AVAILABLE:
        return {
            "success": False,
            "error": "fal_client not installed",
            "mock_mode": True
        }

    if not _validate_api_key():
        return {
            "success": False,
            "error": "FAL_KEY not configured"
        }

    # Get model info
    model_info = get_model(model)
    if not model_info:
        # Fallback mapping
        if "pro" in model.lower():
            model = "nano-banana-pro-edit"
        else:
            model = "nano-banana-edit"
        model_info = get_model(model)

    # Upload image
    try:
        image_url = _upload_image(image_path)
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to upload image: {e}"
        }

    # Build API parameters
    api_params = {
        "image_url": image_url,
        "prompt": prompt
    }

    # Add resolution for pro models
    if "pro" in model and model_info:
        api_params["output_resolution"] = resolution

    api_params.update(kwargs)

    try:
        # Call Fal AI API
        result = fal_client.subscribe(
            model_info.endpoint,
            arguments=api_params,
            with_logs=False
        )

        # Get result image
        images = result.get("images", [])
        if not images:
            return {
                "success": False,
                "error": "No image returned from API"
            }

        img_url = images[0].get("url", "")
        if not img_url:
            return {
                "success": False,
                "error": "Invalid image URL in response"
            }

        # Determine output path
        if not output_path:
            output_base = _ensure_output_dir(output_dir)
            output_path = str(output_base / _generate_output_filename(f"edit_{model}"))

        # Download result
        _download_image(img_url, output_path)

        edit_time = time.time() - start_time
        cost = model_info.price_per_image
        if resolution == "4k" and model_info.supports_4k:
            cost *= 2

        return {
            "success": True,
            "edited_image": output_path,
            "original_image": image_path,
            "model_used": model,
            "endpoint": model_info.endpoint,
            "edit_time": round(edit_time, 2),
            "cost": round(cost, 4),
            "prompt_used": prompt,
            "resolution": resolution if "pro" in model else "standard"
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "edit_time": round(time.time() - start_time, 2)
        }


# =============================================================================
# Batch Operations
# =============================================================================

def batch_generate(
    prompts: List[str],
    model: str = DEFAULT_MODEL_GENERATE,
    output_dir: str = DEFAULT_OUTPUT_DIR,
    **kwargs
) -> Dict[str, Any]:
    """
    Generate multiple images from a list of prompts.

    Args:
        prompts: List of text prompts
        model: Model to use
        output_dir: Output directory
        **kwargs: Additional parameters

    Returns:
        Dictionary with batch results
    """
    results = []
    total_cost = 0.0
    total_time = 0.0

    for i, prompt in enumerate(prompts):
        result = generate_image(
            prompt=prompt,
            model=model,
            output_dir=output_dir,
            **kwargs
        )
        results.append(result)

        if result.get("success"):
            total_cost += result.get("cost", 0)
            total_time += result.get("generation_time", 0)

    successful = sum(1 for r in results if r.get("success"))

    return {
        "success": successful == len(prompts),
        "total_prompts": len(prompts),
        "successful": successful,
        "failed": len(prompts) - successful,
        "total_cost": round(total_cost, 4),
        "total_time": round(total_time, 2),
        "results": results
    }


def batch_edit(
    edits: List[Dict[str, str]],
    model: str = DEFAULT_MODEL_EDIT,
    output_dir: str = DEFAULT_OUTPUT_DIR,
    **kwargs
) -> Dict[str, Any]:
    """
    Apply edits to multiple images.

    Args:
        edits: List of dicts with 'image_path' and 'prompt' keys
        model: Model to use
        output_dir: Output directory
        **kwargs: Additional parameters

    Returns:
        Dictionary with batch results
    """
    results = []
    total_cost = 0.0
    total_time = 0.0

    for edit_info in edits:
        result = edit_image(
            image_path=edit_info.get("image_path", ""),
            prompt=edit_info.get("prompt", ""),
            model=model,
            output_dir=output_dir,
            **kwargs
        )
        results.append(result)

        if result.get("success"):
            total_cost += result.get("cost", 0)
            total_time += result.get("edit_time", 0)

    successful = sum(1 for r in results if r.get("success"))

    return {
        "success": successful == len(edits),
        "total_edits": len(edits),
        "successful": successful,
        "failed": len(edits) - successful,
        "total_cost": round(total_cost, 4),
        "total_time": round(total_time, 2),
        "results": results
    }


# =============================================================================
# Model Selection Helpers
# =============================================================================

def get_available_models(task: str = "generate") -> List[Dict[str, Any]]:
    """
    Get list of available models for a task.

    Args:
        task: "generate" or "edit"

    Returns:
        List of model info dictionaries
    """
    if task == "edit":
        model_type = ModelType.IMAGE_EDIT
    else:
        model_type = ModelType.TEXT_TO_IMAGE

    models = ModelRegistry.list_models(model_type=model_type)
    return [m.to_dict() for m in models]


def recommend_model(
    task: str,
    prefer_quality: bool = False,
    prefer_speed: bool = False,
    max_budget: Optional[float] = None
) -> Dict[str, Any]:
    """
    Get a model recommendation based on requirements.

    Args:
        task: Description of the task
        prefer_quality: Prioritize quality over cost
        prefer_speed: Prioritize speed over quality
        max_budget: Maximum price per image

    Returns:
        Recommended model info
    """
    model = select_best_model(
        task=task,
        prefer_quality=prefer_quality,
        prefer_speed=prefer_speed,
        max_price=max_budget
    )

    if model:
        return {
            "recommended": True,
            "model": model.to_dict()
        }
    else:
        return {
            "recommended": False,
            "fallback": "nano-banana",
            "reason": "No model matched criteria"
        }


# =============================================================================
# Quick Functions
# =============================================================================

def quick_generate(prompt: str) -> Dict[str, Any]:
    """Quick generation with defaults (fast model)."""
    return generate_image(prompt=prompt, model="nano-banana")


def pro_generate(prompt: str, resolution: str = "2k") -> Dict[str, Any]:
    """High-quality generation with Nano Banana Pro."""
    return generate_image(prompt=prompt, model="nano-banana-pro", resolution=resolution)


def quick_edit(image_path: str, prompt: str) -> Dict[str, Any]:
    """Quick edit with defaults (fast model)."""
    return edit_image(image_path=image_path, prompt=prompt, model="nano-banana-edit")


def pro_edit(image_path: str, prompt: str, resolution: str = "2k") -> Dict[str, Any]:
    """High-quality edit with Nano Banana Pro."""
    return edit_image(image_path=image_path, prompt=prompt, model="nano-banana-pro-edit", resolution=resolution)
