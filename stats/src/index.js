// pp-stats：Potato Pai 網站瀏覽人數
// POST /hit  記一次瀏覽，回傳 {ok:1, views}
// GET  /stats 回傳 {ok:1, views}
// 前端已用 localStorage 擋「同一裝置 30 分鐘內只算一次」；這裡再用記憶體擋同 IP 30 分鐘內重複寫入。
const ORIGINS = ["https://potatopai.com", "https://georgepai.github.io"];
const DEDUP_MS = 30 * 60 * 1000;
const seen = new Map(); // ip -> 上次寫入時間（單一 isolate 內有效）
let ready = false;

function cors(req) {
  const o = req.headers.get("Origin") || "";
  return {
    "Access-Control-Allow-Origin": ORIGINS.includes(o) ? o : ORIGINS[0],
    "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type",
    "Vary": "Origin",
  };
}
const json = (req, body, status = 200) =>
  new Response(JSON.stringify(body), { status, headers: { "Content-Type": "application/json", "Cache-Control": "no-store", ...cors(req) } });

async function init(db) {
  if (ready) return;
  await db.prepare("CREATE TABLE IF NOT EXISTS counters (k TEXT PRIMARY KEY, v INTEGER NOT NULL DEFAULT 0)").run();
  await db.prepare("INSERT OR IGNORE INTO counters (k, v) VALUES ('views', 0)").run();
  ready = true;
}
const read = async db => (await db.prepare("SELECT v FROM counters WHERE k='views'").first("v")) ?? 0;

export default {
  async fetch(req, env) {
    const { pathname } = new URL(req.url);
    if (req.method === "OPTIONS") return new Response(null, { status: 204, headers: cors(req) });
    try {
      await init(env.DB);
      if (pathname === "/hit" && req.method === "POST") {
        const ip = req.headers.get("CF-Connecting-IP") || "?";
        const now = Date.now(), last = seen.get(ip) || 0;
        if (now - last > DEDUP_MS) {
          seen.set(ip, now);
          if (seen.size > 5000) for (const [k, t] of seen) if (now - t > DEDUP_MS) seen.delete(k);
          const v = await env.DB.prepare("UPDATE counters SET v = v + 1 WHERE k='views' RETURNING v").first("v");
          return json(req, { ok: 1, views: v });
        }
        return json(req, { ok: 1, views: await read(env.DB), dup: 1 });
      }
      if (pathname === "/stats" && req.method === "GET") return json(req, { ok: 1, views: await read(env.DB) });
      if (pathname === "/") return json(req, { ok: 1, name: "pp-stats" });
      return json(req, { ok: 0, err: "not found" }, 404);
    } catch (e) {
      return json(req, { ok: 0, err: "server" }, 500);
    }
  },
};
