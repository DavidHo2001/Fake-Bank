from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str
    jwt_secret: str
    model_config = SettingsConfigDict(env_file=".env")
    embedding_model_name: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"


settings = Settings()
