import { Router } from "express";
import { authRequired } from "../middleware/auth.js";
import path from "path";
import { fileURLToPath } from "url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const router = Router();

// Доступно авторизованим (будь-яка роль)
router.get("/home", authRequired, (req, res) => {
  res.sendFile(path.join(__dirname, "..", "views", "user.html"));
});

export default router;
