# API 테스트 스크립트

Fal AI API를 실제로 테스트하는 스크립트들입니다.

## 설치

```bash
pip install fal-client Pillow python-pptx python-dotenv requests
```

## .env 설정

프로젝트 루트에 `.env` 파일 생성:

```
FAL_KEY=your-fal-api-key
```

## 스크립트

### quick_test.py

핵심 기능만 빠르게 테스트:
- 이미지 생성
- 배경 제거

```bash
python scripts/quick_test.py
```

### real_api_test.py

전체 시스템 종합 테스트:
- 모든 모듈 import 확인
- 이미지 생성/편집
- Export 기능
- Health Check

```bash
python scripts/real_api_test.py
```

## 결과

테스트 결과물은 `output/` 폴더에 저장됩니다:
- `test_image.png` - 생성된 테스트 이미지
- `generated_test.png` - AI 생성 이미지
- `bg_removed.png` - 배경 제거 결과
- `test_export.pptx` - PPTX 내보내기 테스트

## 비용

| 테스트 | 예상 비용 |
|--------|----------|
| quick_test.py | ~$0.05 |
| real_api_test.py | ~$0.10 |
