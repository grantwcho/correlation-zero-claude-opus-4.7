# Correlation Zero SDK

This package contains the reference Python interfaces that agent contributors
install locally:

- `Agent` base class
- `AgentQuery` request object
- the `freeform` response format
- manifest and contract validation helpers
- a small local test harness

The template keeps this package inside `sdk/` so contributors can
install it with:

```bash
python3 -m pip install -e ./sdk
```
