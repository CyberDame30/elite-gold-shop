import sqlite3 from "sqlite3";
import path from "path";
import { fileURLToPath } from "url";
import bcrypt from "bcrypt";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// SQLite файл зберігаємо в корені репо:
const DB_PATH = path.join(__dirname, "..", "app.db");
sqlite3.verbose();
export const db = new sqlite3.Database(DB_PATH);

// Ініціалізація схем
export function initDb() {
  db.serialize(() => {
    db.run(`CREATE TABLE IF NOT EXISTS users (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      email TEXT UNIQUE NOT NULL,
      password_hash TEXT NOT NULL,
      role TEXT NOT NULL CHECK(role IN ('admin','user')),
      created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );`);

    // Демо-адмін (створиться один раз, якщо таблиця пуста)
    db.get("SELECT COUNT(*) AS cnt FROM users;", async (err, row) => {
      if (err) return console.error("DB count error:", err);
      if (row.cnt === 0) {
        const hash = await bcrypt.hash("admin123", 10);
        db.run(
          `INSERT INTO users (email, password_hash, role) VALUES (?,?,?)`,
          ["admin@elitegold.ua", hash, "admin"],
          (e) => {
            if (e) console.error("Seed admin error:", e);
            else console.log("✅ Seeded admin: admin@elitegold.ua / admin123");
          }
        );
      }
    });
  });
}
