from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Database
    DATABASE_HOST: str = "localhost"
    DATABASE_PORT: int = 5432
    DATABASE_NAME: str = "onixlibrary"
    DATABASE_USER: str = "super_user"
    DATABASE_PASSWORD: str = "carimboatrasado"
    
    # API
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Biblioteca Onix"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "API para gerenciamento de biblioteca e empréstimos de livros"
    
    # CORS
    BACKEND_CORS_ORIGINS: list[str] = [
        "http://localhost:3000", 
        "http://localhost:8080"
        "http://localhost:8765"
    ]
    
    @property
    def database_url(self) -> str:
        return f"postgresql://{self.DATABASE_USER}:{self.DATABASE_PASSWORD}@{self.DATABASE_HOST}:{self.DATABASE_PORT}/{self.DATABASE_NAME}"
    
    class Config:
        env_file = ".env"

settings = Settings()
