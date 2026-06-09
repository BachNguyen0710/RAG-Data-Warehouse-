from pydantic_settings import BaseSettings
from pathlib import Path

class Settings(BaseSettings):
    PROJECT_NAME: str = "RAG data warehouse project"
    SECRET_KEY: str = "change-me"
    UPLOAD_DIR: Path = Path("storage")
    MAX_FILE_SIZE_MB: int = 100


    #SQL server 
    SQL_SERVER: str = "localhost"
    SQL_DATABASE: str = "ragdb"
    SQL_USERNAME: str = "sa"
    SQL_PASSWORD: str = ""
    SQL_DRIVER: str = "ODBC Driver 18 for SQL Server"
    SQL_TRUSTED_CONNECTION: bool = False  # True nếu dùng Windows Auth

    @property
    def DATABASE_URL(self) -> str:
        """Build connection string tự động từ các biến trên."""
        driver = self.SQL_DRIVER.replace(" ", "+")

        if self.SQL_TRUSTED_CONNECTION:
            # Windows Authentication — không cần username/password
            return (
                f"mssql+pyodbc://@{self.SQL_SERVER}/{self.SQL_DATABASE}"
                f"?driver={driver}&TrustServerCertificate=yes"
            )
        # SQL Server Authentication
        return (
            f"mssql+pyodbc://{self.SQL_USERNAME}:{self.SQL_PASSWORD}"
            f"@{self.SQL_SERVER}/{self.SQL_DATABASE}"
            f"?driver={driver}&TrustServerCertificate=yes"
        )

    class Config:
        env_file = ".env"

settings = Settings()