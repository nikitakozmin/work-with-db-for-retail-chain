-- 1.1 Какие товары имеются в магазине?
SELECT 
	s.name as store_name,
    d.name as department_name,
    p.article as article,
    p.name as product_name,
    p.sort as product_sort,
    dp.count as quantity,
    pp.price as current_price,
    (dp.count * pp.price) as total_value
FROM store s
JOIN department d ON s.store_id = d.store_id
JOIN department_product dp ON d.department_id = dp.department_id
JOIN product p ON dp.article = p.article
JOIN product_price pp ON p.article = pp.article AND s.store_class_id = pp.store_class_id
WHERE s.store_id = 1
ORDER BY d.name, p.name;

-- 1.2 Какие товары имеются на базе?
SELECT 
    tb.name as trading_base_name,
    p.article as article,
    p.name as product_name,
    p.sort as product_sort,
    wp.count as available_quantity,
    wp.price as base_price,
    (wp.count * wp.price) as total_value
FROM trading_base tb
JOIN warehouse_product wp ON tb.trading_base_id = wp.trading_base_id
JOIN product p ON wp.article = p.article
WHERE tb.trading_base_id = 2
  AND wp.count > 0
ORDER BY p.name;

-- 2. Какие отсутствующие товары может заказать магазин на базе?
SELECT --DISTINCT
	s.name as store_name,
    p.name as product_name,
    tb.name as trading_base,
    wp.count as available_quantity,
    wp.price as base_price,
	w_priority.priority
FROM product p
JOIN warehouse_product wp ON p.article = wp.article
JOIN trading_base tb ON wp.trading_base_id = tb.trading_base_id
JOIN store s ON s.store_id = 1
JOIN warehouse_priority w_priority ON w_priority.store_id = s.store_id AND w_priority.article = p.article AND w_priority.trading_base_id = tb.trading_base_id
WHERE p.article IN (
    SELECT dp.article
    FROM department_product dp 
    JOIN department d ON dp.department_id = d.department_id 
    WHERE d.store_id = s.store_id AND dp.count = 0
)
AND wp.count > 0
ORDER BY p.name, w_priority.priority;

-- 2.доп Какие отсутствующие товары может заказать магазин на базе (в том числе, которых не было, но для которых есть приоритет)?
SELECT --DISTINCT
	s.name as store_name,
    p.name as product_name,
    tb.name as trading_base,
    wp.count as available_quantity,
    wp.price as base_price,
	w_priority.priority
FROM product p
JOIN warehouse_product wp ON p.article = wp.article
JOIN trading_base tb ON wp.trading_base_id = tb.trading_base_id
JOIN store s ON s.store_id = 1
JOIN warehouse_priority w_priority ON w_priority.store_id = s.store_id AND w_priority.article = p.article AND w_priority.trading_base_id = tb.trading_base_id
WHERE 
(
	p.article IN (
		SELECT dp.article
		FROM department_product dp 
		JOIN department d ON dp.department_id = d.department_id 
		WHERE d.store_id = s.store_id AND dp.count = 0
	) 
	OR p.article NOT IN (
		SELECT dp.article
		FROM department_product dp 
		JOIN department d ON dp.department_id = d.department_id 
		WHERE d.store_id = s.store_id
	)
)
AND wp.count > 0
ORDER BY p.name, w_priority.priority;

-- 3. Какие товары, и в каком количестве имеются в отделе магазина?
SELECT 
    s.name as store_name,
    d.name as department_name,
    p.name as product_name,
    dp.count as quantity
FROM store s
JOIN department d ON s.store_id = d.store_id
JOIN department_product dp ON d.department_id = dp.department_id
JOIN product p ON dp.article = p.article
WHERE d.department_id = 1
ORDER BY p.name;

-- 4. Список заведующих отделами магазина?
SELECT 
    s.name as store_name,
    d.name as department_name,
    e.first_name || ' ' || e.last_name as manager_name
FROM store s
JOIN department d ON s.store_id = d.store_id
JOIN employee e ON d.manager_id = e.employee_id
WHERE s.store_id = 1
ORDER BY d.name;

-- 5. Суммарная стоимость товара в каждом отделе?
SELECT 
    s.name as store_name,
    d.name as department_name,
    SUM(dp.count * pp.price) as total_value
FROM store s
JOIN department d ON s.store_id = d.store_id
JOIN department_product dp ON d.department_id = dp.department_id
JOIN product_price pp ON dp.article = pp.article AND s.store_class_id = pp.store_class_id
GROUP BY s.name, d.name
ORDER BY total_value DESC;

-- 6. На каких базах, и в каких количествах есть товар нужного наименования?
SELECT 
    p.name as product_name,
    tb.name as trading_base,
    tb.description as base_description,
    wp.count as available_quantity,
    wp.price as price_per_unit
FROM product p
JOIN warehouse_product wp ON p.article = wp.article
JOIN trading_base tb ON wp.trading_base_id = tb.trading_base_id
WHERE p.name ILIKE '%молоко%' OR p.article = 1
ORDER BY wp.count DESC;
