from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os

db_host = os.getenv('DB_HOST', 'localhost')
db_port = os.getenv('DB_PORT', '5432')
db_name = os.getenv('DB_NAME', 'university_store_database')
db_user = os.getenv('DB_USER', 'postgres')
db_password = os.getenv('DB_PASSWORD', 'postgres')

# Создание подключения к PostgreSQL
database_url = f'postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}'
engine = create_engine(
    database_url,
    echo=False,
)
    
SessionLocal = sessionmaker(bind=engine)
