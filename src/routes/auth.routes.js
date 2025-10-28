import { Router } from "express";
import { db } from "../db.js";
import bcrypt from "bcrypt";
import jwt from "jsonwebtoken";

const router = Router();

// POST /api/auth/register  (тільки звичайні користувачі)
router.post("/register", async (req, res) => {
  const { email, password } = req.body || {};
  if (!email || !password) return res.status(400).json({ error: "email & password required" });

  try {
    const hash = await bcrypt.hash(password, 10);
    db.run(
      `INSERT INTO users (email, password_hash, role) VALUES (?,?,?)`,
      [email, hash, "user"],
      function (err) {
        if (err) {
          if (err.message?.includes("UNIQUE")) return res.status(409).json({ error: "Email already exists" });
          return res.status(500).json({ error: "DB insert error" });
        }
        const user = { id: this.lastID, email, role: "user" };
        const token = jwt.sign(user, process.env.JWT_SECRET, { expiresIn: process.env.JWT_EXPIRES || "2h" });
        res
          .cookie("token", token, { httpOnly: true, sameSite: "lax" })
          .status(201)
          .json({ message: "Registered", user });
      }
    );
  } catch (e) {
    res.status(500).json({ error: "Hashing error" });
  }
});

// POST /api/auth/login  (для admin і user)
router.post("/login", (req, res) => {
  const { email, password } = req.body || {};
  if (!email || !password) return res.status(400).json({ error: "email & password required" });

  db.get(`SELECT * FROM users WHERE email = ?`, [email], async (err, row) => {
    if (err) return res.status(500).json({ error: "DB select error" });
    if (!row) return res.status(401).json({ error: "Invalid credentials" });

    const ok = await bcrypt.compare(password, row.password_hash);
    if (!ok) return res.status(401).json({ error: "Invalid credentials" });

    const user = { id: row.id, email: row.email, role: row.role };
    const token = jwt.sign(user, process.env.JWT_SECRET, { expiresIn: process.env.JWT_EXPIRES || "2h" });
    res.cookie("token", token, { httpOnly: true, sameSite: "lax" }).json({ message: "Logged in", user });
  });
});

// POST /api/auth/logout
router.post("/logout", (req, res) => {
  res.clearCookie("token", { httpOnly: true, sameSite: "lax" }).json({ message: "Logged out" });
});

// GET /api/auth/me
router.get("/me", (req, res) => {
  const token = req.cookies?.token || req.headers.authorization?.replace("Bearer ", "");
  if (!token) return res.json({ user: null });
  try {
    const payload = jwt.verify(token, process.env.JWT_SECRET);
    res.json({ user: payload });
  } catch {
    res.json({ user: null });
  }
});

export default router;
