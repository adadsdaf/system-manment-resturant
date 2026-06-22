from database.connection import create_connection
import datetime


def get_sales_summary(period="today"):
    conn = create_connection()
    if not conn:
        return {}
    try:
        cursor = conn.cursor()
        now    = datetime.datetime.now()

        if period == "today":
            start = now.strftime("%Y-%m-%d")
            end   = start
        elif period == "week":
            start = (now - datetime.timedelta(days=7)
                     ).strftime("%Y-%m-%d")
            end   = now.strftime("%Y-%m-%d")
        elif period == "month":
            start = now.strftime("%Y-%m-01")
            end   = now.strftime("%Y-%m-%d")
        else:
            start = now.strftime("%Y-%m-%d")
            end   = start

        cursor.execute("""
            SELECT
                COUNT(*)                      AS total_orders,
                COALESCE(SUM(total_amount),0) AS total_revenue,
                COALESCE(AVG(total_amount),0) AS avg_order,
                COALESCE(MAX(total_amount),0) AS max_order,
                COALESCE(SUM(discount_amount),0) AS total_discount,
                COALESCE(SUM(tax_amount),0)   AS total_tax
            FROM orders
            WHERE CAST(created_at AS DATE)
                BETWEEN ? AND ?
            AND order_status = 'Completed'
        """, (start, end))
        row = cursor.fetchone()
        return {
            "total_orders":   row[0] or 0,
            "total_revenue":  float(row[1] or 0),
            "avg_order":      float(row[2] or 0),
            "max_order":      float(row[3] or 0),
            "total_discount": float(row[4] or 0),
            "total_tax":      float(row[5] or 0),
            "period":         period,
            "start":          start,
            "end":            end,
        }
    except Exception as e:
        print(f"Error fetching sales summary: {e}")
        return {}
    finally:
        conn.close()


def get_daily_sales(days=7):
    conn = create_connection()
    if not conn:
        return []
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT
                CAST(created_at AS DATE)      AS sale_date,
                COUNT(*)                      AS total_orders,
                COALESCE(SUM(total_amount),0) AS total_revenue
            FROM orders
            WHERE CAST(created_at AS DATE) >=
                CAST(DATEADD(day, ?, GETDATE()) AS DATE)
            AND order_status = 'Completed'
            GROUP BY CAST(created_at AS DATE)
            ORDER BY sale_date ASC
        """, (-days,))
        return cursor.fetchall()
    except Exception as e:
        print(f"Error fetching daily sales: {e}")
        return []
    finally:
        conn.close()


def get_sales_by_payment_method(period="month"):
    conn = create_connection()
    if not conn:
        return []
    try:
        cursor = conn.cursor()
        now    = datetime.datetime.now()
        if period == "today":
            start = now.strftime("%Y-%m-%d")
        elif period == "week":
            start = (now - datetime.timedelta(days=7)
                     ).strftime("%Y-%m-%d")
        else:
            start = now.strftime("%Y-%m-01")

        cursor.execute("""
            SELECT
                payment_method,
                COUNT(*)                      AS total_orders,
                COALESCE(SUM(total_amount),0) AS total_revenue
            FROM orders
            WHERE CAST(created_at AS DATE) >= ?
            AND order_status = 'Completed'
            GROUP BY payment_method
            ORDER BY total_revenue DESC
        """, (start,))
        return cursor.fetchall()
    except Exception as e:
        print(f"Error fetching payment methods: {e}")
        return []
    finally:
        conn.close()


def get_top_selling_items(limit=10, period="month"):
    conn = create_connection()
    if not conn:
        return []
    try:
        cursor = conn.cursor()
        now    = datetime.datetime.now()
        if period == "today":
            start = now.strftime("%Y-%m-%d")
        elif period == "week":
            start = (now - datetime.timedelta(days=7)
                     ).strftime("%Y-%m-%d")
        else:
            start = now.strftime("%Y-%m-01")

        cursor.execute("""
            SELECT TOP (?)
                oi.item_name,
                SUM(oi.quantity)              AS total_qty,
                COALESCE(SUM(oi.subtotal),0)  AS total_revenue
            FROM order_items oi
            JOIN orders o ON oi.order_id = o.order_id
            WHERE CAST(o.created_at AS DATE) >= ?
            AND o.order_status = 'Completed'
            GROUP BY oi.item_name
            ORDER BY total_qty DESC
        """, (limit, start))
        return cursor.fetchall()
    except Exception as e:
        print(f"Error fetching top items: {e}")
        return []
    finally:
        conn.close()


def get_sales_by_category(period="month"):
    conn = create_connection()
    if not conn:
        return []
    try:
        cursor = conn.cursor()
        now    = datetime.datetime.now()
        if period == "today":
            start = now.strftime("%Y-%m-%d")
        elif period == "week":
            start = (now - datetime.timedelta(days=7)
                     ).strftime("%Y-%m-%d")
        else:
            start = now.strftime("%Y-%m-01")

        cursor.execute("""
            SELECT
                mc.category_name,
                SUM(oi.quantity)             AS total_qty,
                COALESCE(SUM(oi.subtotal),0) AS total_revenue
            FROM order_items oi
            JOIN orders o
                ON oi.order_id = o.order_id
            JOIN menu_items mi
                ON oi.menu_item_id = mi.item_id
            JOIN menu_categories mc
                ON mi.category_id = mc.category_id
            WHERE CAST(o.created_at AS DATE) >= ?
            AND o.order_status = 'Completed'
            GROUP BY mc.category_name
            ORDER BY total_revenue DESC
        """, (start,))
        return cursor.fetchall()
    except Exception as e:
        print(f"Error fetching category sales: {e}")
        return []
    finally:
        conn.close()


def get_top_customers(limit=10, period="month"):
    conn = create_connection()
    if not conn:
        return []
    try:
        cursor = conn.cursor()
        now    = datetime.datetime.now()
        if period == "today":
            start = now.strftime("%Y-%m-%d")
        elif period == "week":
            start = (now - datetime.timedelta(days=7)
                     ).strftime("%Y-%m-%d")
        else:
            start = now.strftime("%Y-%m-01")

        cursor.execute("""
            SELECT TOP (?)
                COALESCE(o.customer_name, 'Guest') AS name,
                COUNT(*)                      AS total_orders,
                COALESCE(SUM(o.total_amount),0) AS total_spent
            FROM orders o
            WHERE CAST(o.created_at AS DATE) >= ?
            AND o.order_status = 'Completed'
            GROUP BY o.customer_name
            ORDER BY total_spent DESC
        """, (limit, start))
        return cursor.fetchall()
    except Exception as e:
        print(f"Error fetching top customers: {e}")
        return []
    finally:
        conn.close()


def get_staff_performance(period="month"):
    conn = create_connection()
    if not conn:
        return []
    try:
        cursor = conn.cursor()
        now    = datetime.datetime.now()
        if period == "today":
            start = now.strftime("%Y-%m-%d")
        elif period == "week":
            start = (now - datetime.timedelta(days=7)
                     ).strftime("%Y-%m-%d")
        else:
            start = now.strftime("%Y-%m-01")

        cursor.execute("""
            SELECT
                u.full_name,
                COUNT(o.order_id)             AS total_orders,
                COALESCE(SUM(o.total_amount),0) AS total_revenue,
                COALESCE(AVG(o.total_amount),0) AS avg_order
            FROM orders o
            JOIN users u ON o.served_by = u.user_id
            WHERE CAST(o.created_at AS DATE) >= ?
            AND o.order_status = 'Completed'
            GROUP BY u.full_name
            ORDER BY total_revenue DESC
        """, (start,))
        return cursor.fetchall()
    except Exception as e:
        print(f"Error fetching staff performance: {e}")
        return []
    finally:
        conn.close()


def get_low_stock_report():
    conn = create_connection()
    if not conn:
        return []
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT
                i.name,
                i.unit,
                i.current_stock,
                i.minimum_stock,
                i.reorder_level,
                i.unit_cost,
                i.current_stock * i.unit_cost AS stock_value,
                COALESCE(s.supplier_name, '—') AS supplier,
                CASE
                    WHEN i.current_stock <= 0
                        THEN 'Out of Stock'
                    WHEN i.current_stock <= i.minimum_stock
                        THEN 'Critical'
                    ELSE 'Low Stock'
                END AS alert_level
            FROM ingredients i
            LEFT JOIN suppliers s
                ON i.supplier_id = s.supplier_id
            WHERE i.current_stock <= i.reorder_level
            AND i.is_active = 1
            ORDER BY i.current_stock ASC
        """)
        return cursor.fetchall()
    except Exception as e:
        print(f"Error fetching low stock: {e}")
        return []
    finally:
        conn.close()


def get_hourly_sales(date=None):
    conn = create_connection()
    if not conn:
        return []
    try:
        cursor = conn.cursor()
        if not date:
            date = datetime.date.today().strftime("%Y-%m-%d")
        cursor.execute("""
            SELECT
                DATEPART(HOUR, created_at)    AS hour,
                COUNT(*)                      AS total_orders,
                COALESCE(SUM(total_amount),0) AS total_revenue
            FROM orders
            WHERE CAST(created_at AS DATE) = ?
            AND order_status = 'Completed'
            GROUP BY DATEPART(HOUR, created_at)
            ORDER BY hour ASC
        """, (date,))
        return cursor.fetchall()
    except Exception as e:
        print(f"Error fetching hourly sales: {e}")
        return []
    finally:
        conn.close()