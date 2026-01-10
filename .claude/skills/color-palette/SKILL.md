---
name: color-palette
description: Extract and analyze color palettes from images or layers
---

# Triggers

Keywords:
- color palette
- extract colors
- analyze colors
- get palette
- color scheme

Korean Keywords:
- 색상 팔레트
- 컬러 추출
- 색상 분석
- 팔레트 추출
- 색 추출

Patterns:
- "extract colors from {image}"
- "get palette from {image}"
- "analyze color scheme of {image}"
- "{image}에서 색상 추출"
- "이 이미지의 팔레트"

# Inputs

- image_path (string): Path to input image or layer [required]
- num_colors (integer): Number of colors to extract (3-12) [optional, default: 5]
- format (string): Output format (hex, rgb, hsl) [optional, default: hex]
- include_names (boolean): Include color names [optional, default: true]
- per_layer (boolean): Extract separately for each layer [optional, default: false]

# Outputs

- colors (array): List of extracted colors
  - value (string): Color in requested format (#RRGGBB, rgb(), hsl())
  - name (string): Human-readable color name
  - percentage (float): Percentage of image this color represents
- dominant_color (object): Most prominent color
- palette_type (string): Warm, cool, neutral, vibrant, muted
- harmony (string): Complementary, analogous, triadic, etc.

# Execution

```bash
cd /home/user/Qwen-Image-Layered
python -c "
from src.fal_api.color_palette import extract_palette
result = extract_palette(
    '{image_path}',
    num_colors={num_colors},
    format='{format}',
    include_names={include_names}
)
print(result)
"
```

# Validation

Before execution:
1. Validate image_path exists
2. Ensure num_colors is between 3 and 12
3. Verify format is one of: hex, rgb, hsl
4. Check image is readable

# Error Handling

- Image not found: Return clear error message
- Invalid format: Default to hex with warning
- Too few colors: Reduce num_colors to available unique colors
- Transparent images: Analyze only non-transparent pixels

# Output Example

```json
{
  "colors": [
    {"value": "#2C5F8C", "name": "Steel Blue", "percentage": 35.2},
    {"value": "#E8D5B7", "name": "Wheat", "percentage": 28.1},
    {"value": "#4A7C59", "name": "Forest Green", "percentage": 18.4},
    {"value": "#8B4513", "name": "Saddle Brown", "percentage": 12.3},
    {"value": "#F5F5DC", "name": "Beige", "percentage": 6.0}
  ],
  "dominant_color": {"value": "#2C5F8C", "name": "Steel Blue"},
  "palette_type": "cool",
  "harmony": "analogous"
}
```

# Example Usage

User: "Extract 8 colors from this image"
Action: Execute with num_colors=8, format=hex

User: "이 레이어의 색상 팔레트를 분석해줘"
Action: Execute with image_path=<provided>, num_colors=5

User: "Get RGB values of main colors in layer_1.png"
Action: Execute with image_path=layer_1.png, format=rgb
