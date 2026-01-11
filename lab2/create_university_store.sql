-- Таблица классов магазинов
CREATE TABLE store_class (
    store_class_id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    description TEXT
);

-- Таблица торговых баз
CREATE TABLE trading_base (
    trading_base_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT
);

-- Таблица сотрудников
CREATE TABLE employee (
    employee_id SERIAL PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL
);

-- Таблица магазинов
CREATE TABLE store (
    store_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    store_class_id INTEGER REFERENCES store_class(store_class_id),
    director_id INTEGER REFERENCES employee(employee_id)
);

-- Таблица отделов
CREATE TABLE department (
    department_id SERIAL PRIMARY KEY,
    store_id INTEGER REFERENCES store(store_id),
    manager_id INTEGER REFERENCES employee(employee_id),
    name VARCHAR(100) NOT NULL
);

-- Таблица товаров
CREATE TABLE product (
    article SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    sort VARCHAR(50)
);

-- Таблица товаров в отделах
CREATE TABLE department_product (
    department_id INTEGER REFERENCES department(department_id),
    article INTEGER REFERENCES product(article),
    count INTEGER NOT NULL DEFAULT 0,
    PRIMARY KEY (department_id, article)
);

-- Таблица товаров на складах баз
CREATE TABLE warehouse_product (
    trading_base_id INTEGER REFERENCES trading_base(trading_base_id),
    article INTEGER REFERENCES product(article),
    count INTEGER NOT NULL DEFAULT 0,
    price DECIMAL(10,2) NOT NULL,
    PRIMARY KEY (trading_base_id, article)
);

-- Таблица цен товаров по классам магазинов
CREATE TABLE product_price (
    store_class_id INTEGER REFERENCES store_class(store_class_id),
    article INTEGER REFERENCES product(article),
    price DECIMAL(10,2) NOT NULL,
    PRIMARY KEY (store_class_id, article)
);

-- Таблица приоритетов поставок
CREATE TABLE warehouse_priority (
    article INTEGER REFERENCES product(article),
    store_id INTEGER REFERENCES store(store_id),
	trading_base_id INTEGER REFERENCES trading_base(trading_base_id),
    priority INTEGER NOT NULL DEFAULT 5,
    PRIMARY KEY (article, store_id, trading_base_id)
);
