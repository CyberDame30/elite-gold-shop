import express from "express";
import path from "path";
import { fileURLToPath } from "url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const app = express();
const PORT = 5173;

// Видаємо статичні файли з папки landing
app.use(express.static(path.join(__dirname, "landing")));

app.get("/", (req, res) => {
  res.sendFile(path.join(__dirname, "landing", "index.html"));
});

app.listen(PORT, () => {
  console.log(`✅ Сервер запущено: http://localhost:${PORT}`);
});
