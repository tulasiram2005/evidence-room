-- Dialect: SQLite
-- query: monthly
WITH monthly AS (
 SELECT order_month, SUM(revenue_paise) revenue_paise, COUNT(*) orders
 FROM clean_orders GROUP BY order_month
)
SELECT *, revenue_paise - LAG(revenue_paise) OVER (ORDER BY order_month) change_paise
FROM monthly ORDER BY order_month;
-- query: top_products
SELECT c.product_id, p.product_name, p.category, SUM(c.revenue_paise) revenue_paise
FROM clean_orders c JOIN products p USING(product_id)
GROUP BY c.product_id ORDER BY revenue_paise DESC, c.product_id LIMIT 10;
-- query: monthly_products
WITH ranked AS (
 SELECT order_month, c.product_id, p.product_name, p.category, SUM(revenue_paise) revenue_paise,
 ROW_NUMBER() OVER (PARTITION BY order_month ORDER BY SUM(revenue_paise) DESC, c.product_id) rank
 FROM clean_orders c JOIN products p USING(product_id) GROUP BY order_month, c.product_id
)
SELECT * FROM ranked WHERE rank <= 10 ORDER BY order_month, rank;
-- query: cohorts
WITH first_orders AS (
 SELECT *, MIN(order_date) OVER (PARTITION BY customer_id) first_date FROM clean_orders
), cohorts AS (
 SELECT *, CASE WHEN order_date = first_date THEN 'new' ELSE 'repeat' END cohort FROM first_orders
)
SELECT order_month, cohort, SUM(revenue_paise) revenue_paise, COUNT(*) orders,
 COUNT(DISTINCT customer_id) customers FROM cohorts
GROUP BY order_month, cohort ORDER BY order_month, cohort;
-- query: health
SELECT bucket, COUNT(*) rows FROM audit_rows GROUP BY bucket ORDER BY bucket;
-- query: exclusions
SELECT order_month, reason_code, COUNT(*) rows FROM audit_rows
WHERE bucket <> 'clean' GROUP BY order_month, reason_code ORDER BY order_month, reason_code;
-- query: reconciliation
SELECT order_month,
 SUM(face_paise) naive_mixed_currency_face_paise,
 SUM(CASE WHEN bucket <> 'clean' THEN -face_paise ELSE 0 END) excluded_delta_paise,
 SUM(CASE WHEN bucket = 'clean' THEN trusted_paise - face_paise ELSE 0 END) conversion_delta_paise,
 SUM(trusted_paise) trusted_revenue_paise
FROM audit_rows WHERE completed_like = 1
GROUP BY order_month ORDER BY order_month;
