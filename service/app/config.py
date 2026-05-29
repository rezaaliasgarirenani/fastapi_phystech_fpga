"""Application configuration loaded from environment variables."""

from os import getenv


DATABASE_URL = getenv("DATABASE_URL", "sqlite:///./fpga_selection.db")
SECRET_KEY = getenv("SECRET_KEY", "change-this-development-secret-key-for-local-course-demo")
ALGORITHM = getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
