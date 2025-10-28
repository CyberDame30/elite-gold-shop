import "dotenv/config";
import express from "express";
import cookieParser from "cookie-parser";
import cors from "cors";
import path from "path";
import { fileURLToPath } from "url";

import { initDb } from "./db.js";
import authRoutes from "./routes/auth.routes.js";
import userRoutes from "./routes/user.routes.js";
import adminRoutes from "./routes/admin.routes.js";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const app = express();
const PORT = process.env.PORT || 4000;

// CORS (за потреби підстав свій фронтенд)
app.use(cors({ origin: true, credentials: true }));
app.use(express.json());
app.use(cookieParser());

// Ініціалізація БД
initDb();

// API-маршрути
app.use("/api/auth", authRoutes);
app.use("/api/user", userRoutes);
app.use("/api/admin", adminRoutes);

// Простенькі форми для реєстрації/логіна (щоб зручно тестувати)
app.get("/register", (_req, res) => {
  res.type("html").send(`
    <form method="post" action="/api/auth/register" onsubmit="event.preventDefault(); fetch('/api/auth/register',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({email: email.value, password: pass.value})}).then(r=>r.json()).then(alert)">
      <h3>Реєстрація user</h3>
      <input id="email" placeholder="email" required />
      <input id="pass" type="password" placeholder="password" required />
      <button>Зареєструватися</button>
    </form>
  `);
});

app.get("/login", (_req, res) => {
  res.type("html").send(`
    <form method="post" action="/api/auth/login" onsubmit="event.preventDefault(); fetch('/api/auth/login',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({email: email.value, password: pass.value})}).then(r=>r.json()).then(alert)">
      <h3>Логін</h3>
      <input id="email" placeholder="email" required />
      <input id="pass" type="password" placeholder="password" required />
      <button>Увійти</button>
      <p>Адмін (seed): admin@elitegold.ua / admin123</p>
    </form>
  `);
});

// Статика лендінгу на тому ж порту (опційно):
app.use(express.static(path.join(__dirname, "..", "landing")));
app.get("/", (_req, res) => res.sendFile(path.join(__dirname, "..", "landing", "index.html")));

app.listen(PORT, () => {
  console.log(`✅ API + Landing running on http://localhost:${PORT}`);
});
