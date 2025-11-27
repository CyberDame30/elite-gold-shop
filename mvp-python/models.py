import sqlite3
from pathlib import Path
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

DB_NAME = "app.db"


def get_connection():
    return sqlite3.connect(DB_NAME)


def init_db():
    """Створення таблиць + дефолтний адмін."""
    conn = get_connection()
    cur = conn.cursor()

    # Таблиця користувачів
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL
        );
        """
    )

    # НОВА ТАБЛИЦЯ З ПОВНИМИ ПОЛЯМИ
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,

            customer_name TEXT,
            phone TEXT,
            email TEXT,
            city TEXT,
            address TEXT,

            delivery_method TEXT,
            payment_method TEXT,
            comment TEXT,

            created_at TEXT DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY(user_id) REFERENCES users(id)
        );
        """
    )

    # Таблиця товарів у замовленні
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS order_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER NOT NULL,
            product_desc TEXT NOT NULL,
            qty INTEGER NOT NULL,
            price REAL NOT NULL,
            FOREIGN KEY(order_id) REFERENCES orders(id)
        );
        """
    )

    conn.commit()

    # Створити дефолтного адміна, якщо немає
    cur.execute("SELECT id FROM users WHERE email = ?", ("admin@elitegold.ua",))
    row = cur.fetchone()
    if not row:
        hashed = generate_password_hash("admin123")
        cur.execute(
            "INSERT INTO users (email, password, role) VALUES (?, ?, ?)",
            ("admin@elitegold.ua", hashed, "admin"),
        )
        conn.commit()

    conn.close()


# ------------------ КОРИСТУВАЧІ ------------------


def create_user(email: str, password: str, role: str = "user"):
    conn = get_connection()
    cur = conn.cursor()

    hashed = generate_password_hash(password)

    cur.execute(
        "INSERT INTO users (email, password, role) VALUES (?, ?, ?)",
        (email, hashed, role),
    )
    conn.commit()
    conn.close()


def find_user_by_email(email: str):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "SELECT id, email, password, role FROM users WHERE email = ?",
        (email,),
    )
    row = cur.fetchone()
    conn.close()
    return row


def check_password(stored_hash: str, candidate: str) -> bool:
    return check_password_hash(stored_hash, candidate)


# ------------------ ЗАМОВЛЕННЯ ------------------


def create_order(
    user_id,
    items,
    customer_name="",
    phone="",
    email="",
    city="",
    address="",
    delivery_method="",
    payment_method="",
    comment=""
):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    # Insert order
    cur.execute("""
        INSERT INTO orders (
            user_id, customer_name, phone, email, city,
            address, delivery_method, payment_method, comment
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (user_id, customer_name, phone, email, city,
          address, delivery_method, payment_method, comment))

    order_id = cur.lastrowid

    # Insert items
    for item in items:
        cur.execute("""
            INSERT INTO order_items (order_id, product_desc, qty, price)
            VALUES (?, ?, ?, ?)
        """, (order_id, item["product_desc"], item["qty"], item["price"]))

    conn.commit()
    conn.close()
    return order_id


def get_all_orders():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT o.id, u.email, o.created_at
        FROM orders o
        JOIN users u ON o.user_id = u.id
        ORDER BY o.id DESC
        """
    )
    rows = cur.fetchall()

    results = []

    for order_id, email, created_at in rows:
        cur.execute("""
            SELECT product_desc, qty, price
            FROM order_items
            WHERE order_id = ?
        """, (order_id,))
        items = cur.fetchall()

        items_str_parts = []
        total = 0
        for desc, qty, price in items:
            items_str_parts.append(f"{desc} (x{qty}) — {price}$")
            total += qty * price

        results.append({
            "id": order_id,
            "email": email,
            "created": created_at,
            "items": "; ".join(items_str_parts),
            "total": total
        })

    conn.close()
    return results


