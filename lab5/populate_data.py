from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from models import Base, StoreClass, TradingBase, Employee, Store, Department, Product, DepartmentProduct, WarehouseProduct, ProductPrice, WarehousePriority
from faker import Faker
import time
from datetime import datetime


truncate_sql = """
TRUNCATE TABLE
    department_product,
    department,
    warehouse_priority,
    store,
    product_price,
    store_class,
    warehouse_product,
    trading_base,
    employee,
    product
RESTART IDENTITY;
"""


def populate_test_data_faker(session, records_per_table=10, use_truncate=True):
    start_time = time.time()
    fake = Faker('ru_RU')  # Русская локализация
    
    # Очистка существующих данных
    if use_truncate:
        print("Очистка существующих данных...")
        session.execute(text(truncate_sql))
        session.commit()
    
    print(f"Генерация тестовых данных ({records_per_table} записей на таблицу)...")
    
    
    # print("Генерация классов магазинов...")
    store_classes_data = [
        ('Элитный', 'Магазины премиум-класса с широким ассортиментом'),
        ('Стандарт', 'Магазины среднего ценового сегмента'),
        ('Эконом', 'Бюджетные магазины'),
        ('Специализированный', 'Магазины узкой направленности'),
        ('Гипермаркет', 'Крупные торговые центры')
    ]
    
    store_classes = []
    for i in range(min(records_per_table, len(store_classes_data))):
        if i < len(store_classes_data):
            name, description = store_classes_data[i]
        else:
            name = fake.company()
            description = fake.text(max_nb_chars=100)
        
        store_classes.append(StoreClass(
            name=name,
            description=description
        ))
    store_class_ids = [sc.store_class_id for sc in store_classes]
    
    session.add_all(store_classes)
    session.flush()
    print(f"Создано {len(store_classes)} классов магазинов")
    
    
    # print("Генерация торговых баз...")
    trading_bases = []
    for i in range(records_per_table):
        trading_bases.append(TradingBase(
            name=fake.company() + ' ' + fake.random_element(['Центр', 'База', 'Склад', 'Комплекс', 'Хаб']),
            description=fake.text(max_nb_chars=150)
        ))
    
    session.add_all(trading_bases)
    session.flush()
    print(f"Создано {len(trading_bases)} торговых баз")
    
    
    # print("Генерация сотрудников...")
    employees = []
    for i in range(records_per_table * 2):  # Больше сотрудников для менеджеров
        employees.append(Employee(
            first_name=fake.first_name(),
            last_name=fake.last_name()
        ))
    
    session.add_all(employees)
    session.flush()
    print(f"Создано {len(employees)} сотрудников")
    
    
    employee_ids = [e.employee_id for e in employees] # Для магазинов и отделов
    
    
    # print("Генерация магазинов...")
    stores = []
    store_names = ['Супермаркет', 'Гипермаркет', 'Магазин', 'Торговый центр', 'Универмаг', 'Маркет', 'Торговая точка']
    
    for i in range(records_per_table):
        stores.append(Store(
            name=fake.random_element(store_names) + " " + fake.company(),
            description=fake.text(max_nb_chars=20),
            store_class_id=fake.random_element(store_class_ids),
            director_id=fake.random_element(employee_ids)
        ))
    
    session.add_all(stores)
    session.flush()
    print(f"Создано {len(stores)} магазинов")
    

    # print("Генерация отделов...")
    departments = []
    department_names = [
        'Молочный отдел', 'Хлебный отдел', 'Овощной отдел', 'Мясной отдел', 'Бакалея',
        'Гастрономия', 'Кондитерский отдел', 'Бытовая техника', 'Электроника', 'Напитки',
        'Фруктовый отдел', 'Рыбный отдел', 'Колбасный отдел', 'Сыры', 'Замороженные продукты',
        'Хозтовары', 'Косметика', 'Одежда', 'Обувь', 'Аксессуары'
    ]
    store_ids = [s.store_id for s in stores]
    
    # Обязательное количество отделов для каждого магазина
    for s_id in map(lambda store: store.store_id, stores):
        departments.append(Department(
            store_id=s_id,
            manager_id=fake.random_element(employee_ids),
            name=fake.random_element(department_names) + (' ' + fake.word() if fake.boolean() else '')
        ))
    # Дополнительное количество отделов для каждого магазина
    for i in range(records_per_table):
        departments.append(Department(
            store_id=fake.random_element(store_ids),
            manager_id=fake.random_element(employee_ids),
            name=fake.random_element(department_names) + (' ' + fake.word() if fake.boolean() else '')
        ))
    
    session.add_all(departments)
    session.flush()
    print(f"Создано {len(departments)} отделов")
    

    # print("Генерация товаров...")
    products = []
    product_types = {
        'Молочные': ['Молоко', 'Йогурт', 'Сыр', 'Кефир', 'Творог', 'Сметана'],
        'Хлебные': ['Хлеб', 'Булочка', 'Батон', 'Пирог', 'Печенье'],
        'Овощи': ['Картофель', 'Морковь', 'Лук', 'Помидоры', 'Огурцы'],
        'Мясо': ['Курица', 'Говядина', 'Свинина', 'Баранина', 'Колбаса'],
        'Бакалея': ['Рис', 'Гречка', 'Макароны', 'Мука', 'Сахар'],
        'Напитки': ['Сок', 'Вода', 'Лимонад', 'Чай', 'Кофе'],
        'Электроника': ['Телевизор', 'Смартфон', 'Ноутбук', 'Планшет', 'Наушники']
    }
    
    for i in range(records_per_table):
        category = fake.random_element(list(product_types.keys()))
        product_name = fake.random_element(product_types[category])
        
        products.append(Product(
            name=f"{product_name} {fake.word()}",
            sort=fake.random_element(['Премиум', 'Стандарт', 'Эконом'] + (['Высший сорт', 'Первый сорт', 'Отборный'] if category != 'Электроника' else []))
        ))
    
    session.add_all(products)
    session.flush()
    print(f"Создано {len(products)} товаров")
    
        
    # print("Генерация товаров в отделах...")
    department_products = []
    
    # Создаем связи между отделами и товарами
    used_combinations = set()
    for i in range(records_per_table * 5):
        dept = fake.random_element(departments)
        prod = fake.random_element(products)
        
        # Избегаем дубликатов
        combination = (dept.department_id, prod.article)
        if combination not in used_combinations:
            department_products.append(DepartmentProduct(
                department_id=dept.department_id,
                article=prod.article,
                count=fake.random_int(min=0, max=100)
            ))
            used_combinations.add(combination)
    
    session.add_all(department_products)
    session.flush()
    print(f"Создано {len(department_products)} связей товаров с отделами")
        
    
    # print("Генерация товаров на складах...")
    warehouse_products = []
    
    used_combinations = set()
    for i in range(records_per_table * 2):
        base = fake.random_element(trading_bases)
        prod = fake.random_element(products)
        
        combination = (base.trading_base_id, prod.article)
        if combination not in used_combinations:
            warehouse_products.append(WarehouseProduct(
                trading_base_id=base.trading_base_id,
                article=prod.article,
                count=fake.random_int(min=10, max=500),
                price=float(fake.random_int(min=50, max=50000) / 100)  # Цены от 0.50 до 500.00
            ))
            used_combinations.add(combination)
    
    session.add_all(warehouse_products)
    session.flush()
    print(f"Создано {len(warehouse_products)} позиций на складах")
    

    # print("Генерация цен товаров...")
    product_prices = []
    for store_class in store_classes:
        for prod in products:
            base_price = float(fake.random_int(min=100, max=10000) / 100)
            if store_class.name == 'Элитный':
                price = base_price * 1.3  # На 30% дороже
            elif store_class.name == 'Эконом':
                price = base_price * 0.8  # На 20% дешевле
            else:
                price = base_price

            product_prices.append(ProductPrice(
                store_class_id=store_class.store_class_id,
                article=prod.article,
                price=price
            ))
    session.add_all(product_prices)
    session.flush()
    print(f"Создано {len(product_prices)} ценовых позиций")
    

    # print("Генерация приоритетов поставок...")
    warehouse_priorities = []
    
    used_combinations = set()
    for i in range(records_per_table * 2):
        prod = fake.random_element(products)
        store = fake.random_element(stores)
        base = fake.random_element(trading_bases)
        
        combination = (prod.article, store.store_id, base.trading_base_id)
        if combination not in used_combinations:
            warehouse_priorities.append(WarehousePriority(
                article=prod.article,
                store_id=store.store_id,
                trading_base_id=base.trading_base_id,
                priority=fake.random_int(min=1, max=10)
            ))
            used_combinations.add(combination)
    
    session.add_all(warehouse_priorities)
    session.flush()
    print(f"Создано {len(warehouse_priorities)} приоритетов поставок")
    
    # Фиксация изменений
    session.commit()
    
    end_time = time.time()
    execution_time = end_time - start_time
    
    print(f"Время выполнения: {execution_time:.2f} секунд")


def create_indexes(engine):
    print("Создание индексов для улучшения производительности...")
    
    indexes_sql = [
        # 1. Индекс для поиска по названию товара
        "CREATE INDEX IF NOT EXISTS idx_product_name_search ON product (name);",
        
        # 2. Индекс для JOIN между Department и Store
        "CREATE INDEX IF NOT EXISTS idx_department_store_id_fk ON department (store_id);",
        
        # 3. Индексы для сортировки по количеству
        "CREATE INDEX IF NOT EXISTS idx_department_product_count_sort ON department_product (count);",
        "CREATE INDEX IF NOT EXISTS idx_warehouse_product_count_sort ON warehouse_product (count);",
        
        # 4. Индекс для сортировки по приоритетам
        "CREATE INDEX IF NOT EXISTS idx_warehouse_priority_sort ON warehouse_priority (priority);",
        
        # 5. Индексы для сортировки по ценам
        "CREATE INDEX IF NOT EXISTS idx_product_price_sort ON product_price (price);",
        "CREATE INDEX IF NOT EXISTS idx_warehouse_product_price_sort ON warehouse_product (price);",
        
        # 6. Составной индекс для DepartmentProduct
        "CREATE INDEX IF NOT EXISTS idx_department_product_join ON department_product (department_id, article);",
        
        # 7. Составной индекс для WarehouseProduct
        "CREATE INDEX IF NOT EXISTS idx_warehouse_product_join ON warehouse_product (trading_base_id, article);",
        
        # 8. Составной индекс для ProductPrice
        "CREATE INDEX IF NOT EXISTS idx_product_price_join ON product_price (store_class_id, article);",
        
        # 9. Индекс для Employee (поиск по имени)
        "CREATE INDEX IF NOT EXISTS idx_employee_name ON employee (last_name, first_name);",
        
        # 10. Индекс для Store по классу
        "CREATE INDEX IF NOT EXISTS idx_store_class ON store (store_class_id);"
    ]
    
    with engine.connect() as conn:
        for sql in indexes_sql:
            try:
                conn.execute(text(sql))
                conn.commit()
            except Exception as e:
                print(f"Ошибка при создании индекса: {e}")


def drop_indexes(engine):
    print("Удаление индексов...")
    
    drop_sql = [
        "DROP INDEX IF EXISTS idx_product_name_search;",
        "DROP INDEX IF EXISTS idx_department_store_id_fk;",
        "DROP INDEX IF EXISTS idx_department_product_count_sort;",
        "DROP INDEX IF EXISTS idx_warehouse_product_count_sort;",
        "DROP INDEX IF EXISTS idx_warehouse_priority_sort;",
        "DROP INDEX IF EXISTS idx_product_price_sort;",
        "DROP INDEX IF EXISTS idx_warehouse_product_price_sort;",
        "DROP INDEX IF EXISTS idx_department_product_join;",
        "DROP INDEX IF EXISTS idx_warehouse_product_join;",
        "DROP INDEX IF EXISTS idx_product_price_join;",
        "DROP INDEX IF EXISTS idx_employee_name;",
        "DROP INDEX IF EXISTS idx_store_class;"
    ]

    with engine.connect() as conn:
        for sql in drop_sql:
            try:
                conn.execute(text(sql))
                conn.commit()
            except Exception as e:
                print(f"Ошибка при удалении индекса: {e}")
    

def populate_test_data(session):
    # Очистка существующих данных
    session.execute(text(truncate_sql))
    
    # Классы магазинов
    store_classes = [
        StoreClass(name='Элитный', description='Магазины премиум-класса с широким ассортиментом'),
        StoreClass(name='Стандарт', description='Магазины среднего ценового сегмента'),
        StoreClass(name='Эконом', description='Бюджетные магазины'),
        StoreClass(name='Специализированный', description='Магазины узкой направленности'),
        StoreClass(name='Гипермаркет', description='Крупные торговые центры')
    ]
    session.add_all(store_classes)
    session.flush()
    
    # Торговые базы
    trading_bases = [
        TradingBase(name='Центральная база "Северная"', description='Крупнейший распределительный центр в северном регионе'),
        TradingBase(name='Южный распределительный центр', description='Современный логистический комплекс южного направления'),
        TradingBase(name='Западный складской комплекс', description='Складские помещения с системой климат-контроля'),
        TradingBase(name='Восточная база снабжения', description='База снабжения для розничных сетей восточного региона'),
        TradingBase(name='Центральный логистический центр', description='Основной хаб для федеральных сетей')
    ]
    session.add_all(trading_bases)
    session.flush()
    
    # Сотрудники
    employees = [
        Employee(first_name='Иван', last_name='Петров'),
        Employee(first_name='Мария', last_name='Сидорова'),
        Employee(first_name='Алексей', last_name='Козлов'),
        Employee(first_name='Ольга', last_name='Николаева'),
        Employee(first_name='Сергей', last_name='Васильев'),
        Employee(first_name='Елена', last_name='Федорова'),
        Employee(first_name='Дмитрий', last_name='Орлов'),
        Employee(first_name='Анна', last_name='Морозова'),
        Employee(first_name='Павел', last_name='Семенов'),
        Employee(first_name='Ирина', last_name='Волкова')
    ]
    session.add_all(employees)
    session.flush()
    
    # Магазины
    stores = [
        Store(name='Супермаркет "Восток"', description='Крупный супермаркет в центре города', 
              store_class_id=store_classes[1].store_class_id, director_id=employees[0].employee_id),
        Store(name='Гипермаркет "Мега"', description='Торговый центр с полным ассортиментом', 
              store_class_id=store_classes[4].store_class_id, director_id=employees[3].employee_id),
        Store(name='Магазин "Эконом"', description='Бюджетный магазин для ежедневных покупок', 
              store_class_id=store_classes[2].store_class_id, director_id=employees[5].employee_id),
        Store(name='Премиум маркет "Люкс"', description='Магазин премиум-класса', 
              store_class_id=store_classes[0].store_class_id, director_id=employees[8].employee_id),
        Store(name='Спецмагазин "Техника"', description='Специализированный магазин электроники', 
              store_class_id=store_classes[3].store_class_id, director_id=employees[3].employee_id)
    ]
    session.add_all(stores)
    session.flush()
    
    # Отделы
    departments = [
        Department(store_id=stores[0].store_id, manager_id=employees[1].employee_id, name='Молочный отдел'),
        Department(store_id=stores[0].store_id, manager_id=employees[2].employee_id, name='Хлебный отдел'),
        Department(store_id=stores[1].store_id, manager_id=employees[4].employee_id, name='Овощной отдел'),
        Department(store_id=stores[1].store_id, manager_id=employees[6].employee_id, name='Мясной отдел'),
        Department(store_id=stores[2].store_id, manager_id=employees[7].employee_id, name='Бакалея'),
        Department(store_id=stores[3].store_id, manager_id=employees[9].employee_id, name='Гастрономия'),
        Department(store_id=stores[3].store_id, manager_id=employees[1].employee_id, name='Кондитерский отдел'),
        Department(store_id=stores[4].store_id, manager_id=employees[2].employee_id, name='Бытовая техника'),
        Department(store_id=stores[4].store_id, manager_id=employees[4].employee_id, name='Электроника'),
        Department(store_id=stores[0].store_id, manager_id=employees[6].employee_id, name='Напитки')
    ]
    session.add_all(departments)
    session.flush()
    
    # Товары
    products = [
        Product(name='Молоко 2,5%', sort='Пастеризованное'),
        Product(name='Хлеб Бородинский', sort='Ржаной'),
        Product(name='Картофель', sort='Отборный'),
        Product(name='Курица охлажденная', sort='Бройлер'),
        Product(name='Рис круглый', sort='Высший сорт'),
        Product(name='Кофе молотый', sort='Арабика'),
        Product(name='Шоколад горький', sort='Премиум'),
        Product(name='Чай черный', sort='Цейлон'),
        Product(name='Сок яблочный', sort='Осветленный'),
        Product(name='Телевизор LED', sort='Smart TV'),
        Product(name='Смартфон', sort='Флагман'),
        Product(name='Йогурт натуральный', sort='Без добавок'),
        Product(name='Сыр Российский', sort='Полутвердый'),
        Product(name='Колбаса докторская', sort='Вареная'),
        Product(name='Печенье овсяное', sort='С шоколадом')
    ]
    session.add_all(products)
    session.flush()
    
    # Товары в отделах
    department_products = [
        (1, 1, 0), (1, 12, 30), (1, 13, 25),
        (2, 2, 40), (2, 15, 45),
        (3, 3, 100), (3, 5, 60),
        (4, 4, 35), (4, 14, 28),
        (5, 5, 55), (5, 6, 20), (5, 7, 35),
        (6, 7, 15), (6, 8, 25), (6, 13, 18),
        (7, 7, 30), (7, 15, 40),
        (8, 10, 8), (9, 11, 12),
        (10, 1, 25), (10, 9, 35)
    ]
    
    for dept_id, art, cnt in department_products:
        session.add(DepartmentProduct(
            department_id=departments[dept_id-1].department_id,
            article=products[art-1].article,
            count=cnt
        ))
    
    # Товары на складах баз
    warehouse_products = [
        (1, 1, 200, 85.50), (1, 2, 150, 45.00), (1, 3, 500, 35.00),
        (2, 4, 180, 320.00), (2, 5, 300, 95.00), (2, 6, 120, 450.00),
        (3, 7, 90, 180.00), (3, 8, 200, 120.00), (3, 9, 150, 110.00),
        (4, 10, 25, 25000.00), (4, 11, 40, 45000.00),
        (5, 12, 100, 65.00), (5, 13, 80, 580.00), (5, 14, 60, 420.00),
        (1, 15, 120, 85.00), (2, 1, 180, 82.00)
    ]
    
    for base_id, art, cnt, price in warehouse_products:
        session.add(WarehouseProduct(
            trading_base_id=trading_bases[base_id-1].trading_base_id,
            article=products[art-1].article,
            count=cnt,
            price=price
        ))
    
    # Цены товаров по классам магазинов
    product_prices = [
        (1, 1, 120.00), (1, 2, 65.00), (1, 3, 50.00),
        (2, 1, 95.00), (2, 2, 48.00), (2, 3, 38.00),
        (3, 1, 80.00), (3, 2, 40.00), (3, 3, 30.00),
        (1, 7, 250.00), (2, 7, 200.00), (3, 7, 150.00),
        (4, 10, 28000.00), (5, 10, 27000.00)
    ]
    
    for class_id, art, price in product_prices:
        session.add(ProductPrice(
            store_class_id=store_classes[class_id-1].store_class_id,
            article=products[art-1].article,
            price=price
        ))
    
    # Приоритеты поставок
    warehouse_priorities = [
        (1, 1, 1, 1), (1, 2, 1, 2), (1, 3, 1, 1),
        (2, 1, 1, 2), (2, 2, 1, 3), (2, 3, 1, 2),
        (3, 1, 1, 1), (3, 2, 1, 1), (3, 3, 1, 1),
        (10, 4, 4, 1), (10, 5, 4, 1), (11, 5, 4, 1),
        (7, 4, 3, 2), (7, 1, 3, 3),
        (1, 1, 2, 2), (2, 1, 2, 3)
    ]
    
    for art, store_id, base_id, priority in warehouse_priorities:
        session.add(WarehousePriority(
            article=products[art-1].article,
            store_id=stores[store_id-1].store_id,
            trading_base_id=trading_bases[base_id-1].trading_base_id,
            priority=priority
        ))
    
    session.commit()
    print("Тестовые данные успешно добавлены!")
