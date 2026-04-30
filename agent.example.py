"""Heavily commented reference agent for contributors."""

from correlation_zero import Agent, CI, Prediction


class ExampleAgent(Agent):
    # Keep this in sync with manifest.yaml.
    AGENT_ID = "supply-chain-cowos-001"

    def daily_forecast(self, metrics: list[str]) -> list[Prediction]:
        # In a real agent, this method would fetch data, compute signals,
        # and emit one Prediction per requested metric.
        predictions: list[Prediction] = []

        for metric_id in metrics:
            predictions.append(
                Prediction(
                    metric_id=metric_id,
                    point_estimate=41.2,
                    unit="USD_billions",
                    confidence_intervals=[
                        CI(level=0.5, low=39.8, high=42.6),
                        CI(level=0.8, low=38.1, high=44.3),
                    ],
                    evidence_refs=["tsmc_monthly_release", "trendforce_q2_note"],
                    reasoning_summary=(
                        "CoWoS allocation appears to be expanding faster than the "
                        "street is modeling, which supports upside on data center revenue."
                    ),
                )
            )

        return predictions

