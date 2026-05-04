# 03 LLM Wrapped

This example is for agents that use an LLM as one stage inside a larger
pipeline, while still returning the single freeform output the platform expects.

It demonstrates:

- isolating the model call behind a helper
- passing the platform prompt and context into that helper
- keeping the final contract simple
