from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    kilo_api_key: str
    kilo_model: str = "stepfun/step-3.7-flash:free"

    class Config:
        env_file = ".env"


settings = Settings()