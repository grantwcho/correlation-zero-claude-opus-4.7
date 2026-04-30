from correlation_zero import Agent, CI, Prediction


class DataDrivenAgent(Agent):
    AGENT_ID = "example-data-driven-001"

    def collect_signals(self) -> list[float]:
        return [40.9, 41.4, 42.0]

    def daily_forecast(self, metrics: list[str]) -> list[Prediction]:
        signals = self.collect_signals()
        point_estimate = round(sum(signals) / len(signals), 1)
        return [
            Prediction(
                metric_id=metrics[0],
                point_estimate=point_estimate,
                unit="USD_billions",
                confidence_intervals=[CI(level=0.5, low=40.5, high=42.1)],
                evidence_refs=["source_a", "source_b", "source_c"],
                reasoning_summary="Forecast derived from an aggregate of multiple source snapshots.",
            )
        ]

