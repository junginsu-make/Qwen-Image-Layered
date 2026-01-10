---
name: text-remove
description: Remove text from images using AI inpainting
---

# Triggers

Keywords:
- remove text
- erase text
- delete text
- clean text
- text removal

Korean Keywords:
- 텍스트 제거
- 글자 지우기
- 문자 삭제
- 텍스트 지워줘
- 글씨 없애기

Patterns:
- "remove text from {image}"
- "erase all text in {image}"
- "clean up text from {image}"
- "{image}에서 텍스트 제거"
- "이 이미지의 글자 지워줘"

# Inputs

- image_path (string): Path to input image [required]
- mask_path (string): Custom mask for text areas [optional]
- auto_detect (boolean): Auto-detect text regions [optional, default: true]
- inpaint_method (string): Inpainting method (ai, telea, ns) [optional, default: ai]
- preserve_quality (boolean): Maintain image quality [optional, default: true]

# Outputs

- output_path (string): Path to cleaned image
- regions_removed (integer): Number of text regions processed
- text_detected (array): List of detected text before removal
- inpaint_method_used (string): Method used for inpainting

# Execution

```bash
cd /home/user/Qwen-Image-Layered
python -c "
from src.fal_api.text_remove import remove_text
result = remove_text(
    '{image_path}',
    mask_path='{mask_path}',
    auto_detect={auto_detect},
    inpaint_method='{inpaint_method}',
    preserve_quality={preserve_quality}
)
print(result)
"
```

# Validation

Before execution:
1. Validate image_path exists
2. If mask provided, verify dimensions match image
3. Check inpaint_method is supported
4. Ensure FAL_KEY for AI inpainting

# Error Handling

- No text detected: Return original with message
- Inpainting failure: Fall back to simpler method
- API timeout: Retry up to 3 times
- Large image: Process in tiles if needed

# Inpainting Methods

| Method | Description | Best For |
|--------|-------------|----------|
| ai | AI-powered Fal inpainting | Complex backgrounds |
| telea | OpenCV Telea algorithm | Simple backgrounds |
| ns | Navier-Stokes method | Smooth gradients |

# Example Usage

User: "Remove all text from this photo"
Action: Execute with auto_detect=true

User: "이 스크린샷에서 글자 지워줘"
Action: Execute with inpaint_method=ai

User: "Clean the watermark from this image"
Action: Execute with auto_detect=true, preserve_quality=true
