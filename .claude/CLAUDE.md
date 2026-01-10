# Qwen Image Layered - Project Context

## Overview

AI-powered image layer decomposition system using Fal AI cloud API.
Decomposes images into multiple RGBA layers for editing without local GPU.

## Tech Stack

- Python 3.10+
- Fal AI API (qwen-image-layered, nano-banana, nano-banana-pro)
- Pillow for image processing
- python-pptx, psd-tools for export
- Gradio for test interface

## Quick Start

```bash
# Install
pip install -r requirements-fal.txt

# Configure
cp .env.example .env
# Edit .env and add FAL_KEY

# Run test UI
python src/fal_api/app_test.py

# Run CLI
python src/fal_api/run_demo.py --image photo.png --layers 4
```

## Project Structure

```
Qwen-Image-Layered/
├── AGENTS.md              # Project rules (root)
├── src/
│   ├── AGENTS.md          # Source code rules
│   ├── app.py             # Local GPU version
│   └── fal_api/           # Cloud API version
│       ├── AGENTS.md      # API rules
│       ├── decompose.py   # Core decomposition
│       ├── export.py      # Multi-format export
│       ├── generation.py  # Image generation/editing
│       ├── model_registry.py # Extensible model registry
│       ├── logging_config.py # Centralized logging
│       ├── cost_tracker.py # API cost tracking
│       ├── path_validator.py # Path validation utilities
│       ├── health_check.py # Self-diagnostic system
│       ├── app_test.py    # Test web UI
│       └── run_demo.py    # CLI tool
├── .claude/
│   ├── AGENTS.md          # Agent system rules
│   ├── CLAUDE.md          # This file
│   ├── skills/            # Auto-trigger modules (25 skills)
│   └── agents/            # Task delegation (8 agents)
├── docs/
│   ├── PRD.md             # Requirements
│   ├── LLD.md             # Design
│   ├── QUICK_START.md     # User guide
│   └── plans/             # Implementation plans
├── tests/                 # Test suites (539 tests)
└── assets/test_images/    # Sample images
```

## System Pipeline

```
┌─────────────────────────────────────────────────────────────────┐
│                    Image Master Agent                            │
├─────────────────────────────────────────────────────────────────┤
│  Phase 1: 분석 (Analysis)                                        │
│  ├── image-decompose (레이어 분해)                               │
│  ├── color-palette (색상 추출)                                   │
│  ├── text-extract (OCR)                                          │
│  ├── font-match (폰트 식별)                                      │
│  └── background-remove (배경 제거)                               │
├─────────────────────────────────────────────────────────────────┤
│  Phase 2: 편집 (Editing)                                         │
│  ├── text-replace (텍스트 교체)                                  │
│  ├── text-effect (텍스트 효과)                                   │
│  ├── text-overlay (텍스트 추가)                                  │
│  ├── style-transfer (스타일 변환)                                │
│  └── smart-upscale (업스케일)                                    │
├─────────────────────────────────────────────────────────────────┤
│  Phase 3: 생성 (Generation) - NEW                                │
│  ├── nano-banana-generate (빠른 이미지 생성)                     │
│  ├── nano-banana-pro-generate (고품질 이미지 생성)               │
│  ├── nano-banana-edit (이미지 편집)                              │
│  └── nano-banana-pro-edit (고급 이미지 편집)                     │
└─────────────────────────────────────────────────────────────────┘
```

## Available Skills (25 Skills)

### Core Skills
| Skill | Trigger | Action |
|-------|---------|--------|
| image-decompose | "분해", "decompose" | Image to layers |
| layer-export | "내보내기", "export" | Export to PPTX/PSD/ZIP |
| quick-edit | "색상 변경", "resize" | Simple layer edits |
| background-remove | "배경 제거", "누끼" | 2-layer separation |

### AI Enhancement Skills
| Skill | Trigger | Action |
|-------|---------|--------|
| smart-upscale | "업스케일", "upscale" | AI 2x/4x upscaling |
| style-transfer | "스타일", "watercolor" | Apply artistic styles |
| color-palette | "팔레트", "colors" | Extract color schemes |
| text-to-layer | "생성", "generate" | Create layers from text |

### Text Processing Skills
| Skill | Trigger | Action |
|-------|---------|--------|
| text-extract | "OCR", "텍스트 추출" | Extract text from images |
| text-translate | "번역", "translate" | Translate text content |
| text-overlay | "텍스트 추가", "watermark" | Add text to images |
| text-effect | "그림자", "neon" | Apply text effects |
| text-to-path | "곡선", "circular" | Text along paths |
| text-remove | "텍스트 제거", "erase" | Remove text via AI |
| text-replace | "교체", "replace" | Replace text in images |
| font-match | "폰트 찾기", "font" | Identify fonts |

### Generation Skills (Phase 3 - NEW)
| Skill | Trigger | Action | Cost |
|-------|---------|--------|------|
| nano-banana-generate | "이미지 생성", "generate" | Fast text-to-image | $0.039/이미지 |
| nano-banana-pro-generate | "고품질 생성", "pro generate" | High-quality 4K generation | $0.15/이미지 |
| nano-banana-edit | "편집", "edit" | Fast image editing | $0.039/이미지 |
| nano-banana-pro-edit | "고급 편집", "pro edit" | Advanced semantic editing | $0.15/이미지 |

### System Skills
| Skill | Trigger | Action |
|-------|---------|--------|
| system-health | "시스템 상태", "health check" | Run system diagnostics |

### LLM Integration Skills (Phase 4 - NEW)
| Skill | Trigger | Action |
|-------|---------|--------|
| prompt-optimizer | "프롬프트 개선", "optimize prompt" | AI-enhanced prompt improvement |
| smart-model-select | "모델 선택", "best model" | Cost-quality optimized model selection |
| quality-check | "품질 검사", "validate" | Vision AI quality validation |
| auto-recovery | "오류 복구", "auto retry" | Intelligent error recovery |

## Available SubAgents (8 Agents)

| Agent | When Used | Purpose |
|-------|-----------|---------|
| BatchProcessor | 2+ images | Bulk processing |
| LayerEditor | Multi-step edits | Complex editing |
| CompositionEngine | Combining layers | Moodboards, collages |
| QualityChecker | After decompose | Validate results |
| TemplateEngine | Marketing assets | Template composition |
| FinalComposer | Full pipeline | Analysis→Edit→Generate |
| SystemDiagnostics | System issues | Error pattern analysis |
| **IntelligentOrchestrator** | Natural language | LLM-powered orchestration (NEW) |

## Model Registry

확장 가능한 모델 레지스트리로 새 Fal AI 모델 쉽게 추가 가능:

```python
from src.fal_api.model_registry import ModelRegistry, get_model, list_models

# 모델 정보 조회
model = get_model("nano-banana-pro")
print(f"Price: ${model.price_per_image}")

# 모델 목록 조회
gen_models = list_models(model_type=ModelType.TEXT_TO_IMAGE)

# 새 모델 등록
ModelRegistry.register(
    "custom-model",
    endpoint="fal-ai/custom",
    model_type=ModelType.TEXT_TO_IMAGE,
    tier=ModelTier.STANDARD,
    price_per_image=0.05,
    description="Custom model"
)
```

### 등록된 모델

| Model | Type | Tier | Price |
|-------|------|------|-------|
| nano-banana | TEXT_TO_IMAGE | FAST | $0.039 |
| nano-banana-pro | TEXT_TO_IMAGE | PRO | $0.15 |
| nano-banana-edit | IMAGE_EDIT | FAST | $0.039 |
| nano-banana-pro-edit | IMAGE_EDIT | PRO | $0.15 |
| flux-schnell | TEXT_TO_IMAGE | FAST | $0.003 |
| flux-dev | TEXT_TO_IMAGE | STANDARD | $0.025 |
| creative-upscaler | UPSCALE | STANDARD | $0.02 |
| llava-next | ANALYSIS | STANDARD | $0.01 |
| lama-inpainting | IMAGE_EDIT | STANDARD | $0.01 |

## Key Commands

### Single Image
```bash
python src/fal_api/run_demo.py --image photo.png --layers 4
```

### Batch Processing
```bash
python src/fal_api/run_demo.py --batch ./photos --layers 4
```

### Export Only
```python
from src.fal_api.export import LayerExporter
exporter = LayerExporter(layer_files)
exporter.export_all("./output", "my_layers")
```

### Image Generation (NEW)
```python
from src.fal_api.generation import generate_image, edit_image

# Generate image from text
result = generate_image(
    prompt="a beautiful sunset over mountains",
    model="nano-banana-pro",
    resolution="4k"
)

# Edit existing image
result = edit_image(
    image_path="photo.png",
    prompt="change the sky to purple",
    model="nano-banana-edit"
)
```

## Test Suites

| Suite | Tests | Description |
|-------|-------|-------------|
| TDD Compliance | 29 | Core system verification |
| AI Enhancement | 25 | AI skill tests |
| Text Processing | 34 | Text skill tests |
| Phase 3 Generation | 89 | Generation system tests |
| Pipeline Integration | 61 | Full pipeline tests |
| Mock API | 55 | API logic tests |
| Integration | 57 | System integration tests |
| Error Handling | 59 | Error handling tests |
| Infrastructure | 35 | Logging, cost tracking, path validation |
| Health Check | 43 | Self-diagnostic system tests |
| LLM Integration | 52 | LLM client, prompt, router, quality, recovery |
| **Total** | **539** | **100% Pass Rate** |

```bash
# Run all tests
python tests/run_all_tests.py
```

## Infrastructure Modules

### Logging (logging_config.py)

```python
from src.fal_api import configure_logging, get_logger

# Configure logging
configure_logging(level="DEBUG", log_to_file=True, log_dir="./logs")

# Get logger for module
logger = get_logger("my_module")
logger.info("Processing image...")
```

### Cost Tracking (cost_tracker.py)

```python
from src.fal_api import CostTracker, record_cost, get_cost_report, OperationType

# Record costs
record_cost(OperationType.GENERATE, "nano-banana-pro", 0.15)
record_cost(OperationType.EDIT, "nano-banana-edit", 0.039)

# Get report
print(get_cost_report())

# With budget limit
tracker = CostTracker(budget_limit=10.00)
tracker.record(OperationType.GENERATE, "model", 0.50)
print(f"Remaining: ${tracker.budget_limit - tracker.get_total():.2f}")
```

### Path Validation (path_validator.py)

```python
from src.fal_api import validate_image, ensure_dir, list_images

# Validate image path
path = validate_image("photo.png")  # Raises if invalid

# Ensure directory exists
output_dir = ensure_dir("./output")

# List all images in directory
images = list_images("./photos", recursive=True)
```

### Health Check (health_check.py)

```python
from src.fal_api import (
    run_health_check, get_system_status,
    get_health_report, get_recent_errors
)

# Quick status check
status = get_system_status()  # Returns: 'ok', 'warning', 'error', or 'unknown'

# Full health check
results = run_health_check()
# Returns: {
#   'api_key': {...},
#   'dependencies': {...},
#   'disk_space': {...},
#   'output_directory': {...},
#   'overall_status': 'ok'
# }

# Human-readable report
print(get_health_report())

# View recent errors
errors = get_recent_errors(limit=5)
for error in errors:
    print(f"[{error['operation']}] {error['message']}")
```

**Checks Performed:**
| Check | OK | Warning | Error |
|-------|-----|---------|-------|
| API Key | Configured | Too short | Missing |
| Dependencies | All installed | Missing optional | Missing required |
| Disk Space | > 500MB | 100-500MB | < 100MB |
| Output Directory | Writable | - | Permission denied |

### LLM Integration (Phase 4 - NEW)

```python
from src.fal_api import (
    # Prompt Optimization
    enhance_prompt, generate_variations, score_prompt,
    # Model Selection
    select_model, assess_complexity,
    # Task Routing
    route_request, parse_intent, get_execution_plan,
    # Quality Validation
    validate_output, rate_generation, detect_artifacts,
    # Error Recovery
    analyze_error, suggest_recovery, auto_recover
)

# Enhance vague prompts (uses Gemini 3 Flash)
enhanced = enhance_prompt("nice sunset")
# Returns: "A breathtaking sunset with vibrant orange and purple sky..."

# Select optimal model for budget
result = select_model(
    task="Generate product photos",
    budget=0.20,
    prefer_quality=True
)
print(f"Use: {result['model']} (${result['cost']})")

# Route natural language requests
plan = route_request("배경 제거하고 스타일 변경해줘")
print(f"Skills: {plan['skills']}")
print(f"Estimated cost: ${plan['estimated_cost']}")

# Validate output quality (uses GPT-5.2 Vision)
quality = validate_output("generated.png")
print(f"Quality: {quality.overall:.0%} ({quality.level.value})")

# Auto-recover from errors
result = auto_recover(
    operation=generate_image,
    args=("prompt",),
    max_attempts=3
)
```

**LLM Models Used:**
| Task | Model | Provider | Purpose |
|------|-------|----------|---------|
| Prompt Enhancement | gemini-3-flash | Google | Fast, cost-effective |
| Task Routing | gemini-3-flash | Google | Intent parsing |
| Quality Validation | gpt-5.2 | OpenAI | Vision analysis |
| Error Analysis | claude-sonnet-4-5 | Anthropic | Complex reasoning |

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| FAL_KEY | Yes | Fal AI API key |
| FAL_LOG_LEVEL | No | Logging level (DEBUG, INFO, WARNING) |
| FAL_LOG_DIR | No | Directory for log files |
| FAL_LOG_TO_FILE | No | Enable file logging (true/false) |

## Cost Summary

| Operation | Cost |
|-----------|------|
| Image decomposition | ~$0.05/image |
| Nano Banana generation | $0.039/image |
| Nano Banana Pro generation (2K) | $0.15/image |
| Nano Banana Pro generation (4K) | $0.30/image |
| Upscale | ~$0.02/image |
| Style transfer | ~$0.03/image |
| OCR | ~$0.01/image |

## Golden Rules

1. Never hardcode FAL_KEY
2. Always preserve RGBA alpha channel
3. Max 10 layers per request
4. Use 640px resolution for best results
5. Use ModelRegistry for model selection

## Documentation

- [PRD](../docs/PRD.md) - Product requirements
- [LLD](../docs/LLD.md) - Technical design
- [Quick Start](../docs/QUICK_START.md) - User guide
- [Plan](../docs/plans/PLAN_agent_system.md) - Implementation plan
- [Root AGENTS.md](../AGENTS.md) - Project rules
