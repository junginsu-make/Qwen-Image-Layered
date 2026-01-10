# 프로젝트 인수인계 문서

> **목적**: 새로운 Claude 세션이 이 프로젝트를 완벽히 이해하고 계속 개발할 수 있도록 하는 종합 문서

---

## 1. 프로젝트 개요

### 프로젝트명
**Qwen-Image-Layered** - AI 기반 이미지 레이어 분해 시스템

### 핵심 기능
이미지를 여러 개의 RGBA 레이어로 분해하여 개별 편집이 가능하게 하는 시스템

### 원본 저장소
- **원본**: [Qwen/Qwen-Image-Layered](https://github.com/Qwen/Qwen-Image-Layered) (Alibaba Qwen 팀)
- **Fork**: [junginsu-make/Qwen-Image-Layered](https://github.com/junginsu-make/Qwen-Image-Layered)

### 개발 현황
| 항목 | 상태 |
|------|------|
| 기본 기능 | ✅ 완료 |
| Cloud API 통합 | ✅ 완료 |
| AI Agent 시스템 | ✅ 완료 |
| LLM 통합 | ✅ 완료 |
| 테스트 | ✅ 539개 (100% 통과) |
| 실제 API 테스트 | ⏳ 대기 (로컬 환경 필요) |

---

## 2. 기술 스택

### 핵심 기술
```
Python 3.10+
├── Fal AI API (클라우드 이미지 처리)
│   ├── qwen-image-layered (레이어 분해)
│   ├── nano-banana (빠른 이미지 생성)
│   └── nano-banana-pro (고품질 4K 생성)
├── Pillow (이미지 처리)
├── python-pptx (PPTX 내보내기)
├── psd-tools (PSD 내보내기)
└── Gradio (웹 인터페이스)
```

### LLM 통합 (Phase 4)
```
Claude: claude-sonnet-4-5-20250929 (오류 분석)
GPT: gpt-5.2 (Vision 품질 검증)
Gemini: gemini-3-flash (프롬프트 최적화, 라우팅)
```

### 필요한 API 키
| 키 | 용도 | 필수 여부 |
|----|------|----------|
| FAL_KEY | Fal AI (이미지 처리) | ✅ 필수 |
| ANTHROPIC_API_KEY | Claude (오류 분석) | 선택 |
| OPENAI_API_KEY | GPT (품질 검증) | 선택 |
| GOOGLE_API_KEY | Gemini (프롬프트) | 선택 |

---

## 3. 프로젝트 구조

```
Qwen-Image-Layered/
├── .claude/                    # Claude Code 설정
│   ├── CLAUDE.md              # 📌 주요 컨텍스트 파일 (필독)
│   ├── AGENTS.md              # 에이전트 규칙
│   ├── skills/                # 25개 Skills 정의
│   │   ├── image-decompose/
│   │   ├── nano-banana-generate/
│   │   ├── prompt-optimizer/
│   │   └── ... (22개 더)
│   └── agents/                # 8개 SubAgents 정의
│       ├── batch_processor.md
│       ├── intelligent_orchestrator.md
│       └── ... (6개 더)
│
├── src/
│   ├── app.py                 # 로컬 GPU 버전 (원본)
│   └── fal_api/               # ⭐ 클라우드 API 버전 (주요 개발 영역)
│       ├── __init__.py        # 모듈 exports
│       ├── decompose.py       # 이미지 분해
│       ├── generation.py      # 이미지 생성/편집
│       ├── export.py          # PPTX/PSD/ZIP 내보내기
│       ├── model_registry.py  # 모델 레지스트리
│       ├── llm_client.py      # LLM 통합 클라이언트
│       ├── prompt_optimizer.py # 프롬프트 최적화
│       ├── intelligent_router.py # 작업 라우팅
│       ├── quality_validator.py # 품질 검증
│       ├── error_recovery.py  # 오류 복구
│       ├── health_check.py    # 시스템 진단
│       ├── logging_config.py  # 로깅
│       ├── cost_tracker.py    # 비용 추적
│       └── path_validator.py  # 경로 검증
│
├── tests/                     # 539개 테스트
│   ├── run_all_tests.py       # 전체 테스트 실행
│   ├── test_llm_integration.py # LLM 통합 테스트 (52개)
│   └── ...
│
├── scripts/                   # 실제 API 테스트 스크립트
│   ├── quick_test.py          # 빠른 테스트
│   └── real_api_test.py       # 종합 테스트
│
├── docs/                      # 문서
│   ├── PRD.md                 # 요구사항
│   ├── LLD.md                 # 설계 문서
│   └── QUICK_START.md         # 사용 가이드
│
├── .env.example               # 환경변수 예시
├── requirements-fal.txt       # 의존성
├── README.md                  # 메인 문서 (한국어)
└── PROJECT_HANDOFF.md         # 📌 이 문서
```

---

## 4. 구현된 기능 상세

### Phase 1: 분석 (Analysis)
| 기능 | 파일 | 설명 |
|------|------|------|
| 이미지 분해 | decompose.py | 이미지 → 여러 RGBA 레이어 |
| 배경 제거 | decompose.py | 2레이어 분리 (전경/배경) |
| 색상 추출 | color_palette.py | 이미지에서 색상 팔레트 추출 |
| OCR | text_ocr.py | 이미지에서 텍스트 추출 |
| 폰트 식별 | font_match.py | 이미지의 폰트 식별 |

### Phase 2: 편집 (Editing)
| 기능 | 파일 | 설명 |
|------|------|------|
| 텍스트 교체 | text_replace.py | 이미지 내 텍스트 교체 |
| 텍스트 효과 | text_effect.py | 그림자, 네온 등 효과 |
| 스타일 변환 | style_transfer.py | 수채화 등 스타일 적용 |
| 업스케일 | upscale.py | AI 2x/4x 업스케일링 |

### Phase 3: 생성 (Generation)
| 기능 | 파일 | 설명 | 비용 |
|------|------|------|------|
| 빠른 생성 | generation.py | Nano Banana 모델 | $0.039 |
| 고품질 생성 | generation.py | Nano Banana Pro | $0.15 |
| 이미지 편집 | generation.py | AI 기반 편집 | $0.039-0.15 |

### Phase 4: LLM 통합 (Intelligent Automation)
| 기능 | 파일 | 사용 모델 |
|------|------|----------|
| 프롬프트 최적화 | prompt_optimizer.py | Gemini 3 Flash |
| 모델 선택 | model_selector.py | 규칙 기반 |
| 작업 라우팅 | intelligent_router.py | Gemini 3 Flash |
| 품질 검증 | quality_validator.py | GPT-5.2 Vision |
| 오류 복구 | error_recovery.py | Claude Sonnet 4.5 |

---

## 5. 테스트 현황

### 테스트 스위트
| 스위트 | 테스트 수 | 파일 |
|--------|----------|------|
| TDD Compliance | 29 | run_tests.py |
| AI Enhancement | 25 | run_new_tests.py |
| Text Processing | 34 | run_text_tests.py |
| Phase 3 Generation | 89 | run_phase3_tests.py |
| Pipeline Integration | 61 | test_pipeline_integration.py |
| Mock API | 55 | test_mock_api.py |
| Integration | 57 | test_integration.py |
| Error Handling | 59 | test_error_handling.py |
| Infrastructure | 35 | test_infrastructure.py |
| Health Check | 43 | test_health_check.py |
| LLM Integration | 52 | test_llm_integration.py |
| **총계** | **539** | run_all_tests.py |

### 테스트 실행
```bash
# 전체 테스트
python tests/run_all_tests.py

# 특정 테스트만
python tests/test_llm_integration.py
```

### 중요 참고사항
- 대부분 **Mock 테스트** (실제 API 호출 없음)
- 실제 API 테스트는 `scripts/` 폴더의 스크립트 사용
- 로컬 환경에서 FAL_KEY 설정 후 실행 필요

---

## 6. 사용 방법

### 설치
```bash
pip install -r requirements-fal.txt
```

### 환경 설정
```bash
cp .env.example .env
# .env 파일에 FAL_KEY 추가
```

### 이미지 분해
```python
from src.fal_api import ImageLayerDecomposer, LayerExporter

# 분해
decomposer = ImageLayerDecomposer()
layers = decomposer.decompose_and_save("image.png", num_layers=4)

# 내보내기
exporter = LayerExporter(layers)
exporter.export_all("./output", "my_layers")
```

### 이미지 생성
```python
from src.fal_api.generation import generate_image

result = generate_image(
    prompt="아름다운 일몰",
    model="nano-banana-pro"
)
```

---

## 7. 남은 작업 / 개선 가능 사항

### 완료되지 않은 작업
| 작업 | 상태 | 설명 |
|------|------|------|
| 실제 API 테스트 | ⏳ | 로컬 환경에서 FAL_KEY로 테스트 필요 |
| LLM API 키 통합 | ⏳ | Claude/GPT/Gemini 실제 연동 |

### 향후 개선 가능 사항
1. **웹 UI 개선**: Gradio 인터페이스 확장
2. **배치 처리 최적화**: 대량 이미지 처리 성능 개선
3. **캐싱 시스템**: API 호출 결과 캐싱
4. **사용자 인증**: 다중 사용자 지원

---

## 8. 주요 파일 설명

### 📌 필독 파일
| 파일 | 설명 |
|------|------|
| `.claude/CLAUDE.md` | Claude가 참조하는 주요 컨텍스트 |
| `README.md` | 프로젝트 메인 문서 (한국어) |
| `docs/QUICK_START.md` | 사용자 가이드 |
| `docs/LLD.md` | 기술 설계 문서 |

### 핵심 코드 파일
| 파일 | 설명 |
|------|------|
| `src/fal_api/__init__.py` | 모든 모듈 exports |
| `src/fal_api/decompose.py` | 이미지 분해 핵심 로직 |
| `src/fal_api/generation.py` | 이미지 생성 핵심 로직 |
| `src/fal_api/llm_client.py` | LLM 통합 클라이언트 |

---

## 9. 개발 가이드라인

### 코드 스타일
- Python 3.10+ 타입 힌트 사용
- Docstring 필수 (Google 스타일)
- 함수/클래스 단위 테스트 작성

### 새 기능 추가 시
1. `tests/` 에 테스트 먼저 작성 (TDD)
2. `src/fal_api/` 에 구현
3. `src/fal_api/__init__.py` 에 export 추가
4. `.claude/skills/` 에 Skill 정의 (필요시)
5. 문서 업데이트

### 커밋 규칙
```
Add: 새 기능 추가
Update: 기존 기능 수정
Fix: 버그 수정
Docs: 문서 수정
Test: 테스트 추가/수정
```

---

## 10. 문제 해결

### 자주 발생하는 문제

**Q: FAL_KEY 오류**
```
A: .env 파일에 FAL_KEY 설정 확인
   FAL_KEY=your-api-key
```

**Q: 모듈 import 오류**
```
A: 프로젝트 루트에서 실행 또는 PYTHONPATH 설정
   export PYTHONPATH=/path/to/Qwen-Image-Layered
```

**Q: 테스트 실패**
```
A: python tests/run_all_tests.py 로 전체 테스트 확인
   대부분 Mock 테스트이므로 API 키 없이도 통과해야 함
```

---

## 11. 연락처 및 참고 자료

### 원본 프로젝트
- GitHub: https://github.com/Qwen/Qwen-Image-Layered
- 논문: https://arxiv.org/abs/2512.15603
- 데모: https://huggingface.co/spaces/Qwen/Qwen-Image-Layered

### Fal AI
- 문서: https://fal.ai/docs
- API 키 발급: https://fal.ai (Dashboard → Keys)

---

## 12. 새 세션 시작 시 체크리스트

새로운 Claude 세션에서 이 프로젝트 작업 시:

- [ ] `.claude/CLAUDE.md` 읽기
- [ ] `PROJECT_HANDOFF.md` (이 문서) 읽기
- [ ] `.env` 파일 존재 확인
- [ ] `python tests/run_all_tests.py` 실행하여 시스템 상태 확인
- [ ] 작업할 기능/버그 파악
- [ ] 관련 코드 파일 읽기
- [ ] TDD로 테스트 먼저 작성 후 구현

---

*마지막 업데이트: 2026년 1월*
*작성: Claude (Anthropic)*
