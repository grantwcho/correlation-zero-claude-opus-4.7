# 03 LLM Wrapped

This example is for agents that use an LLM as one stage inside a larger
pipeline, while still returning explicit structured outputs.

It demonstrates:

- isolating the model call behind a helper
- converting model output into native SDK objects
- keeping the final contract deterministic

