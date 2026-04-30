from correlation_zero import Agent, CI, Prediction


class PredictionOnlyAgent(Agent):
    AGENT_ID = "example-prediction-only-001"

    def project_metric(self, metric_id: str) -> Prediction:
        baselines = {
            "revenue_data_center_q2_fy27": (41.8, "USD_billions"),
            "gross_margin_q2_fy27": (76.2, "percent"),
        }
        point_estimate, unit = baselines[metric_id]
        return Prediction(
            metric_id=metric_id,
            point_estimate=point_estimate,
            unit=unit,
            confidence_intervals=[CI(level=0.5, low=point_estimate - 0.8, high=point_estimate + 0.8)],
            evidence_refs=["model_baseline"],
            reasoning_summary="Purely numeric forecast path with no language-model dependency.",
        )

    def daily_forecast(self, metrics: list[str]) -> list[Prediction]:
        return [self.project_metric(metric_id) for metric_id in metrics]

