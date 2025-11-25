# models.py — прості ORM-like функції на sqlite3
import sqlite3
from pathlib import Path
from werkzeug.security import generate_password_hash, check_password_hash

DB_PATH = Path(__file__).resolve().parent / "app_mvp.db"

def get_conn():
    return sqlite3.connect(DB_PATH)

def init_db():
    conn = get_conn()
    cur = conn.cursor()
    cur.executescript("""
    CREATE TABLE IF NOT EXISTS users (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      email TEXT UNIQUE NOT NULL,
      password_hash TEXT NOT NULL,
      role TEXT NOT NULL DEFAULT 'user',
      created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS products (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      name TEXT,
      base_price INTEGER DEFAULT 0
    );

    CREATE TABLE IF NOT EXISTS orders (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      user_id INTEGER,
      created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
      total INTEGER,
      FOREIGN KEY(user_id) REFERENCES users(id)
    );

    CREATE TABLE IF NOT EXISTS order_items (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      order_id INTEGER,
      product_desc TEXT,
      qty INTEGER,
      price INTEGER,
      FOREIGN KEY(order_id) REFERENCES orders(id)
    );
    """)
    conn.commit()
    conn.close()

def create_user(email, password, role="user"):
    conn = get_conn()
    cur = conn.cursor()
    try:
        ph = generate_password_hash(password)
        cur.execute("INSERT INTO users (email,password_hash,role) VALUES (?,?,?)", (email, ph, role))
        conn.commit()
        return cur.lastrowid
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

def find_user_by_email(email):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT id,email,password_hash,role FROM users WHERE email=?", (email,))
    row = cur.fetchone()
    conn.close()
    return row

def check_password(stored_hash, password):
    return check_password_hash(stored_hash, password)

def create_order(user_id, items):
    """
    items: list of dict {product_desc, qty, price}
    returns order id
    """
    conn = get_conn()
    cur = conn.cursor()
    total = sum(it["qty"]*it["price"] for it in items)
    cur.execute("INSERT INTO orders (user_id,total) VALUES (?,?)", (user_id, total))
    order_id = cur.lastrowid
    for it in items:
        cur.execute("INSERT INTO order_items (order_id,product_desc,qty,price) VALUES (?,?,?,?)",
                    (order_id, it["product_desc"], it["qty"], it["price"]))
    conn.commit()
    conn.close()
    return order_id
