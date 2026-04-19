import os
from pathlib import Path
from urllib.parse import quote_plus

# This file defines the global configuration of the GoGoJob application,
# including secret keys, database connections, and local data paths.
# During development, we used Gemini as a vibe-coding assistant to help us
# understand how environment variables and configuration classes are usually
# organized in a Flask project.
#
# One practical challenge we encountered was setting up MySQL locally.
# Installing and configuring MySQL turned out to be a real challenge for
# almost every team member (honestly, a lot harder than expected 😅).
# Therefore, we intentionally kept some AI-generated Chinese comments
# in this file to help us quickly understand what each field means,
# how it should be modified, and how to make the application run correctly
# on our own local machines.

BASE_DIR = Path(__file__).resolve().parent.parent


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "gogojob-secret-key")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    RAW_CSV_PATH = os.getenv("RAW_CSV_PATH", str(BASE_DIR / "clean_data" / "all_jobs_cleaned.csv"))
    # ⚠️  本地开发必看：以下配置请修改为你自己本地的MySQL信息
    # ==============================================
    # MySQL服务地址，本地开发默认127.0.0.1，无需修改
    MYSQL_HOST = os.getenv("MYSQL_HOST", "127.0.0.1")
    # MySQL端口号，默认安装的MySQL是3306，如果你本地改了端口，改成自己的
    MYSQL_PORT = int(os.getenv("MYSQL_PORT", 3306))
    # MySQL用户名，默认是root，如果你创建了其他用户，改成自己的
    MYSQL_USER = os.getenv("MYSQL_USER", "root")
    # MySQL密码，改成你自己本地root用户的密码
    MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "@Aa488429581")
    # MySQL数据库名，和你下面创建的数据库名保持一致，默认gogojob
    MYSQL_DB = os.getenv("MYSQL_DB", "gogojob")

    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URI",
        f"mysql+pymysql://{MYSQL_USER}:{quote_plus(MYSQL_PASSWORD)}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}?charset=utf8mb4",
    )
