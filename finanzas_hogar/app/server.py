"""Servidor mínimo de la App "Finanzas del hogar" para Home Assistant.

Sirve la interfaz (index.html) y guarda los datos en /data/finanzas.json.
Solo acepta conexiones que llegan por el ingress de Home Assistant, que es
quien exige el login.
"""
import json
import os
import re
import threading
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

PORT = int(os.environ.get("PORT", "8099"))
DATA_DIR = os.environ.get("DATA_DIR", "/data")
DB_FILE = os.path.join(DATA_DIR, "finanzas.json")
APP_DIR = os.path.dirname(os.path.abspath(__file__))
INDEX = os.path.join(APP_DIR, "index.html")
# 172.30.32.2 es el gateway de ingress del Supervisor. ALLOW_ANY=1 solo para pruebas locales.
INGRESS_IPS = {"172.30.32.2", "127.0.0.1", "::1"}
ALLOW_ANY = os.environ.get("ALLOW_ANY") == "1"
PATH_RE = re.compile(r"^[A-Za-z0-9_\-.~:@+]+(/[A-Za-z0-9_\-.~:@+]+)*$")
MAX_BODY = 5 * 1024 * 1024

lock = threading.Lock()
state = {"rev": 0, "docs": {}}


def load():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, encoding="utf-8") as f:
            raw = json.load(f)
        state["rev"] = int(raw.get("rev", 0))
        state["docs"] = raw.get("docs", {})


def save():
    os.makedirs(DATA_DIR, exist_ok=True)
    tmp = DB_FILE + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False)
    os.replace(tmp, DB_FILE)


def valid_doc_path(p):
    return bool(PATH_RE.match(p)) and len(p.split("/")) % 2 == 0 and ".." not in p.split("/")


class Handler(BaseHTTPRequestHandler):
    server_version = "FinanzasHogar/1.0"

    def log_message(self, fmt, *args):  # registro breve en el log de la App
        print("%s - %s" % (self.address_string(), fmt % args), flush=True)

    # ---------- utilidades ----------
    def allowed(self):
        if ALLOW_ANY or self.client_address[0] in INGRESS_IPS:
            return True
        self.send_error(403, "Solo se accede por Home Assistant")
        return False

    def route(self):
        # Quita el prefijo de ingress si viniera y la query
        path = self.path.split("?", 1)[0]
        ing = self.headers.get("X-Ingress-Path", "")
        if ing and path.startswith(ing):
            path = path[len(ing):]
        return "/" + path.lstrip("/")

    def send_json(self, obj, code=200, extra=None):
        body = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(body)))
        for k, v in (extra or {}).items():
            self.send_header(k, v)
        self.end_headers()
        self.wfile.write(body)

    def read_json(self):
        n = int(self.headers.get("Content-Length", "0"))
        if n <= 0 or n > MAX_BODY:
            raise ValueError("cuerpo vacío o demasiado grande")
        data = json.loads(self.rfile.read(n).decode("utf-8"))
        if not isinstance(data, dict):
            raise ValueError("se esperaba un objeto JSON")
        return data

    # ---------- verbos ----------
    def do_GET(self):
        if not self.allowed():
            return
        r = self.route()
        if r in ("/", "/index.html"):
            with open(INDEX, "rb") as f:
                body = f.read()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Cache-Control", "no-cache")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        elif r == "/api/docs":
            q = self.path.split("?", 1)[1] if "?" in self.path else ""
            since = None
            m = re.search(r"since=(\d+)", q)
            if m:
                since = int(m.group(1))
            with lock:
                if since is not None and since == state["rev"]:
                    return self.send_json({"rev": state["rev"], "unchanged": True})
                return self.send_json({"rev": state["rev"], "docs": state["docs"]})
        elif r == "/api/export":
            with lock:
                out = {"formato": "finanzas-hogar", "version": 1,
                       "exportado": datetime.now().strftime("%Y-%m-%d %H:%M"), "docs": state["docs"]}
            fname = "respaldo-finanzas-%s.json" % datetime.now().strftime("%Y-%m-%d")
            self.send_json(out, extra={"Content-Disposition": 'attachment; filename="%s"' % fname})
        else:
            self.send_error(404)

    def do_PUT(self):
        if not self.allowed():
            return
        r = self.route()
        if not r.startswith("/api/doc/"):
            return self.send_error(404)
        p = r[len("/api/doc/"):]
        if not valid_doc_path(p):
            return self.send_json({"error": "ruta inválida"}, 400)
        try:
            data = self.read_json()
        except Exception as e:  # noqa: BLE001
            return self.send_json({"error": str(e)}, 400)
        with lock:
            state["docs"][p] = data
            state["rev"] += 1
            save()
            rev = state["rev"]
        self.send_json({"ok": True, "rev": rev})

    def do_DELETE(self):
        if not self.allowed():
            return
        r = self.route()
        if not r.startswith("/api/doc/"):
            return self.send_error(404)
        p = r[len("/api/doc/"):]
        if not valid_doc_path(p):
            return self.send_json({"error": "ruta inválida"}, 400)
        with lock:
            state["docs"].pop(p, None)
            state["rev"] += 1
            save()
            rev = state["rev"]
        self.send_json({"ok": True, "rev": rev})

    def do_POST(self):
        if not self.allowed():
            return
        r = self.route()
        if r != "/api/import":
            return self.send_error(404)
        try:
            data = self.read_json()
            docs = data.get("docs")
            if data.get("formato") != "finanzas-hogar" or not isinstance(docs, dict):
                raise ValueError("el archivo no es un respaldo de Finanzas del hogar")
            for k, v in docs.items():
                if not valid_doc_path(k) or not isinstance(v, dict):
                    raise ValueError("documento inválido: %s" % k)
        except Exception as e:  # noqa: BLE001
            return self.send_json({"error": str(e)}, 400)
        with lock:
            # copia de seguridad del estado anterior antes de reemplazar
            if state["docs"]:
                bak = os.path.join(DATA_DIR, "antes-de-importar-%s.json" % datetime.now().strftime("%Y%m%d-%H%M%S"))
                with open(bak, "w", encoding="utf-8") as f:
                    json.dump(state, f, ensure_ascii=False)
            state["docs"] = docs
            state["rev"] += 1
            save()
            rev = state["rev"]
        self.send_json({"ok": True, "rev": rev, "documentos": len(docs)})


if __name__ == "__main__":
    load()
    print("Finanzas del hogar escuchando en el puerto %d (datos en %s)" % (PORT, DB_FILE), flush=True)
    ThreadingHTTPServer(("0.0.0.0", PORT), Handler).serve_forever()
