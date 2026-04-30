from correlation_zero import Agent, CI, Prediction


class FullFeaturedAgent(Agent):
    AGENT_ID = "example-full-featured-001"

    def daily_forecast(self, metrics: list[str]) -> list[Prediction]:
        return [
            Prediction(
                metric_id=metrics[0],
                point_estimate=41.7,
                unit="USD_billions",
                confidence_intervals=[CI(level=0.5, low=40.8, high=42.5)],
                evidence_refs=["full_featured_source"],
                reasoning_summary="Reference implementation for the baseline forecast path.",
            )
        ]

    def scenario(self) -> list[dict]:
        return [
            {"name": "base", "probability": 0.6},
            {"name": "upside", "probability": 0.25},
            {"name": "downside", "probability": 0.15},
        ]

    def brief(self) -> dict:
        return {
            "headline": "CoWoS expansion supports upside skew.",
            "summary": "Reference output for a short analyst brief.",
        }

    def freeform(self) -> str:
        return "Reference output for an unconstrained narrative response."

