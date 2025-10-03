from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
from functools import wraps

app = Flask(__name__)
app.secret_key = "clave_secreta"

# ------------------ Conexión BD ------------------
def get_db_connection():
    conn = sqlite3.connect("ponystore.db")  # tu BD
    conn.row_factory = sqlite3.Row
    return conn

# ------------------ Decoradores ------------------
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "usuario" not in session:
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated_function

def role_required(roles):
    def wrapper(f):
        @wraps(f)
        def decorated_view(*args, **kwargs):
            if "rol" not in session or session["rol"] not in roles:
                return "Acceso denegado: permisos insuficientes"
            return f(*args, **kwargs)
        return decorated_view
    return wrapper

# ------------------ Login ------------------
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        usuario = request.form["usuario"]
        contrasena = request.form["contrasena"]

        conn = get_db_connection()
        user = conn.execute(
            "SELECT * FROM usuarios WHERE usuario=? AND contrasena=?",
            (usuario, contrasena)
        ).fetchone()
        conn.close()

        if user:
            session["usuario"] = user["usuario"]
            session["rol"] = user["rol"]
            return redirect(url_for("index"))
        else:
            return render_template("login.html", mensaje="Usuario o contraseña incorrectos")

    return render_template("login.html")

# ------------------ Registro ------------------
@app.route("/registro", methods=["GET", "POST"])
def registro():
    if request.method == "POST":
        usuario = request.form["usuario"]
        contrasena = request.form["contrasena"]

        conn = get_db_connection()
        conn.execute("INSERT INTO usuarios (usuario, contrasena, rol) VALUES (?, ?, ?)",
                     (usuario, contrasena, "user"))  # nuevos son "user"
        conn.commit()
        conn.close()
        return redirect(url_for("login"))

    return render_template("registro.html")

# ------------------ Página principal ------------------
@app.route("/index")
@login_required
def index():
    conn = get_db_connection()
    ropa = conn.execute("SELECT * FROM ropa").fetchall()
    comida = conn.execute("SELECT * FROM comida").fetchall()
    conn.close()

    return render_template("index.html",
                           usuario=session["usuario"],
                           rol=session["rol"],
                           ropa=ropa,
                           comida=comida)

# ------------------ Eliminar productos ------------------
@app.route("/delete/<categoria>/<int:item_id>")
@login_required
@role_required(["admin"])
def delete_item(categoria, item_id):
    conn = get_db_connection()
    conn.execute(f"DELETE FROM {categoria} WHERE id = ?", (item_id,))
    conn.commit()
    conn.close()
    return redirect(url_for("index"))

# ------------------ Agregar productos ------------------
@app.route("/add", methods=["POST"])
@login_required
@role_required(["admin"])
def add_item():
    categoria = request.form["categoria"]
    nombre = request.form["nombre"]
    color = request.form["color"]
    precio = request.form["precio"]
    
    conn = get_db_connection()

    if categoria == "ropa":
        talla = request.form.get("talla", "S,M,G")  # valor por defecto
        stock = request.form.get("stock", 1)        # valor por defecto
        conn.execute(
            "INSERT INTO ropa (nombre, descripcion, color, precio, talla, stock) VALUES (?, ?, ?, ?, ?, ?)",
            (nombre, "Sin descripción", color, precio, talla, stock)
        )

    elif categoria == "comida":
        stock = request.form.get("stock", 1)        # valor por defecto
        conn.execute(
            "INSERT INTO comida (nombre, descripcion, color, precio, stock) VALUES (?, ?, ?, ?, ?)",
            (nombre, "Sin descripción", color, precio, stock)
        )

    conn.commit()
    conn.close()
    return redirect(url_for("index"))

# ------------------ Logout ------------------
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(debug=True)
