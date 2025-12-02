from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """애플리케이션 설정"""
    
    # OpenAI
    openai_api_key: str
    
    # API
    api_port: int = 8000
    api_host: str = "0.0.0.0"
    
    # 환경
    environment: str = "development"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# 전역 설정 인스턴스
settings = Settings()
