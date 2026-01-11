from sqlalchemy import func, and_, or_, not_, case, select
from sqlalchemy.orm import aliased
from models import WarehousePriority, ProductPrice, WarehouseProduct, DepartmentProduct, Product, Department, Store, Employee, TradingBase, StoreClass

def execute_queries(session):
    print("=" * 80)
    print("ЗАПРОСЫ К БАЗЕ ДАННЫХ УНИВЕРСИТЕТСКОГО МАГАЗИНА")
    print("=" * 80)
    
    # 1.1 Какие товары имеются в магазине?
    print("\n1.1 ТОВАРЫ В МАГАЗИНЕ 'Супермаркет \"Восток\"' (ID=1):")
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
    .filter(Store.store_id == 1)
    .order_by(Department.name, Product.name)
    .all())
    
    for product in store_products:
        print(f"Отдел: {product.department_name:20} Товар: {product.product_name:25} "
              f"Кол-во: {product.quantity:3} Цена: {float(product.current_price):8.2f} "
              f"Сумма: {float(product.total_value):10.2f}")
    
    # 1.2 Какие товары имеются на базе?
    print("\n1.2 ТОВАРЫ НА ТОРГОВОЙ БАЗЕ 'Южный распределительный центр' (ID=2):")
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
    .filter(TradingBase.trading_base_id == 2)
    .filter(WarehouseProduct.count > 0)
    .order_by(Product.name)
    .all())
    
    for product in base_products:
        print(f"Товар: {product.product_name:25} Кол-во: {product.available_quantity:4} "
              f"Цена: {float(product.base_price):8.2f} Сумма: {float(product.total_value):12.2f}")
    
    # 2. Какие отсутствующие товары может заказать магазин на базе?
    print("\n2. ОТСУТСТВУЮЩИЕ ТОВАРЫ ДЛЯ ЗАКАЗА МАГАЗИНОМ 'Супермаркет \"Восток\"' (ID=1):")
    print("-" * 60)
    
    # Подзапрос для товаров с нулевым количеством в магазине
    zero_products_subquery = select(DepartmentProduct.article).\
        join(Department, DepartmentProduct.department_id == Department.department_id).\
        where(and_(
            Department.store_id == 1,
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
    .join(Store, Store.store_id == 1)
    .join(WarehousePriority, and_(
        WarehousePriority.store_id == Store.store_id,
        WarehousePriority.article == Product.article,
        WarehousePriority.trading_base_id == TradingBase.trading_base_id
    ))
    .filter(Product.article.in_(zero_products_subquery))
    .filter(WarehouseProduct.count >= 1)
    .order_by(Product.name, WarehousePriority.priority)
    .all())
    
    for product in orderable_products:
        print(f"Товар: {product.product_name:25} База: {product.trading_base:30} "
              f"Доступно: {product.available_quantity:3} Цена: {float(product.base_price):8.2f} "
              f"Приоритет: {product.priority}")
    
    # 2.доп Какие отсутствующие товары может заказать магазин на базе (в том числе, которых не было, но для которых есть приоритет)?
    print("\n2.доп ОТСУТСТВУЮЩИЕ ТОВАРЫ ДЛЯ ЗАКАЗА МАГАЗИНОМ (включая новые товары с приоритетами) 'Супермаркет \"Восток\"' (ID=1):")
    print("-" * 60)
    
    # Подзапрос для товаров, которые есть в магазине
    store_products_subquery = select(DepartmentProduct.article).\
        join(Department, DepartmentProduct.department_id == Department.department_id).\
        where(Department.store_id == 1)
    
    # Подзапрос для товаров с нулевым количеством
    zero_count_subquery = select(DepartmentProduct.article).\
        join(Department, DepartmentProduct.department_id == Department.department_id).\
        where(and_(
            Department.store_id == 1,
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
    .join(Store, Store.store_id == 1)
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
    .all())
    
    if extended_orderable_products:
        for product in extended_orderable_products:
            status_text = "ЗАКОНЧИЛСЯ" if product.status == 'ЗАКОНЧИЛСЯ' else "НОВЫЙ ТОВАР (может быть добавлен)"
            print(f"Товар: {product.product_name:25} Статус: {status_text:25} "
                  f"База: {product.trading_base:25} Приоритет: {product.priority}")
    else:
        print("Нет товаров для заказа")

    # 3. Какие товары, и в каком количестве имеются в отделе магазина?
    print("\n3. ТОВАРЫ В ОТДЕЛЕ 'Молочный отдел' (ID=1):")
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
    .filter(Department.department_id == 1)
    .order_by(Product.name)
    .all())
    
    for product in department_products:
        print(f"Магазин: {product.store_name:25} Отдел: {product.department_name:20} "
              f"Товар: {product.product_name:25} Кол-во: {product.quantity}")
    
    # 4. Список заведующих отделами магазина
    print("\n4. ЗАВЕДУЮЩИЕ ОТДЕЛАМИ МАГАЗИНА 'Супермаркет \"Восток\"' (ID=1):")
    print("-" * 60)
    
    department_managers = (session.query(
        Store.name.label('store_name'),
        Department.name.label('department_name'),
        func.concat(Employee.first_name, ' ', Employee.last_name).label('manager_name')
    )
    .select_from(Store)
    .join(Department, Store.store_id == Department.store_id)
    .join(Employee, Department.manager_id == Employee.employee_id)
    .filter(Store.store_id == 1)
    .order_by(Department.name)
    .all())
    
    for manager in department_managers:
        print(f"Отдел: {manager.department_name:20} Заведующий: {manager.manager_name}")
    
    # 5. Суммарная стоимость товара в каждом отделе
    print("\n5. СУММАРНАЯ СТОИМОСТЬ ТОВАРОВ ПО ОТДЕЛАМ:")
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
    .all())
    
    for dept in department_values:
        print(f"Магазин: {dept.store_name:25} Отдел: {dept.department_name:20} "
              f"Сумма: {float(dept.total_value):12.2f}")
    
    # 6. На каких базах, и в каких количествах есть товар нужного наименования?
    print("\n6. ПОИСК ТОВАРА 'Молоко' ПО БАЗАМ:")
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
    .filter(Product.name.ilike('%молоко%'))
    .order_by(WarehouseProduct.count.desc())
    .all())
    
    for product in search_products:
        print(f"Товар: {product.product_name:25} База: {product.trading_base:35} "
              f"Кол-во: {product.available_quantity:4} Цена: {float(product.price_per_unit):8.2f}")
