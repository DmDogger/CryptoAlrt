from pydantic_settings import BaseSettings


class SchedulerSettings(BaseSettings):
    """Scheduler configuration settings."""
    
    fetch_interval_cron: str = "30 * * * *" # test cron time for demo coingecko api
    cryptocurrencies: list[str] = ["bitcoin", "ethereum", "cardano", "solana"]
    
    class Config:
        env_prefix = "SCHEDULER_"
        env_file = ".env"


scheduler_settings = SchedulerSettings()
