# system-health

System health check and diagnostics skill.

## Description

Performs comprehensive system health checks including:
- API key validation
- Dependency verification
- Disk space monitoring
- Output directory accessibility
- Recent error tracking

## Triggers

Activate this skill when user mentions:
- "시스템 상태", "system status"
- "헬스 체크", "health check"
- "진단", "diagnostics"
- "오류 확인", "check errors"
- "시스템 점검", "system check"

## Usage

```python
from src.fal_api.health_check import (
    run_health_check,
    get_system_status,
    get_recent_errors,
    get_health_report
)

# Quick status check
status = get_system_status()
print(f"System status: {status}")

# Full health check
results = run_health_check()
for key, value in results.items():
    print(f"{key}: {value}")

# Human-readable report
print(get_health_report())

# Recent errors
errors = get_recent_errors(limit=5)
for error in errors:
    print(f"[{error['operation']}] {error['message']}")
```

## Output

### Check Results

| Field | Description |
|-------|-------------|
| `api_key` | FAL_KEY configuration status |
| `dependencies` | Required package installation status |
| `disk_space` | Available disk space |
| `output_directory` | Output folder accessibility |
| `overall_status` | Combined status (ok/warning/error) |

### Status Values

| Status | Meaning |
|--------|---------|
| `ok` | All checks passed |
| `warning` | Non-critical issues found |
| `error` | Critical issues require attention |
| `unknown` | Unable to determine status |

## Error Tracking

The system automatically tracks errors. You can:

```python
from src.fal_api.health_check import record_error, get_recent_errors

# Record an error (usually called automatically)
record_error("decompose", "API timeout after 30 seconds")

# View recent errors
errors = get_recent_errors(limit=10)
```

## Example Response

```
============================================================
System Health Report
============================================================
Timestamp: 2026-01-10T12:00:00
Overall Status: OK

--- API Key ---
  Status: ok
  API key configured (fal_...xyz)

--- Dependencies ---
  Status: ok
  All dependencies installed

--- Disk Space ---
  Status: ok
  Sufficient disk space: 45.2 GB

--- Output Directory ---
  Status: ok
  Output directory ready: ./output
============================================================
```

## Troubleshooting Actions

When issues are detected:

| Issue | Recommended Action |
|-------|-------------------|
| API key missing | Set FAL_KEY in .env file |
| Missing dependencies | Run `pip install -r requirements-fal.txt` |
| Low disk space | Free up space or change output directory |
| Output directory error | Check permissions or create directory |
