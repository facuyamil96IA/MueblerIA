import firebase_admin
import os
from firebase_admin import credentials, firestore
from flask import Flask, render_template, request, redirect, url_for, session
from datetime import datetime

# Inicializar la aplicación Flask
app = Flask(__name__)
app.secret_key = "supersecretkey"

# Inicializar Firebase con credenciales JSON
cred = credentials.Certificate("red.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

# Código de acceso
ACCESS_CODE = "39776041F"

# ---------------- AUTENTICACIÓN ----------------
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        codigo = request.form.get("codigo")
        if codigo == ACCESS_CODE:
            session["authenticated"] = True
            return redirect(url_for("home"))
        else:
            return render_template("login.html", error="Código incorrecto")
    return render_template("login.html")

@app.route("/home")
def home():
    if not session.get("authenticated"):
        return redirect(url_for("login"))
    return render_template("home.html")

# ---------------- INVENTARIO ----------------
@app.route("/inventario", methods=["GET", "POST"])
def inventario():
    if not session.get("authenticated"):
        return redirect(url_for("login"))

    productos_ref = db.collection("productos").stream()
    productos = [producto.to_dict() for producto in productos_ref]

    return render_template("inventario.html", productos=productos)

@app.route("/agregar-producto", methods=["POST"])
def agregar_producto():
    if not session.get("authenticated"):
        return redirect(url_for("login"))

    producto_data = {
        "nombre": request.form.get("nombre"),
        "descripcion": request.form.get("descripcion"),
        "costo": float(request.form.get("costo")),
        "precio_venta": float(request.form.get("precio_venta")),
        "stock_disponible": int(request.form.get("stock")),
        "proveedor": request.form.get("proveedor"),
        "url_imagen": request.form.get("url_imagen"),
    }

    db.collection("productos").add(producto_data)

    return redirect(url_for("inventario"))

# ---------------- REGISTRAR COMPRA ----------------
@app.route("/registrar-compra", methods=["GET", "POST"])
def registrar_compra():
    if not session.get("authenticated"):
        return redirect(url_for("login"))

    productos_ref = db.collection("productos").stream()
    productos = [producto.to_dict() for producto in productos_ref]

    if request.method == "POST":
        nombre = request.form.get("nombre")
        direccion = request.form.get("direccion")
        celular = request.form.get("celular")
        producto_seleccionado = request.form.get("producto")
        modo_pago = request.form.get("modo_pago")
        bonificacion = float(request.form.get("bonificacion"))

        producto_ref = db.collection("productos").where("nombre", "==", producto_seleccionado).stream()
        producto = next(producto_ref, None)

        if producto:
            precio_final = producto.get("precio_venta") - bonificacion
            if modo_pago == "Tarjeta":
                precio_final *= 1.3

            cliente_data = {
                "nombre": nombre,
                "direccion": direccion,
                "celular": celular,
                "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "producto": producto_seleccionado,
                "modo_pago": modo_pago,
                "bonificacion": bonificacion,
                "total": precio_final,
            }

            db.collection("clientes").add(cliente_data)

        return redirect(url_for("home"))

    return render_template("registrar_compra.html", productos=productos)

# ---------------- REGISTRAR COMPRA CON CUOTAS ----------------
@app.route("/registrar-cuotas", methods=["GET", "POST"])
def registrar_cuotas():
    if not session.get("authenticated"):
        return redirect(url_for("login"))

    productos_ref = db.collection("productos").stream()
    productos = [producto.to_dict() for producto in productos_ref]

    if request.method == "POST":
        nombre = request.form.get("nombre")
        direccion = request.form.get("direccion")
        celular = request.form.get("celular")
        productos_seleccionados = request.form.getlist("productos")
        plan = int(request.form.get("plan"))
        cuotas_pagas = 0

        precio_total = sum(
            [producto.get("precio_venta") for producto in productos if producto["nombre"] in productos_seleccionados]
        )
        valor_cuotas = precio_total / plan
        cuotas_restantes = plan

        cliente_cuotas_data = {
            "nombre": nombre,
            "direccion": direccion,
            "celular": celular,
            "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "productos": productos_seleccionados,
            "plan": plan,
            "valor_cuotas": valor_cuotas,
            "cuotas_pagas": cuotas_pagas,
            "cuotas_restantes": cuotas_restantes,
            "saldo": precio_total,
        }

        db.collection("clientes_cuotas").add(cliente_cuotas_data)

        return redirect(url_for("home"))

    return render_template("registrar_cuotas.html", productos=productos)

# ---------------- EJECUCIÓN ----------------
port = int(os.getenv("PORT", 5000))

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=port)
    app.run(debug=True)
