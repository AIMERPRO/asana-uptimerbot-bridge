import os
from dataclasses import dataclass

from dotenv import load_dotenv

@dataclass(frozen=True)
class Settings:
    load_dotenv()

    config = dict(os.environ)

    uptimerobot_token: str = config.get("UPTIMEROBOT_API_KEY", "")
    default_scheme: str = config.get("DEFAULT_SCHEME", "")
    asana_path_token: str = config.get("ASANA_PATH_TOKEN", "")


settings = Settings()
