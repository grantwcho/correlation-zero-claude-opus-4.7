from correlation_zero import Agent, CI, Prediction


class MinimalAgent(Agent):
    AGENT_ID = "example-minimal-001"

    def daily_forecast(self, metrics: list[str]) -> list[Prediction]:
        return [
            Prediction(
                metric_id=metrics[0],
                point_estimate=41.0,
                unit="USD_billions",
                confidence_intervals=[CI(level=0.5, low=40.2, high=41.8)],
                evidence_refs=["example_source"],
                reasoning_summary="Minimal hard-coded example that demonstrates the contract.",
            )
        ]

