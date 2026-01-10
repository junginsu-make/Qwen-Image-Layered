# Image Master Agent - Quick Start Guide

AI 기반 이미지 레이어 분해 및 처리 시스템 사용 가이드입니다.

## 목차

1. [설치](#설치)
2. [빠른 시작](#빠른-시작)
3. [Skills 사용법](#skills-사용법)
4. [SubAgents 사용법](#subagents-사용법)
5. [실전 예제](#실전-예제)
6. [문제 해결](#문제-해결)

---

## 설치

### 1. 요구사항

- Python 3.10 이상
- Fal AI API 키 (https://fal.ai 에서 발급)

### 2. 설치 단계

```bash
# 1. 저장소 클론
git clone https://github.com/junginsu-make/Qwen-Image-Layered.git
cd Qwen-Image-Layered

# 2. 의존성 설치
pip install -r requirements-fal.txt

# 3. 환경 설정
cp .env.example .env

# 4. API 키 설정 (.env 파일 편집)
# FAL_KEY=your_api_key_here
```

### 3. 설치 확인

```bash
python -c "from src.fal_api.decompose import ImageLayerDecomposer; print('OK')"
```

---

## 빠른 시작

### 이미지 레이어 분해 (CLI)

```bash
# 기본 사용 (4개 레이어로 분해)
python src/fal_api/run_demo.py --image photo.png

# 레이어 수 지정
python src/fal_api/run_demo.py --image photo.png --layers 6

# 출력 디렉토리 지정
python src/fal_api/run_demo.py --image photo.png --output ./my_output
```

### 웹 UI 실행

```bash
python src/fal_api/app_test.py
# 브라우저에서 http://localhost:7870 접속
```

### Python 코드에서 사용

```python
from src.fal_api.decompose import decompose_image

# 이미지 분해
result = decompose_image(
    image_path="photo.png",
    num_layers=4,
    output_dir="./output"
)

print(f"생성된 레이어: {result['layer_files']}")
```

---

## Skills 사용법

Skills는 특정 키워드로 자동 트리거되는 기능입니다.

### Core Skills

#### image-decompose (이미지 분해)
```
트리거: "분해", "decompose", "레이어로 나눠"

예시:
- "이 사진을 4개 레이어로 분해해줘"
- "Decompose this image into 6 layers"
```

#### layer-export (내보내기)
```
트리거: "내보내기", "export", "PPTX", "PSD"

예시:
- "레이어를 PSD로 내보내줘"
- "Export layers to PowerPoint"
```

#### background-remove (배경 제거)
```
트리거: "배경 제거", "누끼", "remove background"

예시:
- "이 사진 누끼 따줘"
- "Remove background from this image"
```

### AI Enhancement Skills

#### smart-upscale (업스케일)
```
트리거: "업스케일", "upscale", "해상도 높여"

예시:
- "이미지를 4배로 업스케일해줘"
- "Enhance resolution to 4x"

옵션:
- scale_factor: 2 또는 4 (기본값: 2)
```

#### style-transfer (스타일 변환)
```
트리거: "스타일", "watercolor", "수채화", "유화"

예시:
- "수채화 스타일로 변환해줘"
- "Apply oil painting style"

지원 스타일:
- watercolor (수채화)
- oil_painting (유화)
- sketch (스케치)
- cartoon (카툰)
- anime (애니메이션)
- pop_art (팝아트)
```

#### color-palette (색상 팔레트)
```
트리거: "팔레트", "색상 추출", "colors"

예시:
- "이 이미지의 색상 팔레트 추출해줘"
- "Extract 8 colors from this image"

출력: HEX, RGB, HSL 형식
```

#### text-to-layer (텍스트로 레이어 생성)
```
트리거: "레이어 생성", "generate layer"

예시:
- "빨간 자동차 레이어 생성해줘"
- "Generate a layer with golden sparkles"
```

### Text Processing Skills

#### text-extract (OCR)
```
트리거: "OCR", "텍스트 추출", "글자 인식"

예시:
- "이 스크린샷에서 텍스트 추출해줘"
- "Extract text from this document"

지원 언어: 한국어, 영어, 일본어, 중국어 등
```

#### text-translate (번역)
```
트리거: "번역", "translate"

예시:
- "이 텍스트를 영어로 번역해줘"
- "Translate to Korean"
```

#### text-overlay (텍스트 추가)
```
트리거: "텍스트 추가", "워터마크", "캡션"

예시:
- "이미지에 'Copyright 2024' 워터마크 추가"
- "Add caption at the bottom"

옵션:
- position: center, top, bottom, top-left 등
- font_size: 픽셀 단위
- color: HEX 코드
```

#### text-effect (텍스트 효과)
```
트리거: "그림자", "네온", "glow"

예시:
- "네온 효과로 'OPEN' 텍스트 만들어줘"
- "Add drop shadow to text"

지원 효과: shadow, glow, neon, outline, gradient, 3d
```

#### text-remove (텍스트 제거)
```
트리거: "텍스트 제거", "글자 지워", "erase text"

예시:
- "이 이미지에서 텍스트 지워줘"
- "Remove all text from this photo"
```

#### text-replace (텍스트 교체)
```
트리거: "텍스트 교체", "바꿔", "replace"

예시:
- "'SALE'을 'SOLD'로 바꿔줘"
- "Replace '$99' with '$79'"
```

#### font-match (폰트 찾기)
```
트리거: "폰트 찾기", "이 폰트 뭐야", "identify font"

예시:
- "이 로고의 폰트 찾아줘"
- "What font is this?"
```

---

## SubAgents 사용법

SubAgents는 복잡한 작업을 처리하는 전문 에이전트입니다.

### BatchProcessor (배치 처리)
```
사용 시점: 2개 이상 이미지 처리

예시:
- "photos 폴더의 모든 이미지를 레이어로 분해해줘"
- "Process all images in this directory"

기능:
- 자동 이미지 수집
- 진행률 표시
- 실패 처리 및 재시도
- 결과 리포트 생성
```

### LayerEditor (레이어 편집기)
```
사용 시점: 복잡한 멀티스텝 편집

예시:
- "레이어 1을 50% 축소하고, 레이어 2와 합성해줘"
- "Edit layer colors and merge"

기능:
- 세션 기반 편집
- Undo/Redo 지원
- 여러 작업 순차 실행
```

### CompositionEngine (합성 엔진)
```
사용 시점: 레이어 합성, 콜라주 생성

예시:
- "이 레이어들로 무드보드 만들어줘"
- "Create a collage with grid layout"

기능:
- 블렌드 모드 (multiply, screen, overlay 등)
- 레이아웃 템플릿 (grid, stack, featured)
```

### QualityChecker (품질 검사)
```
사용 시점: 분해 결과 검증

예시:
- "분해 결과 품질 검사해줘"
- "Check layer quality"

검사 항목:
- 완전성 (누락 영역)
- 투명도 처리
- 엣지 품질
- 색상 정확도
```

### TemplateEngine (템플릿 엔진)
```
사용 시점: 마케팅 자료 생성

예시:
- "이 제품 사진으로 인스타그램 포스트 만들어줘"
- "Create YouTube thumbnail with this image"

템플릿:
- social_square (1080x1080) - 인스타그램
- social_story (1080x1920) - 스토리
- thumbnail_yt (1280x720) - YouTube
- banner_wide (1920x480) - 웹 배너
```

---

## 실전 예제

### 예제 1: 제품 사진 처리

```python
from src.fal_api.decompose import decompose_image
from src.fal_api.export import LayerExporter

# 1. 이미지를 레이어로 분해
result = decompose_image("product.png", num_layers=4)

# 2. 다양한 형식으로 내보내기
exporter = LayerExporter(result['layer_files'])
exporter.export_all("./output", "product_layers")

# 결과: product_layers.pptx, product_layers.psd, product_layers.zip
```

### 예제 2: 배경 제거 후 새 배경 합성

```python
from src.fal_api.decompose import decompose_image

# 1. 배경 분리 (2 레이어)
result = decompose_image("portrait.png", num_layers=2)

# 2. 전경 레이어(layer_1.png)를 새 배경과 합성
# CompositionEngine 사용
```

### 예제 3: 소셜 미디어 포스트 자동 생성

```
1. 제품 이미지 → image-decompose로 분해
2. 배경 레이어 → style-transfer로 스타일 변환
3. TemplateEngine → social_square 템플릿 적용
4. text-overlay → 제품명 추가
5. layer-export → 최종 내보내기
```

---

## 문제 해결

### FAQ

**Q: FAL_KEY 오류가 발생해요**
```
A: .env 파일에 FAL_KEY가 올바르게 설정되었는지 확인하세요.
   FAL_KEY=fal_xxxxxxxxxxxxx
```

**Q: 이미지 분해가 느려요**
```
A: Fal AI API 처리 시간은 15-30초입니다.
   이미지 크기가 크면 640px로 리사이즈하면 더 빠릅니다.
```

**Q: 레이어 수가 요청한 것과 달라요**
```
A: 이미지 복잡도에 따라 최적 레이어 수가 조정될 수 있습니다.
   2-10개 범위 내에서 요청하세요.
```

**Q: 한글이 깨져요**
```
A: text-extract의 language 옵션을 'ko'로 설정하세요.
   폰트가 한글을 지원하는지도 확인하세요.
```

### 오류 코드

| 코드 | 의미 | 해결 방법 |
|------|------|----------|
| FAL_001 | API 키 오류 | .env 파일 확인 |
| FAL_002 | 이미지 형식 오류 | PNG, JPG, WebP만 지원 |
| FAL_003 | 타임아웃 | 재시도 또는 이미지 크기 줄이기 |
| FAL_004 | 레이어 수 초과 | 2-10 범위로 설정 |

---

## Phase 3: 이미지 생성 (Nano Banana)

Phase 3는 분석과 편집 결과를 바탕으로 최종 이미지를 생성합니다.

### 사용 가능한 모델

| 모델 | 용도 | 비용 | 특징 |
|------|------|------|------|
| nano-banana | 빠른 생성 | $0.039/이미지 | 빠른 반복, 초안 |
| nano-banana-pro | 고품질 생성 | $0.15/이미지 (4K: $0.30) | 완벽한 텍스트, 4K 지원 |
| nano-banana-edit | 빠른 편집 | $0.039/이미지 | 간단한 수정 |
| nano-banana-pro-edit | 고급 편집 | $0.15/이미지 | 시맨틱 이해 기반 |

### 이미지 생성 예제

```python
from src.fal_api.generation import generate_image, edit_image

# 빠른 생성 (초안용)
result = generate_image(
    prompt="a cute cat sitting on a couch",
    model="nano-banana"
)

# 고품질 생성 (프로덕션용)
result = generate_image(
    prompt="professional product photography of a watch",
    model="nano-banana-pro",
    resolution="4k"
)

print(f"생성된 이미지: {result['generated_images']}")
print(f"비용: ${result['cost']}")
```

### 이미지 편집 예제

```python
# 빠른 편집
result = edit_image(
    image_path="photo.png",
    prompt="change the sky to purple sunset",
    model="nano-banana-edit"
)

# 고급 편집 (시맨틱 이해)
result = edit_image(
    image_path="portrait.png",
    prompt="add warm golden hour lighting while preserving skin tones",
    model="nano-banana-pro-edit",
    resolution="4k"
)
```

### FinalComposer SubAgent

전체 파이프라인을 자동 실행하는 에이전트:

```
사용 시점: 분석 -> 편집 -> 생성 전체 워크플로우

예시:
- "이 이미지를 분석해서 마케팅 배너 만들어줘"
- "제품 사진을 고품질로 재생성해줘"

기능:
1. 이미지 분석 (색상, 텍스트, 레이어)
2. 최적 모델 자동 선택
3. 컨텍스트 기반 프롬프트 강화
4. 최종 이미지 생성
```

### 모델 레지스트리

새 모델을 쉽게 추가할 수 있는 확장 가능한 구조:

```python
from src.fal_api.model_registry import ModelRegistry, get_model, list_models

# 모델 정보 조회
model = get_model("nano-banana-pro")
print(f"모델: {model.name}")
print(f"가격: ${model.price_per_image}")
print(f"4K 지원: {model.supports_4k}")

# 사용 가능한 모델 목록
all_models = list_models()
for m in all_models:
    print(f"- {m.name}: {m.tier.value}, ${m.price_per_image}")
```

---

## 추가 리소스

- [PRD 문서](PRD.md) - 제품 요구사항
- [LLD 문서](LLD.md) - 기술 설계
- [AGENTS.md](../AGENTS.md) - 시스템 규칙
- [API 문서](https://fal.ai/docs) - Fal AI API

---

## 비용 안내

| 작업 | 예상 비용 |
|------|----------|
| 이미지 분해 | ~$0.05/이미지 |
| Nano Banana 생성 | $0.039/이미지 |
| Nano Banana Pro 생성 (2K) | $0.15/이미지 |
| Nano Banana Pro 생성 (4K) | $0.30/이미지 |
| 업스케일 | ~$0.02/이미지 |
| 스타일 변환 | ~$0.03/이미지 |
| 텍스트 생성 | ~$0.03/이미지 |
| OCR | ~$0.01/이미지 |

---

## 테스트 실행

```bash
# 전체 테스트 실행 (444개 테스트)
python tests/run_all_tests.py

# Phase 3 테스트만 실행
python tests/run_phase3_tests.py
python tests/test_pipeline_integration.py
```

---

*최종 업데이트: 2026-01-10*
