from pydantic_settings import BaseSettings


class SchedulerSettings(BaseSettings):
    """Scheduler configuration settings."""
    
    fetch_interval_cron: str = "* * * * *"  # Каждую минуту (для теста)
    cryptocurrencies: list[str] = ["bitcoin", "ethereum", "cardano", "solana"]
    
    class Config:
        env_prefix = "SCHEDULER_"
        env_file = ".env"


scheduler_settings = SchedulerSettings()
