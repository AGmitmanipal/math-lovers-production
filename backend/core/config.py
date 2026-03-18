from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    REFRESH_TOKEN_EXPIRE_DAYS: int

    DATABASE_URL: str

    COOKIE_SECURE: bool = False 
    COOKIE_HTTPONLY: bool = True
    COOKIE_SAMESITE: str = "lax"

    class Config:
        env_file = ".env"


settings = Settings()