from sqlalchemy import func, and_, or_, not_, case, select, text
from sqlalchemy.orm import aliased
from models import WarehousePriority, ProductPrice, WarehouseProduct, DepartmentProduct, Product, Department, Store, Employee, TradingBase, StoreClass
import time
    
def execute_queries(session, show_output=True):
    print("=" * 80)
    print("ЗАПРОСЫ К БАЗЕ ДАННЫХ УНИВЕРСИТЕТСКОГО МАГАЗИНА")
    print("=" * 80)

    log = {}
    
    # Выполнение всех запросов
    for query_func in queries:
        log[query_func.__name__] = str(query_func(session, show_output=show_output))
    
    return log

def query_1_1_store_products(session, store_id=1, show_output=True):
    """1.1 Какие товары имеются в магазине?"""
    start_time = time.time()
    
    if show_output:
        print(f"\n1.1 ТОВАРЫ В МАГАЗИНЕ ID={store_id}:")
        print("-" * 60)
    
    store_products = (session.query(
        Store.name.label('store_name'),
        Department.name.label('department_name'),
        Product.article,
        Product.name.label('product_name'),
        Product.sort.label('product_sort'),
        DepartmentProduct.count.label('quantity'),
        ProductPrice.price.label('current_price'),
        (DepartmentProduct.count * ProductPrice.price).label('total_value')
    )
    .select_from(Store)
    .join(Department, Store.store_id == Department.store_id)
    .join(DepartmentProduct, Department.department_id == DepartmentProduct.department_id)
    .join(Product, DepartmentProduct.article == Product.article)
    .join(ProductPrice, and_(
        Product.article == ProductPrice.article,
        Store.store_class_id == ProductPrice.store_class_id
    ))
    .filter(Store.store_id == store_id)
    .order_by(Department.name, Product.name)
    .limit(100)
    .all())
    
    end_time = time.time()
    execution_time = end_time - start_time
    
    if show_output:
        for product in store_products:
            print(f"Отдел: {product.department_name:20} Товар: {product.product_name:25} "
                  f"Кол-во: {product.quantity:3} Цена: {float(product.current_price):8.2f} "
                  f"Сумма: {float(product.total_value):10.2f}")
    
    print(f"Запрос 1.1 выполнен за {execution_time:.4f} секунд, обработано {len(store_products)} записей")
    return store_products, execution_time

def query_1_2_base_products(session, base_id=2, show_output=True):
    """1.2 Какие товары имеются на базе?"""
    start_time = time.time()
    
    if show_output:
        print(f"\n1.2 ТОВАРЫ НА ТОРГОВОЙ БАЗЕ ID={base_id}:")
        print("-" * 60)
    
    base_products = (session.query(
        TradingBase.name.label('trading_base_name'),
        Product.article,
        Product.name.label('product_name'),
        Product.sort.label('product_sort'),
        WarehouseProduct.count.label('available_quantity'),
        WarehouseProduct.price.label('base_price'),
        (WarehouseProduct.count * WarehouseProduct.price).label('total_value')
    )
    .select_from(TradingBase)
    .join(WarehouseProduct, TradingBase.trading_base_id == WarehouseProduct.trading_base_id)
    .join(Product, WarehouseProduct.article == Product.article)
    .filter(TradingBase.trading_base_id == base_id)
    .filter(WarehouseProduct.count > 0)
    .order_by(Product.name)
    .limit(100)
    .all())
    
    end_time = time.time()
    execution_time = end_time - start_time
    
    if show_output:
        for product in base_products:
            print(f"Товар: {product.product_name:25} Кол-во: {product.available_quantity:4} "
                  f"Цена: {float(product.base_price):8.2f} Сумма: {float(product.total_value):12.2f}")
    
    print(f"Запрос 1.2 выполнен за {execution_time:.4f} секунд, обработано {len(base_products)} записей")
    return base_products, execution_time

def query_2_1_orderable_products(session, store_id=1, show_output=True):
    """2. Какие отсутствующие товары может заказать магазин на базе?"""
    start_time = time.time()
    
    if show_output:
        print(f"\n2. ОТСУТСТВУЮЩИЕ ТОВАРЫ ДЛЯ ЗАКАЗА МАГАЗИНОМ ID={store_id}:")
        print("-" * 60)
    
    # Подзапрос для товаров с нулевым количеством в магазине
    zero_products_subquery = select(DepartmentProduct.article).\
        join(Department, DepartmentProduct.department_id == Department.department_id).\
        where(and_(
            Department.store_id == store_id,
            DepartmentProduct.count == 0
        )).\
        scalar_subquery()
    
    orderable_products = (session.query(
        Store.name.label('store_name'),
        Product.name.label('product_name'),
        TradingBase.name.label('trading_base'),
        WarehouseProduct.count.label('available_quantity'),
        WarehouseProduct.price.label('base_price'),
        WarehousePriority.priority
    )
    .select_from(Product)
    .join(WarehouseProduct, Product.article == WarehouseProduct.article)
    .join(TradingBase, WarehouseProduct.trading_base_id == TradingBase.trading_base_id)
    .join(Store, Store.store_id == store_id)
    .join(WarehousePriority, and_(
        WarehousePriority.store_id == Store.store_id,
        WarehousePriority.article == Product.article,
        WarehousePriority.trading_base_id == TradingBase.trading_base_id
    ))
    .filter(Product.article.in_(zero_products_subquery))
    .filter(WarehouseProduct.count >= 1)
    .order_by(Product.name, WarehousePriority.priority)
    .limit(100)
    .all())
    
    end_time = time.time()
    execution_time = end_time - start_time
    
    if show_output:
        for product in orderable_products:
            print(f"Товар: {product.product_name:25} База: {product.trading_base:30} "
                  f"Доступно: {product.available_quantity:3} Цена: {float(product.base_price):8.2f} "
                  f"Приоритет: {product.priority}")
    
    print(f"Запрос 2 выполнен за {execution_time:.4f} секунд, обработано {len(orderable_products)} записей")
    return orderable_products, execution_time

def query_2_2_extended_orderable_products(session, store_id=1, show_output=True):
    """2.2 Какие отсутствующие товары может заказать магазин на базе (включая новые товары)?"""
    start_time = time.time()
    
    if show_output:
        print(f"\n2.2 ОТСУТСТВУЮЩИЕ ТОВАРЫ ДЛЯ ЗАКАЗА МАГАЗИНОМ ID={store_id} (включая новые товары):")
        print("-" * 60)
    
    # Подзапрос для товаров, которые есть в магазине
    store_products_subquery = select(DepartmentProduct.article).\
        join(Department, DepartmentProduct.department_id == Department.department_id).\
        where(Department.store_id == store_id)
    
    # Подзапрос для товаров с нулевым количеством
    zero_count_subquery = select(DepartmentProduct.article).\
        join(Department, DepartmentProduct.department_id == Department.department_id).\
        where(and_(
            Department.store_id == store_id,
            DepartmentProduct.count == 0
        ))
    
    extended_orderable_products = (session.query(
        Store.name.label('store_name'),
        Product.name.label('product_name'),
        TradingBase.name.label('trading_base'),
        WarehouseProduct.count.label('available_quantity'),
        WarehouseProduct.price.label('base_price'),
        WarehousePriority.priority,
        case(
            (Product.article.in_(zero_count_subquery), 'ЗАКОНЧИЛСЯ'),
            (not_(Product.article.in_(store_products_subquery)), 'НОВЫЙ ТОВАР'),
            else_='ДРУГОЙ'
        ).label('status')
    )
    .select_from(Product)
    .join(WarehouseProduct, Product.article == WarehouseProduct.article)
    .join(TradingBase, WarehouseProduct.trading_base_id == TradingBase.trading_base_id)
    .join(Store, Store.store_id == store_id)
    .join(WarehousePriority, and_(
        WarehousePriority.store_id == Store.store_id,
        WarehousePriority.article == Product.article,
        WarehousePriority.trading_base_id == TradingBase.trading_base_id
    ))
    .filter(or_(
        Product.article.in_(zero_count_subquery),
        not_(Product.article.in_(store_products_subquery))
    ))
    .filter(WarehouseProduct.count >= 0)
    .order_by(Product.name, WarehousePriority.priority)
    .limit(100)
    .all())
    
    end_time = time.time()
    execution_time = end_time - start_time
    
    if show_output:
        if extended_orderable_products:
            for product in extended_orderable_products:
                status_text = "ЗАКОНЧИЛСЯ" if product.status == 'ЗАКОНЧИЛСЯ' else "НОВЫЙ ТОВАР (может быть добавлен)"
                print(f"Товар: {product.product_name:25} Статус: {status_text:25} "
                      f"База: {product.trading_base:25} Приоритет: {product.priority}")
        else:
            print("Нет товаров для заказа")
    
    print(f"Запрос 2.2 выполнен за {execution_time:.4f} секунд, обработано {len(extended_orderable_products)} записей")
    return extended_orderable_products, execution_time

def query_3_department_products(session, department_id=1, store_id=1, show_output=True):
    """3. Какие товары, и в каком количестве имеются в отделе магазина?"""
    start_time = time.time()
    
    if show_output:
        print(f"\n3. ТОВАРЫ В ОТДЕЛЕ ID={department_id} МАГАЗИНА ID={store_id}:")
        print("-" * 60)
    
    department_products = (session.query(
        Store.name.label('store_name'),
        Department.name.label('department_name'),
        Product.name.label('product_name'),
        DepartmentProduct.count.label('quantity')
    )
    .select_from(Store)
    .join(Department, Store.store_id == Department.store_id)
    .join(DepartmentProduct, Department.department_id == DepartmentProduct.department_id)
    .join(Product, DepartmentProduct.article == Product.article)
    .filter(Department.department_id == department_id)
    .order_by(Product.name)
    .limit(100)
    .all())
    
    end_time = time.time()
    execution_time = end_time - start_time
    
    if show_output:
        for product in department_products:
            print(f"Магазин: {product.store_name:25} Отдел: {product.department_name:20} "
                  f"Товар: {product.product_name:25} Кол-во: {product.quantity}")
    
    print(f"Запрос 3 выполнен за {execution_time:.4f} секунд, обработано {len(department_products)} записей")
    return department_products, execution_time

def query_4_department_managers(session, store_id=1, show_output=True):
    """4. Список заведующих отделами магазина"""
    start_time = time.time()
    
    if show_output:
        print(f"\n4. ЗАВЕДУЮЩИЕ ОТДЕЛАМИ МАГАЗИНА ID={store_id}:")
        print("-" * 60)
    
    department_managers = (session.query(
        Store.name.label('store_name'),
        Department.name.label('department_name'),
        func.concat(Employee.first_name, ' ', Employee.last_name).label('manager_name')
    )
    .select_from(Store)
    .join(Department, Store.store_id == Department.store_id)
    .join(Employee, Department.manager_id == Employee.employee_id)
    .filter(Store.store_id == store_id)
    .order_by(Department.name)
    .limit(100)
    .all())
    
    end_time = time.time()
    execution_time = end_time - start_time
    
    if show_output:
        for manager in department_managers:
            print(f"Отдел: {manager.department_name:20} Заведующий: {manager.manager_name}")
    
    print(f"Запрос 4 выполнен за {execution_time:.4f} секунд, обработано {len(department_managers)} записей")
    return department_managers, execution_time

def query_5_department_values(session, show_output=True):
    """5. Суммарная стоимость товара в каждом отделе"""
    start_time = time.time()
    
    if show_output:
        print(f"\n5. СУММАРНАЯ СТОИМОСТЬ ТОВАРОВ ПО ОТДЕЛАМ:")
        print("-" * 60)
    
    department_values = (session.query(
        Store.name.label('store_name'),
        Department.name.label('department_name'),
        func.sum(DepartmentProduct.count * ProductPrice.price).label('total_value')
    )
    .select_from(Store)
    .join(Department, Store.store_id == Department.store_id)
    .join(DepartmentProduct, Department.department_id == DepartmentProduct.department_id)
    .join(ProductPrice, and_(
        DepartmentProduct.article == ProductPrice.article,
        Store.store_class_id == ProductPrice.store_class_id
    ))
    .group_by(Store.name, Department.name)
    .order_by(func.sum(DepartmentProduct.count * ProductPrice.price).desc())
    .limit(100)
    .all())
    
    end_time = time.time()
    execution_time = end_time - start_time
    
    if show_output:
        for dept in department_values:
            print(f"Магазин: {dept.store_name:25} Отдел: {dept.department_name:20} "
                  f"Сумма: {float(dept.total_value):12.2f}")
    
    print(f"Запрос 5 выполнен за {execution_time:.4f} секунд, обработано {len(department_values)} записей")
    return department_values, execution_time

def query_6_product_search(session, product_name='Молоко', show_output=True):
    """6. На каких базах, и в каких количествах есть товар нужного наименования?"""
    start_time = time.time()
    
    if show_output:
        print(f"\n6. ПОИСК ТОВАРА '{product_name}' ПО БАЗАМ:")
        print("-" * 60)
    
    search_products = (session.query(
        Product.name.label('product_name'),
        TradingBase.name.label('trading_base'),
        TradingBase.description.label('base_description'),
        WarehouseProduct.count.label('available_quantity'),
        WarehouseProduct.price.label('price_per_unit')
    )
    .select_from(Product)
    .join(WarehouseProduct, Product.article == WarehouseProduct.article)
    .join(TradingBase, WarehouseProduct.trading_base_id == TradingBase.trading_base_id)
    .filter(Product.name.ilike(f'%{product_name}%'))
    .order_by(WarehouseProduct.count.desc())
    .limit(100)
    .all())
    
    end_time = time.time()
    execution_time = end_time - start_time
    
    if show_output:
        for product in search_products:
            print(f"Товар: {product.product_name:25} База: {product.trading_base:35} "
                  f"Кол-во: {product.available_quantity:4} Цена: {float(product.price_per_unit):8.2f}")
    
    print(f"Запрос 6 выполнен за {execution_time:.4f} секунд, обработано {len(search_products)} записей")
    return search_products, execution_time

queries = [
    query_1_1_store_products,
    query_1_2_base_products,
    query_2_1_orderable_products,
    query_2_2_extended_orderable_products,
    query_3_department_products,
    query_4_department_managers,
    query_5_department_values,
    query_6_product_search
]

# -- 6. На каких базах, и в каких количествах есть товар нужного наименования?
def bad_query_like(session, value):
    sql_query = f"""
    SELECT 
        p.name as product_name,
        tb.name as trading_base,
        tb.description as base_description,
        wp.count as available_quantity,
        wp.price as price_per_unit
    FROM product p
    JOIN warehouse_product wp ON p.article = wp.article
    JOIN trading_base tb ON wp.trading_base_id = tb.trading_base_id
    WHERE p.name ILIKE '%{value}%';
    """
    # SQL-инъекция:
    # %'; SELECT * FROM product --
    print(sql_query)
    return session.execute(text(sql_query)).all()

# -- 6. На каких базах, и в каких количествах есть товар нужного наименования?
def bad_query_id(session, value):
    sql_query = f"""
    SELECT 
        p.name as product_name,
        tb.name as trading_base,
        tb.description as base_description,
        wp.count as available_quantity,
        wp.price as price_per_unit
    FROM product p
    JOIN warehouse_product wp ON p.article = wp.article
    JOIN trading_base tb ON wp.trading_base_id = tb.trading_base_id
    WHERE p.article = {value};
    """
    # SQL-инъекция:
    # 1; SELECT * FROM product --
    print(sql_query)
    return session.execute(text(sql_query)).all()
