import os
from pathlib import Path
from urllib.parse import quote_plus

BASE_DIR = Path(__file__).resolve().parent


def get_database_url():
    """Use the MySQL database for this project by default so it matches the existing schema and created database."""
    explicit_database_url = os.environ.get('DATABASE_URL')
    if explicit_database_url:
        return explicit_database_url

    use_mysql_value = os.environ.get('USE_MYSQL')
    if use_mysql_value is None:
        use_mysql = True
    else:
        use_mysql = use_mysql_value.lower() in {'1', 'true', 'yes', 'on'}

    if not use_mysql:
        return f'sqlite:///{BASE_DIR / "placement_training.db"}'

    user = os.environ.get('MYSQL_USER', 'root')
    password = os.environ.get('MYSQL_PASSWORD', 'Priyakumar@27')
    if not password:
        return f'sqlite:///{BASE_DIR / "placement_training.db"}'

    host = os.environ.get('MYSQL_HOST', 'localhost')
    port = os.environ.get('MYSQL_PORT', '3306')
    database = os.environ.get('MYSQL_DATABASE', 'placement_training_system')
    return f'mysql+pymysql://{quote_plus(user)}:{quote_plus(password)}@{host}:{port}/{database}'


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'placement-training-secret-key')
    SQLALCHEMY_DATABASE_URI = get_database_url()
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WTF_CSRF_ENABLED = False
    UPLOAD_FOLDER = BASE_DIR / 'static' / 'uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig,
}