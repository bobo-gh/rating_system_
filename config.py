import os

class Config:
    # 数据库配置
    MYSQL_HOST = os.getenv('MYSQL_HOST', 'localhost')
    MYSQL_PORT = int(os.getenv('MYSQL_PORT', 3306))
    MYSQL_USER = os.getenv('MYSQL_USER', 'rating_user')  # 默认使用 rating_user
    MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD', 'rating123456')  # 使用正确的密码
    MYSQL_DATABASE = os.getenv('MYSQL_DATABASE', 'rating_system')

    # SQLAlchemy配置
    SQLALCHEMY_DATABASE_URI = f'mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # JWT配置
    JWT_SECRET_KEY = os.getenv('JWT_SECRET', 'your-jwt-secret')
    
    # 其他配置
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key')
