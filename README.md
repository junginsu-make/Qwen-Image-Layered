<p align="center">
    <img src="https://qianwen-res.oss-cn-beijing.aliyuncs.com/Qwen-Image/layered/qwen-image-layered-logo.png" width="800"/>
<p>
<p align="center">&nbsp&nbsp🤗 <a href="https://huggingface.co/Qwen/Qwen-Image-Layered">HuggingFace</a>&nbsp&nbsp | &nbsp&nbsp🤖 <a href="https://modelscope.cn/models/Qwen/Qwen-Image-Layered">ModelScope</a>&nbsp&nbsp | &nbsp&nbsp 📑 <a href="https://arxiv.org/abs/2512.15603">논문</a> &nbsp&nbsp | &nbsp&nbsp 📑 <a href="https://qwen.ai/blog?id=qwen-image-layered">블로그</a> &nbsp&nbsp | &nbsp&nbsp 🤗 <a href="https://huggingface.co/spaces/Qwen/Qwen-Image-Layered">데모</a> &nbsp&nbsp
</p>

<p align="center">
    <img src="https://qianwen-res.oss-cn-beijing.aliyuncs.com/Qwen-Image/layered/layered.JPG" width="1024"/>
<p>

## 소개

**Qwen-Image-Layered**를 소개합니다. 이 모델은 이미지를 여러 개의 RGBA 레이어로 분해할 수 있습니다. 이러한 레이어 표현은 **내재적 편집 가능성**을 제공합니다: 각 레이어를 다른 콘텐츠에 영향을 주지 않고 독립적으로 조작할 수 있습니다. 또한 이러한 레이어 표현은 크기 조절, 위치 변경, 색상 변경과 같은 **고품질 기본 작업**을 자연스럽게 지원합니다. 의미적 또는 구조적 구성 요소를 별도의 레이어로 물리적으로 분리함으로써, 고품질이며 일관된 편집이 가능합니다.

[![Qwen Image Layered](https://img.youtube.com/vi/OVhmiBrsziQ/0.jpg)](https://www.youtube.com/watch?v=OVhmiBrsziQ)

## 뉴스

- 2025.12.22: [Huggingface Spaces](https://huggingface.co/spaces/Qwen/Qwen-Image-Layered) 및 [Modelscope Studio](https://modelscope.cn/studios/Qwen/Qwen-Image-Layered)에서 Qwen-Image-Layered를 체험해보세요.
- 2025.12.19: Qwen-Image-Layered 모델 가중치 공개! [Huggingface](https://huggingface.co/Qwen/Qwen-Image-Layered) 및 [ModelScope](https://modelscope.cn/models/Qwen/Qwen-Image-Layered)에서 확인하세요!
- 2025.12.19: Qwen-Image-Layered 출시! 자세한 내용은 [블로그](https://qwen.ai/blog?id=qwen-image-layered)를 참조하세요!
- 2025.12.18: [연구 논문](https://arxiv.org/abs/2512.15603)을 Arxiv에 공개했습니다!

> [!NOTE]
> - 텍스트 프롬프트는 입력 이미지의 전체 내용을 설명하기 위한 것입니다. 부분적으로 가려진 요소도 포함됩니다(예: 전경 객체 뒤에 숨겨진 텍스트를 지정할 수 있음). 개별 레이어의 의미적 내용을 명시적으로 제어하기 위한 것은 아닙니다.
> - 공개된 가중치는 이미지-다중 RGBA 분해 작업에 특화되어 미세 조정되었습니다. 따라서 모델이 텍스트 조건부 추론을 지원하지만, 텍스트-다중 RGBA 생성 성능은 제한적입니다.

## 빠른 시작

### 로컬 GPU 사용 (권장 사양: NVIDIA GPU)

1. transformers>=4.51.3 확인 (Qwen2.5-VL 지원)

2. 최신 버전의 diffusers 설치
```bash
pip install git+https://github.com/huggingface/diffusers
pip install python-pptx
pip install psd-tools
```

```python
from diffusers import QwenImageLayeredPipeline
import torch
from PIL import Image

pipeline = QwenImageLayeredPipeline.from_pretrained("Qwen/Qwen-Image-Layered")
pipeline = pipeline.to("cuda", torch.bfloat16)
pipeline.set_progress_bar_config(disable=None)

image = Image.open("asserts/test_images/1.png").convert("RGBA")
inputs = {
    "image": image,
    "generator": torch.Generator(device='cuda').manual_seed(777),
    "true_cfg_scale": 4.0,
    "negative_prompt": " ",
    "num_inference_steps": 50,
    "num_images_per_prompt": 1,
    "layers": 4,
    "resolution": 640,      # 해상도 버킷 (640, 1024). 현재 버전에서는 640 권장
    "cfg_normalize": True,  # CFG 정규화 활성화 여부
    "use_en_prompt": True,  # 사용자가 캡션을 제공하지 않을 경우 자동 캡션 언어
}

with torch.inference_mode():
    output = pipeline(**inputs)
    output_image = output.images[0]

for i, image in enumerate(output_image):
    image.save(f"{i}.png")
```

## Qwen-Image-Layered 배포

다음 스크립트는 이미지를 분해하고 레이어를 pptx, zip, psd 파일로 내보낼 수 있는 Gradio 기반 웹 인터페이스를 시작합니다:
```bash
python src/app.py
```

분해 후 특정 레이어를 편집하려면, Qwen-Image-Edit를 사용하여 투명도가 있는 이미지를 편집할 수 있는 Gradio 기반 웹 인터페이스를 실행하세요:
```bash
python src/tool/edit_rgba_image.py
```

개별 분해된 레이어 편집 후, 다음 스크립트를 사용하여 새 이미지로 결합할 수 있습니다. 레이어를 아래에서 위 순서로 업로드하세요:
```bash
python src/tool/combine_layers.py
```

## 쇼케이스

### 응용 프로그램에서의 레이어 분해
이미지가 주어지면, Qwen-Image-Layered는 여러 RGBA 레이어로 분해할 수 있습니다:
![예시 이미지](https://qianwen-res.oss-cn-beijing.aliyuncs.com/Qwen-Image/layered/幻灯片1.JPG)

분해 후, 편집은 대상 레이어에만 적용되며, 나머지 콘텐츠와 물리적으로 분리되어 편집 간 일관성을 근본적으로 보장합니다.

예를 들어, 첫 번째 레이어의 색상을 변경하고 다른 모든 콘텐츠는 그대로 유지할 수 있습니다:
![예시 이미지](https://qianwen-res.oss-cn-beijing.aliyuncs.com/Qwen-Image/layered/幻灯片2.JPG)

두 번째 레이어의 소녀를 소년으로 교체할 수도 있습니다 (대상 레이어는 Qwen-Image-Edit로 편집):
![예시 이미지](https://qianwen-res.oss-cn-beijing.aliyuncs.com/Qwen-Image/layered/幻灯片3.JPG)

텍스트를 "Qwen-Image"로 수정 (대상 레이어는 Qwen-Image-Edit로 편집):
![예시 이미지](https://qianwen-res.oss-cn-beijing.aliyuncs.com/Qwen-Image/layered/幻灯片4.JPG)

또한, 레이어 구조는 기본 작업을 자연스럽게 지원합니다. 예를 들어, 원하지 않는 객체를 깔끔하게 삭제할 수 있습니다:
![예시 이미지](https://qianwen-res.oss-cn-beijing.aliyuncs.com/Qwen-Image/layered/幻灯片5.JPG)

왜곡 없이 객체 크기를 조절할 수도 있습니다:
![예시 이미지](https://qianwen-res.oss-cn-beijing.aliyuncs.com/Qwen-Image/layered/幻灯片6.JPG)

레이어 분해 후, 캔버스 내에서 객체를 자유롭게 이동할 수 있습니다:
![예시 이미지](https://qianwen-res.oss-cn-beijing.aliyuncs.com/Qwen-Image/layered/幻灯片7.JPG)

### 유연하고 반복적인 분해
Qwen-Image-Layered는 고정된 레이어 수에 제한되지 않습니다. 모델은 가변 레이어 분해를 지원합니다. 예를 들어, 필요에 따라 이미지를 3개 또는 8개 레이어로 분해할 수 있습니다:

![예시 이미지](https://qianwen-res.oss-cn-beijing.aliyuncs.com/Qwen-Image/layered/幻灯片8.JPG)

또한, 분해는 재귀적으로 적용될 수 있습니다: 모든 레이어는 다시 분해될 수 있어 무한 분해가 가능합니다.

![예시 이미지](https://qianwen-res.oss-cn-beijing.aliyuncs.com/Qwen-Image/layered/幻灯片9.JPG)


## 클라우드 API (GPU 불필요)

로컬 GPU가 없다면, **Fal AI API**를 사용하여 클라우드에서 Qwen-Image-Layered를 실행할 수 있습니다.

### 설정

1. 의존성 설치:
```bash
pip install -r requirements-fal.txt
```

2. [fal.ai](https://fal.ai)에서 API 키를 받고 `.env` 파일 생성:
```bash
cp .env.example .env
# .env를 편집하여 FAL_KEY 추가
```

### 사용법

**커맨드 라인:**
```bash
# 테스트 이미지 사용
python src/fal_api/run_demo.py --test-image 1 --layers 4

# 사용자 이미지 사용
python src/fal_api/run_demo.py --image path/to/image.png --layers 5 --output ./my_output
```

**Python API:**
```python
from src.fal_api import ImageLayerDecomposer, LayerExporter

# 이미지 분해
decomposer = ImageLayerDecomposer()
layer_files = decomposer.decompose_and_save(
    image_source="path/to/image.png",
    output_dir="./output",
    num_layers=4,
)

# 다양한 형식으로 내보내기
exporter = LayerExporter(layer_files)
results = exporter.export_all("./output", "my_layers")
# 결과: PNG, PPTX, PSD, ZIP
```

**간단한 한 줄 코드:**
```python
from src.fal_api.decompose import decompose_image

layer_files = decompose_image("image.png", output_dir="./output", num_layers=4)
```

### 비용
- 이미지당 약 **$0.05**
- 처리 시간: 15-30초


## AI 에이전트 시스템 (Claude Code 통합)

이 프로젝트는 자연어 제어를 위한 Claude Code 에이전트 시스템을 포함하며, **25개 Skills**과 **8개 SubAgents**를 제공합니다.

### 시스템 파이프라인

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
│  Phase 3: 생성 (Generation)                                      │
│  ├── nano-banana-generate (빠른 이미지 생성, $0.039)             │
│  ├── nano-banana-pro-generate (고품질 4K 생성, $0.15)            │
│  ├── nano-banana-edit (이미지 편집)                              │
│  └── nano-banana-pro-edit (고급 이미지 편집)                     │
├─────────────────────────────────────────────────────────────────┤
│  Phase 4: LLM 통합 (Intelligent Automation)                      │
│  ├── prompt-optimizer (프롬프트 개선)                            │
│  ├── smart-model-select (모델 선택)                              │
│  ├── quality-check (품질 검증)                                   │
│  └── auto-recovery (오류 복구)                                   │
└─────────────────────────────────────────────────────────────────┘
```

### 사용 가능한 Skills (25개)

| 카테고리 | Skills |
|----------|--------|
| **코어** | image-decompose, layer-export, quick-edit, background-remove |
| **AI 향상** | smart-upscale, style-transfer, color-palette, text-to-layer |
| **텍스트 처리** | text-extract, text-translate, text-overlay, text-effect, text-to-path, text-remove, text-replace, font-match |
| **생성** | nano-banana-generate, nano-banana-pro-generate, nano-banana-edit, nano-banana-pro-edit |
| **LLM 통합** | prompt-optimizer, smart-model-select, quality-check, auto-recovery |
| **시스템** | system-health |

### 사용 가능한 SubAgents (8개)

| Agent | 사용 시점 | 목적 |
|-------|-----------|------|
| `BatchProcessor` | 다중 이미지 | 진행률 표시와 함께 대량 처리 |
| `LayerEditor` | 복잡한 편집 | 다단계 편집 파이프라인 |
| `CompositionEngine` | 레이어 결합 | 무드보드, 콜라주 |
| `QualityChecker` | 분해 후 | 결과 품질 검증 |
| `TemplateEngine` | 마케팅 자산 | 템플릿 기반 구성 |
| `FinalComposer` | 전체 파이프라인 | 분석 → 편집 → 생성 |
| `SystemDiagnostics` | 시스템 문제 | 오류 패턴 분석 |
| `IntelligentOrchestrator` | 자연어 요청 | LLM 기반 작업 조율 |

### 이미지 생성 (Nano Banana)

Fal AI의 Nano Banana 모델을 사용하여 이미지 생성 또는 편집:

```python
from src.fal_api.generation import generate_image, edit_image

# 빠른 생성 ($0.039/이미지)
result = generate_image(
    prompt="산 위의 아름다운 일몰",
    model="nano-banana"
)

# 고품질 4K 생성 ($0.15/이미지, 4K: $0.30)
result = generate_image(
    prompt="전문적인 제품 사진",
    model="nano-banana-pro",
    resolution="4k"
)

# 기존 이미지 편집
result = edit_image(
    image_path="photo.png",
    prompt="배경을 해변으로 변경",
    model="nano-banana-edit"
)
```

### LLM 통합

Claude, GPT, Gemini를 활용한 지능형 자동화:

```python
from src.fal_api import enhance_prompt, select_model, route_request

# 프롬프트 개선 (Gemini 3 Flash 사용)
enhanced = enhance_prompt("예쁜 일몰")
# 결과: "산 위로 펼쳐진 선명한 주황색과 보라색 하늘의 숨막히는 일몰..."

# 최적 모델 선택
result = select_model(task="제품 사진 생성", budget=0.20)
print(f"추천 모델: {result['model']} (${result['cost']})")

# 자연어 요청 라우팅
plan = route_request("배경 제거하고 스타일 변경해줘")
print(f"Skills: {plan['skills']}")
```

### 모델 레지스트리

모든 Fal AI 모델을 위한 확장 가능한 레지스트리:

```python
from src.fal_api.model_registry import get_model, list_models

# 모델 정보 조회
model = get_model("nano-banana-pro")
print(f"가격: ${model.price_per_image}")

# 사용 가능한 모델 목록
models = list_models()
```

### 예시 명령어

```
"이 이미지를 5개 레이어로 분해해줘"
"photo.jpg에서 배경 제거해줘"
"레이어를 PPTX로 내보내기"
"Nano Banana Pro로 일몰 이미지 생성해줘"
"이 사진에 따뜻한 조명 추가해서 편집해줘"
"photos 폴더의 모든 이미지 처리해줘"
"이 이미지들로 무드보드 만들어줘"
```

### 테스트 스위트

**539개 자동화 테스트** (100% 통과율):

```bash
python tests/run_all_tests.py
```

| 테스트 스위트 | 테스트 수 | 설명 |
|--------------|----------|------|
| TDD Compliance | 29 | 코어 시스템 검증 |
| AI Enhancement | 25 | AI 스킬 테스트 |
| Text Processing | 34 | 텍스트 스킬 테스트 |
| Phase 3 Generation | 89 | 생성 시스템 테스트 |
| Pipeline Integration | 61 | 전체 파이프라인 테스트 |
| Mock API | 55 | API 로직 테스트 |
| Integration | 57 | 시스템 통합 테스트 |
| Error Handling | 59 | 오류 처리 테스트 |
| Infrastructure | 35 | 인프라 테스트 |
| Health Check | 43 | 자가 진단 테스트 |
| LLM Integration | 52 | LLM 통합 테스트 |

### 실제 API 테스트

```bash
# 빠른 테스트
python scripts/quick_test.py

# 전체 시스템 테스트
python scripts/real_api_test.py
```

## 비용 요약

| 작업 | 비용 |
|------|------|
| 이미지 분해 | ~$0.05/이미지 |
| Nano Banana 생성 | $0.039/이미지 |
| Nano Banana Pro 생성 (2K) | $0.15/이미지 |
| Nano Banana Pro 생성 (4K) | $0.30/이미지 |
| 업스케일 | ~$0.02/이미지 |
| 스타일 변환 | ~$0.03/이미지 |
| OCR | ~$0.01/이미지 |


## 라이선스

Qwen-Image-Layered는 Apache 2.0 라이선스 하에 제공됩니다.

## 인용

본 연구가 도움이 되셨다면 인용을 부탁드립니다.

```bibtex
@misc{yin2025qwenimagelayered,
      title={Qwen-Image-Layered: Towards Inherent Editability via Layer Decomposition},
      author={Shengming Yin, Zekai Zhang, Zecheng Tang, Kaiyuan Gao, Xiao Xu, Kun Yan, Jiahao Li, Yilei Chen, Yuxiang Chen, Heung-Yeung Shum, Lionel M. Ni, Jingren Zhou, Junyang Lin, Chenfei Wu},
      year={2025},
      eprint={2512.15603},
      archivePrefix={arXiv},
      primaryClass={cs.CV},
      url={https://arxiv.org/abs/2512.15603},
}
```
