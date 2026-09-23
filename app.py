"""API REST - Tarea individual 7 (Programación Web).

Implementa el contrato de tareas y estudiantes con Flask + SQLite.
Ejecutar:  python app.py   ->   http://127.0.0.1:5000/api/
"""
import re
import sqlite3

from flask import Flask, g, jsonify, request

ESTADOS = ("pendiente", "completada")
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

app = Flask(__name__)
app.url_map.strict_slashes = False  # acepta /api/tareas y /api/tareas/
app.config["DATABASE"] = "tareas.db"

SCHEMA = """
DROP TABLE IF EXISTS tarea;
DROP TABLE IF EXISTS estudiante;

CREATE TABLE estudiante (
    id     INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    email  TEXT NOT NULL UNIQUE
);

CREATE TABLE tarea (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    titulo        TEXT NOT NULL,
    curso         TEXT NOT NULL,
    fechaEntrega  TEXT NOT NULL,
    estado        TEXT NOT NULL CHECK (estado IN ('pendiente', 'completada')),
    estudiante_id INTEGER NOT NULL
        REFERENCES estudiante(id) ON DELETE CASCADE
);

INSERT INTO estudiante (nombre, email) VALUES
    ('Ana López',   'ana@correo.com'),
    ('Luis Pérez',  'luis@correo.com'),
    ('María Gómez', 'maria@correo.com');

INSERT INTO tarea (titulo, curso, fechaEntrega, estado, estudiante_id) VALUES
    ('Ensayo de historia',      'Historia Universal', '2026-10-05', 'pendiente',  1),
    ('Práctica de laboratorio', 'Química',            '2026-09-28', 'completada', 1),
    ('Informe de física',       'Física',             '2026-10-12', 'pendiente',  2),
    ('Proyecto de programación', 'Programación Web',  '2026-10-20', 'pendiente',  3);
"""


# ---------------------------------------------------------------- base de datos
def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(app.config["DATABASE"])
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


@app.teardown_appcontext
def close_db(_exc):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    """Recrea las tablas y carga datos de ejemplo."""
    db = sqlite3.connect(app.config["DATABASE"])
    db.executescript(SCHEMA)
    db.commit()
    db.close()


# --------------------------------------------------------------------- helpers
def error(status, mensaje):
    return jsonify({"error": mensaje}), status


def json_body():
    data = request.get_json(silent=True)
    return data if isinstance(data, dict) else None


def tarea_dict(row):
    return {
        "id": row["id"],
        "titulo": row["titulo"],
        "curso": row["curso"],
        "fechaEntrega": row["fechaEntrega"],
        "estado": row["estado"],
        "estudiante_id": row["estudiante_id"],
    }


def estudiante_dict(row):
    return {"id": row["id"], "nombre": row["nombre"], "email": row["email"]}


def validar_estudiante(data):
    """Devuelve un mensaje de error o None si el body es válido."""
    if data is None:
        return "El body debe ser un JSON válido"
    nombre, email = data.get("nombre"), data.get("email")
    if not isinstance(nombre, str) or not nombre.strip():
        return "El campo 'nombre' es obligatorio"
    if not isinstance(email, str) or not EMAIL_RE.match(email.strip()):
        return "El campo 'email' es obligatorio y debe tener formato válido"
    return None


# ---------------------------------------------------------------------- tareas
@app.get("/api/tareas")
def listar_tareas():
    estado = request.args.get("estado")
    db = get_db()
    if estado is None:
        rows = db.execute("SELECT * FROM tarea ORDER BY id").fetchall()
    elif estado in ESTADOS:
        rows = db.execute(
            "SELECT * FROM tarea WHERE estado = ? ORDER BY id", (estado,)
        ).fetchall()
    else:
        return error(400, "Valor de 'estado' inválido: use pendiente o completada")
    return jsonify([tarea_dict(r) for r in rows]), 200


@app.get("/api/tareas/<int:tarea_id>")
def obtener_tarea(tarea_id):
    row = get_db().execute("SELECT * FROM tarea WHERE id = ?", (tarea_id,)).fetchone()
    if row is None:
        return error(404, f"No existe una tarea con id {tarea_id}")
    return jsonify(tarea_dict(row)), 200


@app.patch("/api/tareas/<int:tarea_id>")
def actualizar_estado_tarea(tarea_id):
    db = get_db()
    if db.execute("SELECT 1 FROM tarea WHERE id = ?", (tarea_id,)).fetchone() is None:
        return error(404, f"No existe una tarea con id {tarea_id}")

    data = json_body()
    if data is None or "estado" not in data:
        return error(400, "El body debe incluir el campo 'estado'")
    if data["estado"] not in ESTADOS:
        return error(400, "Valor de 'estado' inválido: use pendiente o completada")

    db.execute("UPDATE tarea SET estado = ? WHERE id = ?", (data["estado"], tarea_id))
    db.commit()
    row = db.execute("SELECT * FROM tarea WHERE id = ?", (tarea_id,)).fetchone()
    return jsonify(tarea_dict(row)), 200


@app.delete("/api/tareas/<int:tarea_id>")
def eliminar_tarea(tarea_id):
    db = get_db()
    cur = db.execute("DELETE FROM tarea WHERE id = ?", (tarea_id,))
    db.commit()
    if cur.rowcount == 0:
        return error(404, f"No existe una tarea con id {tarea_id}")
    return "", 204


# ----------------------------------------------------------------- estudiantes
@app.get("/api/estudiantes")
def listar_estudiantes():
    rows = get_db().execute("SELECT * FROM estudiante ORDER BY id").fetchall()
    return jsonify([estudiante_dict(r) for r in rows]), 200


@app.get("/api/estudiantes/<int:est_id>")
def obtener_estudiante(est_id):
    row = get_db().execute(
        "SELECT * FROM estudiante WHERE id = ?", (est_id,)
    ).fetchone()
    if row is None:
        return error(404, f"No existe un estudiante con id {est_id}")
    return jsonify(estudiante_dict(row)), 200


@app.post("/api/estudiantes")
def crear_estudiante():
    data = json_body()
    msg = validar_estudiante(data)
    if msg:
        return error(400, msg)

    db = get_db()
    try:
        cur = db.execute(
            "INSERT INTO estudiante (nombre, email) VALUES (?, ?)",
            (data["nombre"].strip(), data["email"].strip()),
        )
        db.commit()
    except sqlite3.IntegrityError:
        return error(409, "Ya existe un estudiante con ese email")

    row = db.execute("SELECT * FROM estudiante WHERE id = ?", (cur.lastrowid,)).fetchone()
    resp = jsonify(estudiante_dict(row))
    resp.status_code = 201
    resp.headers["Location"] = f"/api/estudiantes/{row['id']}/"
    return resp


@app.put("/api/estudiantes/<int:est_id>")
def modificar_estudiante(est_id):
    db = get_db()
    if db.execute("SELECT 1 FROM estudiante WHERE id = ?", (est_id,)).fetchone() is None:
        return error(404, f"No existe un estudiante con id {est_id}")

    data = json_body()
    msg = validar_estudiante(data)
    if msg:
        return error(400, msg)

    try:
        db.execute(
            "UPDATE estudiante SET nombre = ?, email = ? WHERE id = ?",
            (data["nombre"].strip(), data["email"].strip(), est_id),
        )
        db.commit()
    except sqlite3.IntegrityError:
        return error(409, "Ya existe un estudiante con ese email")

    row = db.execute("SELECT * FROM estudiante WHERE id = ?", (est_id,)).fetchone()
    return jsonify(estudiante_dict(row)), 200


@app.delete("/api/estudiantes/<int:est_id>")
def eliminar_estudiante(est_id):
    db = get_db()
    cur = db.execute("DELETE FROM estudiante WHERE id = ?", (est_id,))  # cascada a sus tareas
    db.commit()
    if cur.rowcount == 0:
        return error(404, f"No existe un estudiante con id {est_id}")
    return "", 204


# ------------------------------------------------------------ errores genéricos
@app.errorhandler(404)
def no_encontrado(_e):
    return error(404, "Recurso no encontrado")


@app.errorhandler(405)
def metodo_no_permitido(_e):
    return error(405, "Método HTTP no permitido para este endpoint")


if __name__ == "__main__":
    init_db()  # cada arranque deja la BD limpia con los datos de ejemplo
    app.run(debug=True)
