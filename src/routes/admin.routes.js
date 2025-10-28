import { Router } from "express";
import { authRequired, requireRole } from "../middleware/auth.js";
import path from "path";
import { fileURLToPath } from "url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const router = Router();

// Тільки роль admin
router.get("/dashboard", authRequired, requireRole("admin"), (req, res) => {
  res.sendFile(path.join(__dirname, "..", "views", "admin.html"));
});

export default router;
