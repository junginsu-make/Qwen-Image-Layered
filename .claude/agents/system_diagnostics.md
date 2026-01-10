# SystemDiagnostics SubAgent

Comprehensive system diagnostics and troubleshooting agent.

## Description

The SystemDiagnostics agent performs deep system analysis and provides actionable recommendations. It goes beyond simple health checks to diagnose complex issues and suggest solutions.

## When to Use

Automatically delegate to SystemDiagnostics when:
- User reports system problems or errors
- Multiple consecutive failures occur
- User asks for troubleshooting help
- System health check shows warnings or errors
- Before starting batch processing (preventive check)

## Capabilities

### 1. Deep System Analysis
- API connectivity testing
- Dependency version verification
- Configuration validation
- Resource availability check

### 2. Error Analysis
- Pattern detection in recent errors
- Root cause identification
- Correlation with system state

### 3. Performance Check
- Memory usage monitoring
- Disk I/O assessment
- Network latency to API

### 4. Automated Fixes
- Missing dependency installation suggestions
- Configuration repair guidance
- Cleanup recommendations

## Workflow

```
┌─────────────────────────────────────────────────────────────┐
│                 SystemDiagnostics Agent                      │
├─────────────────────────────────────────────────────────────┤
│  Step 1: Collect Information                                 │
│  ├── Run health checks                                       │
│  ├── Gather recent errors                                    │
│  ├── Check system resources                                  │
│  └── Verify configurations                                   │
├─────────────────────────────────────────────────────────────┤
│  Step 2: Analyze Results                                     │
│  ├── Identify issues                                         │
│  ├── Determine severity                                      │
│  ├── Find root causes                                        │
│  └── Check for patterns                                      │
├─────────────────────────────────────────────────────────────┤
│  Step 3: Generate Recommendations                            │
│  ├── Prioritize fixes                                        │
│  ├── Provide step-by-step solutions                          │
│  └── Suggest preventive measures                             │
├─────────────────────────────────────────────────────────────┤
│  Step 4: Report                                              │
│  ├── Summary of findings                                     │
│  ├── Detailed issue list                                     │
│  └── Action items                                            │
└─────────────────────────────────────────────────────────────┘
```

## Implementation

```python
from src.fal_api.health_check import (
    HealthChecker,
    run_health_check,
    get_recent_errors,
    get_health_report
)
from src.fal_api.cost_tracker import get_cost_report

def run_diagnostics():
    """Run comprehensive diagnostics."""

    # Step 1: Collect information
    checker = HealthChecker()
    health_results = checker.check_all()
    recent_errors = checker.get_recent_errors(limit=20)
    cost_report = get_cost_report()

    # Step 2: Analyze
    issues = []

    if health_results['api_key']['status'] != 'ok':
        issues.append({
            'severity': 'critical',
            'component': 'API Key',
            'problem': health_results['api_key']['message'],
            'solution': 'Set FAL_KEY in .env file'
        })

    if health_results['dependencies']['status'] != 'ok':
        missing = health_results['dependencies'].get('missing_required', [])
        issues.append({
            'severity': 'critical' if missing else 'warning',
            'component': 'Dependencies',
            'problem': health_results['dependencies']['message'],
            'solution': 'pip install -r requirements-fal.txt'
        })

    if health_results['disk_space']['status'] != 'ok':
        issues.append({
            'severity': 'warning',
            'component': 'Disk Space',
            'problem': health_results['disk_space']['message'],
            'solution': 'Free up disk space or change output directory'
        })

    # Step 3: Check error patterns
    if len(recent_errors) > 5:
        # Check for repeated errors
        operations = [e['operation'] for e in recent_errors]
        most_common = max(set(operations), key=operations.count)
        count = operations.count(most_common)

        if count > 3:
            issues.append({
                'severity': 'warning',
                'component': 'Error Pattern',
                'problem': f"Repeated failures in '{most_common}' ({count} times)",
                'solution': f"Investigate {most_common} operation"
            })

    # Step 4: Generate report
    return {
        'status': 'error' if any(i['severity'] == 'critical' for i in issues) else
                  'warning' if issues else 'ok',
        'issues': issues,
        'health_check': health_results,
        'recent_errors': recent_errors[:5],
        'recommendations': [i['solution'] for i in issues]
    }
```

## Output Format

```json
{
  "status": "warning",
  "issues": [
    {
      "severity": "warning",
      "component": "Disk Space",
      "problem": "Low disk space: 450 MB",
      "solution": "Free up disk space or change output directory"
    }
  ],
  "health_check": { ... },
  "recent_errors": [ ... ],
  "recommendations": [
    "Free up disk space or change output directory"
  ]
}
```

## Error Pattern Detection

The agent detects these common patterns:

| Pattern | Indication | Action |
|---------|------------|--------|
| Repeated timeouts | Network/API issues | Check connectivity |
| API errors cluster | Rate limiting or key issues | Verify API key |
| Disk errors | Storage full | Clear temp files |
| Import errors | Missing packages | Reinstall dependencies |

## Usage Examples

```
User: "이미지 처리가 계속 실패해요"
→ SystemDiagnostics runs full analysis

User: "시스템 상태 점검해줘"
→ Triggers comprehensive diagnostics

User: "왜 오류가 자꾸 나는지 모르겠어요"
→ Error pattern analysis and root cause identification
```

## Integration

This agent integrates with:
- `health_check.py` - Core health checking
- `cost_tracker.py` - Cost analysis
- `logging_config.py` - Log analysis
- `errors.py` - Error classification
