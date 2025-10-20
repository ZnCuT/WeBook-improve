import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # 数据库配置 - 支持SQLite和MySQL
    USE_SQLITE = os.getenv('USE_SQLITE', 'true').lower() == 'true'
    
    if USE_SQLITE:
        # SQLite配置（开发环境推荐）
        SQLALCHEMY_DATABASE_URI = 'sqlite:///webook.db'
    else:
        # MySQL配置
        DB_USER = os.getenv('DB_USER', 'root')
        DB_PASSWORD = os.getenv('DB_PASSWORD', '123456')
        DB_HOST = os.getenv('DB_HOST', '127.0.0.1')
        DB_PORT = os.getenv('DB_PORT', '3306')
        DB_NAME = os.getenv('DB_NAME', 'webook_db')
        SQLALCHEMY_DATABASE_URI = f'mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset=utf8mb4'
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # 安全密钥（固定值，避免每次重启变化）
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-please-change-in-production')
    
    # 文件上传配置
    UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', 'uploads')
    MAX_CONTENT_LENGTH = int(os.getenv('MAX_CONTENT_LENGTH', 16 * 1024 * 1024))  # 16MB
    
    # 语义检索配置
    SEMANTIC_MODEL = os.getenv('SEMANTIC_MODEL', 'paraphrase-multilingual-MiniLM-L12-v2')
    FAISS_INDEX_PATH = os.getenv('FAISS_INDEX_PATH', 'data/faiss_index.bin')
    VECTOR_DIM = int(os.getenv('VECTOR_DIM', 384))