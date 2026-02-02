-- Ejemplo 6: Query con UNION
SELECT 
    customer_id,
    'order' as transaction_type,
    order_date as transaction_date,
    order_amount as amount
FROM orders
WHERE order_date >= CURRENT_DATE - INTERVAL '180' DAY

UNION ALL

SELECT 
    customer_id,
    'return' as transaction_type,
    return_date as transaction_date,
    return_amount * -1 as amount
FROM returns
WHERE return_date >= CURRENT_DATE - INTERVAL '180' DAY

ORDER BY customer_id, transaction_date DESC;