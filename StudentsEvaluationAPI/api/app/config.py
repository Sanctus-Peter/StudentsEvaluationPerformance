from pydantic import BaseSettings


class Settings(BaseSettings):
    db_hostname: str
    db_port: str
    db_password: str
    db_username: str
    db_name: str
    secret_key: str
    algorithm: str
    access_tok_expire_minutes: int
    cloudinary_cloud_name: str
    cloudinary_api_key: str
    cloudinary_api_secret: str

    class Config:
        env_file = ".env"


settings = Settings()
