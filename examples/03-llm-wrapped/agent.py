from correlation_zero import Agent, CI, Prediction


def model_stub(metric_id: str) -> dict:
    return {
        "metric_id": metric_id,
        "point_estimate": 42.1,
        "unit": "USD_billions",
        "reasoning_summary": "Example stub for structured model output.",
    }


class LLMWrappedAgent(Agent):
    AGENT_ID = "example-llm-wrapped-001"

    def daily_forecast(self, metrics: list[str]) -> list[Prediction]:
        predictions: list[Prediction] = []
        for metric_id in metrics:
            raw = model_stub(metric_id)
            predictions.append(
                Prediction(
                    metric_id=raw["metric_id"],
                    point_estimate=raw["point_estimate"],
                    unit=raw["unit"],
                    confidence_intervals=[CI(level=0.5, low=40.7, high=43.4)],
                    evidence_refs=["structured_model_stub"],
                    reasoning_summary=raw["reasoning_summary"],
                )
            )
        return predictions

