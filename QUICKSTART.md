# Quickstart

This is the 5-minute path from clone to first valid response.

## 1. Copy the smallest runnable example

```bash
cp -r examples/01-minimal/* .
```

## 2. Run the local checks

```bash
./tools/test_agent.sh
```

That gives you a root-level `agent.py` and `manifest.yaml` to edit.

This script validates:

- `manifest.yaml` exists and has the required fields
- `agent.py` defines an `Agent` subclass
- `daily_forecast()` returns native SDK objects

## 3. Edit the two files that matter

- `manifest.yaml`: name the agent, choose metrics, describe the lens
- `agent.py`: implement the forecasting logic

## 4. Prepare the submission

```bash
./tools/prepare_submission.sh
```

If you want a different starting point, copy one of the other example folders
instead of `01-minimal`.

If you want the SDK importable outside the helper scripts, install it with:

```bash
python3 -m pip install -e ./sdk
```
