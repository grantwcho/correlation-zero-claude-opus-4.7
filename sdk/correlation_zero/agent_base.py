from .schemas import ResponseFormat


class Agent:
    AGENT_ID = "replace-me"
    SUPPORTED_FORMATS = [ResponseFormat.DAILY_FORECAST.value]

    def daily_forecast(self, metrics: list[str]):
        raise NotImplementedError("Implement daily_forecast() in your agent.")

    def scenario(self):
        raise NotImplementedError("Optional method for scenario responses.")

    def brief(self):
        raise NotImplementedError("Optional method for brief responses.")

    def freeform(self):
        raise NotImplementedError("Optional method for freeform responses.")

