import express from "express";
import path from "path";
import { fileURLToPath } from "url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const app = express();
const PORT = 5173;


app.use((req, _res, next) => {
  console.log("→", new Date().toISOString(), req.method, req.url);
  next();
});


app.use((_, res, next) => {
  res.set("Cache-Control", "no-store, no-cache, must-revalidate, proxy-revalidate");
  res.set("Pragma", "no-cache");
  res.set("Expires", "0");
  next();
});


app.use(express.static(path.join(__dirname, "landing")));


app.get("/", (_, res) => {
  res.sendFile(path.join(__dirname, "landing", "index.html"));
});


app.get("/ping", (_, res) => res.type("text").send("pong"));

app.listen(PORT, () => {
  console.log(`✅ Сервер запущено: http://localhost:${PORT}`);
});
