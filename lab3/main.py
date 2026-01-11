from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base
from populate_data import populate_test_data
from queries import execute_queries
import os

def main():
    # Параметры подключения к PostgreSQL
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
    
    # Создание таблиц
    print("Создание таблиц в PostgreSQL...")
    Base.metadata.create_all(engine)
    
    # Создание сессии
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        # Заполнение тестовыми данными
        print("Заполнение базы данных тестовыми данными...")
        populate_test_data(session)
        
        # Выполнение запросов
        execute_queries(session)
        
    except Exception as e:
        print(f"Произошла ошибка: {e}")
        session.rollback()
    finally:
        session.close()

if __name__ == "__main__":
    main()
