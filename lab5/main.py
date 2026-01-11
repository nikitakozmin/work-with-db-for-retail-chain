from db import engine
from models import Base
from app import create_app
from populate_data import populate_test_data
from db import SessionLocal

def main():
    print("Создание отсутствующих таблиц в PostgreSQL...")
    Base.metadata.create_all(engine)

    print("Заполнение базы данных тестовыми значениями...")
    populate_test_data(SessionLocal())

    app = create_app()
    app.run(
        host="10.10.0.105",
        port=8000,
        debug=True
    )

if __name__ == "__main__":
    main()
