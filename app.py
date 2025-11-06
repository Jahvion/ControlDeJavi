# app.py
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from datetime import datetime, date
from apscheduler.schedulers.background import BackgroundScheduler
from pytz import timezone
import os

import storage  # expone: CATEGORIES, ensure_data_file, list_products, add_product, delete_product
import bot  # expone: send_message(text: str) -> bool

# --- Configuración base ---
app = Flask(__name__)
# CORS abierto para permitir llamadas desde el frontend (.dev o .app)
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=False)

API_KEY = os.getenv("API_KEY", "javi123")
ALERT_DAYS = [30, 15, 7, 4, 3, 2, 1]
AR_TZ = timezone("America/Argentina/Buenos_Aires")
NOTIFY_HOUR = 22
DATE_FMT = "%Y-%m-%d"


# --- Middleware de seguridad ---
@app.before_request
def check_api_key():
  if request.method == "OPTIONS":
    return "", 200
  if request.path in ("/", "/health"):
    return None
  client_key = request.headers.get("X-API-KEY")
  if client_key != API_KEY:
    return jsonify({"error": "unauthorized"}), 401


# --- Helpers internos ---
def _parse_date(s: str):
  try:
    return datetime.strptime(s, DATE_FMT).date()
  except Exception:
    return None


def _today_ar():
  return datetime.now(AR_TZ).date()


def _human(delta_days: int):
  if delta_days < 0:
    return f"❌ vencido hace {-delta_days} día(s)"
  if delta_days == 0:
    return "⚠️ vence HOY"
  if delta_days == 1:
    return "⚠️ vence en 1 día"
  return f"⚠️ vence en {delta_days} días"


def _summarize(products):
  if not products:
    return "No hay productos cargados todavía."

  hoy = _today_ar()
  por_categoria = {}
  sin_fecha = []

  for p in products:
    name = p.get("name") or p.get("title") or "Sin nombre"
    cat = p.get("category") or "Otros"
    dstr = p.get("expiration_date")
    if not dstr:
      sin_fecha.append((cat, name))
      continue
    d = _parse_date(dstr)
    if not d:
      sin_fecha.append((cat, name))
      continue

    delta = (d - hoy).days
    if delta <= 0 or (delta in ALERT_DAYS) or (0 < delta <= min(ALERT_DAYS)):
      por_categoria.setdefault(cat, []).append((name, dstr, delta))

  if not por_categoria and not sin_fecha:
    return "✅ Nada por vencer según los umbrales configurados."

  partes = []
  if por_categoria:
    for cat, items in sorted(por_categoria.items()):
      partes.append(f"• {cat}:")
      for name, dstr, delta in sorted(items, key=lambda x: x[2]):
        partes.append(f"   - {name} ({dstr}) → {_human(delta)}")
  if sin_fecha:
    partes.append("\nℹ️ Productos sin fecha de vencimiento:")
    for (cat, name) in sin_fecha[:10]:
      partes.append(f"   - {name} [{cat}]")

  return "\n".join(partes)


def _send_daily_notification():
  try:
    productos = storage.list_products()
    resumen = _summarize(productos)
    header = "⏰ *ControlDeJavi* — chequeo diario de vencimientos (22:00 AR)\n"
    ok = bot.send_message(header + resumen)
    print(f"[notify] Telegram enviado: {ok}")
    return ok
  except Exception as e:
    print("[notify] Error:", e)
    return False


# --- Endpoints principales ---
@app.route("/", methods=["GET"])
def home():
  return ("<h3>API corriendo correctamente ✅</h3>"
          "<ul>"
          "<li>GET /products</li>"
          "<li>POST /products</li>"
          "<li>DELETE /products/&lt;id&gt;</li>"
          "<li>GET /test-notification</li>"
          "</ul>"), 200


@app.route("/health", methods=["GET"])
def health():
  return jsonify({"ok": True}), 200


@app.route("/products", methods=["GET"])
def list_all():
  cat = request.args.get("category")
  data = storage.list_products()
  if cat:
    data = [p for p in data if p.get("category") == cat]
  return jsonify(data), 200


@app.route("/products", methods=["POST"])
def add_product():
  data = request.get_json(silent=True) or {}
  name = (data.get("name") or "").strip()
  category = (data.get("category") or "").strip()
  expiration_date = (data.get("expiration_date") or "").strip()

  if not name or not category or not expiration_date:
    return jsonify({"error":
                    "Faltan campos: name, category, expiration_date"}), 400

  if storage.CATEGORIES and category not in storage.CATEGORIES:
    return jsonify(
        {"error":
         f"Categoría inválida. Usa una de: {storage.CATEGORIES}"}), 400

  d = _parse_date(expiration_date)
  if not d:
    return jsonify({"error":
                    f"Formato de fecha inválido. Usa {DATE_FMT}"}), 400

  try:
    # Llamada posicional (sin quantity)
    created = storage.add_product(name, category, d.strftime(DATE_FMT))

    if isinstance(created, bool):
      created = {
          "name": name,
          "category": category,
          "expiration_date": d.strftime(DATE_FMT),
      }

    return jsonify({"ok": True, "product": created}), 201
  except Exception as e:
    return jsonify({"error": f"No se pudo guardar: {str(e)}"}), 500


@app.route("/products/<pid>", methods=["DELETE"])
def delete_one(pid):
  try:
    try:
      product_id = int(pid)
    except ValueError:
      return jsonify({"error": "ID inválido"}), 400
    ok = storage.delete_product(product_id)
    if not ok:
      return jsonify({"error": "No existe el ID"}), 404
    return "", 204
  except Exception as e:
    return jsonify({"error": f"No se pudo borrar: {str(e)}"}), 500

@app.route("/test-notification", methods=["GET"])
def test_notification():
  try:
    productos = storage.list_products()
    resumen = _summarize(productos)
    ok = bot.send_message("🔔 Prueba de ControlDeJavi\n" + resumen)
    return jsonify({"ok": ok}), (200 if ok else 500)
  except Exception as e:
    return jsonify({"error": f"Error enviando prueba: {str(e)}"}), 500


# --- Scheduler ---
def _start_scheduler():
  sched = BackgroundScheduler(timezone=AR_TZ)
  sched.add_job(_send_daily_notification, "cron", hour=NOTIFY_HOUR, minute=0)
  sched.start()
  return sched




# ---- Frontend static serving ----
@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def serve_frontend(path):
  root = "frontend"
  # If request matches an existing file (css/js/img), serve it
  if path and os.path.exists(os.path.join(root, path)):
    return send_from_directory(root, path)
  # Otherwise, serve index.html
  return send_from_directory(root, "index.html")


# --- Inicio ---
if __name__ == "__main__":
  print("✅ ControlDeJavi iniciado")
  storage.ensure_data_file()
  try:
    bot.send_message(
        "✅ ControlDeJavi backend en marcha. Notificaciones diarias 22:00 (AR)."
    )
  except Exception as e:
    print("[startup] Aviso Telegram falló:", e)

  _start_scheduler()
  app.run(host="0.0.0.0", port=int(os.getenv("PORT", 10000)), debug=False)
