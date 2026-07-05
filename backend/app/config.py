import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    MONGO_URI: str = os.getenv("MONGO_URI", "")
    DB_NAME: str = os.getenv("DB_NAME", "fraud_detection")
    API_KEY: str = os.getenv("API_KEY", "")

    def __init__(self):
        # Fail loudly at startup, not silently at request-time
        missing = []
        if not self.MONGO_URI:
            missing.append("MONGO_URI")
        if not self.API_KEY:
            missing.append("API_KEY")
        if missing:
            raise RuntimeError(
                f"Missing required environment variables: {', '.join(missing)}. "
                f"Check that backend/.env exists and is loaded correctly."
            )


settings = Settings()