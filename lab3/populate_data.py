from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from models import Base, StoreClass, TradingBase, Employee, Store, Department, Product, DepartmentProduct, WarehouseProduct, ProductPrice, WarehousePriority

def populate_test_data(session):
    # Очистка существующих данных
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
