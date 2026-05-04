# Submission Guide

Before submitting, run:

```bash
./tools/test_agent.sh
./tools/prepare_submission.sh
```

Keep secrets out of the repo. Read API keys and tokens from environment
variables, and document the required variable names in your submission notes.

If your agent needs third-party packages, add the install instructions or package
metadata expected by your deployment path. The local SDK only validates the
platform contract; it does not vendor external dependencies for you.
