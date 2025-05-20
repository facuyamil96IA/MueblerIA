from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.secret_key = "supersecretkey"

# Configuración de base de datos en Render
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://muebleria_db_user:yZFvN1VuJq0lU9Y7f2KFSUuIT56ryXta@dpg-d0mg7ejuibrs73emgc6g-a.oregon-postgres.render.com/muebleria_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

ACCESS_CODE = "39776041F"

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

@app.route("/inventario", methods=["GET", "POST"])
def inventario():
    if not session.get("authenticated"):
        return redirect(url_for("login"))
    
    productos = Producto.query.all()
    return render_template("inventario.html", productos=productos)

@app.route("/agregar-producto", methods=["POST"])
def agregar_producto():
    if not session.get("authenticated"):
        return redirect(url_for("login"))
    
    nombre = request.form.get("nombre")
    descripcion = request.form.get("descripcion")
    costo = float(request.form.get("costo"))
    precio_venta = float(request.form.get("precio_venta"))
    stock = int(request.form.get("stock"))
    proveedor = request.form.get("proveedor")
    url_imagen = request.form.get("url_imagen")

    nuevo_producto = Producto(nombre=nombre, descripcion=descripcion, costo=costo,
                              precio_venta=precio_venta, stock_disponible=stock, 
                              proveedor=proveedor, url_imagen=url_imagen)

    db.session.add(nuevo_producto)
    db.session.commit()

    return redirect(url_for("inventario"))

@app.route("/registrar-compra", methods=["GET", "POST"])
def registrar_compra():
    if not session.get("authenticated"):
        return redirect(url_for("login"))

    productos = Producto.query.all()

    if request.method == "POST":
        nombre = request.form.get("nombre")
        direccion = request.form.get("direccion")
        celular = request.form.get("celular")
        producto_seleccionado = request.form.get("producto")
        modo_pago = request.form.get("modo_pago")
        bonificacion = float(request.form.get("bonificacion"))

        producto = Producto.query.filter_by(nombre=producto_seleccionado).first()
        precio_final = producto.precio_venta - bonificacion

        if modo_pago == "Tarjeta":
            precio_final *= 1.3

        nuevo_cliente = Cliente(nombre=nombre, direccion=direccion, celular=celular,
                                fecha=datetime.now(), productos=producto_seleccionado,
                                modo_pago=modo_pago, bonificacion=bonificacion, total=precio_final)

        db.session.add(nuevo_cliente)
        db.session.commit()

        return redirect(url_for("home"))

    return render_template("registrar_compra.html", productos=productos)

@app.route("/registrar-cuotas", methods=["GET", "POST"])
def registrar_cuotas():
    if not session.get("authenticated"):
        return redirect(url_for("login"))

    productos = Producto.query.all()

    if request.method == "POST":
        nombre = request.form.get("nombre")
        direccion = request.form.get("direccion")
        celular = request.form.get("celular")
        productos_seleccionados = request.form.getlist("productos")
        plan = int(request.form.get("plan"))
        cuotas_pagas = 0

        precio_total = sum([Producto.query.filter_by(nombre=p).first().precio_venta for p in productos_seleccionados])
        valor_cuotas = precio_total / plan
        cuotas_restantes = plan

        nuevo_cliente_cuotas = ClienteCuotas(nombre=nombre, direccion=direccion, celular=celular,
                                             fecha=datetime.now(), productos=", ".join(productos_seleccionados),
                                             plan=plan, valor_cuotas=valor_cuotas,
                                             cuotas_pagas=cuotas_pagas, cuotas_restantes=cuotas_restantes,
                                             saldo=precio_total)

        db.session.add(nuevo_cliente_cuotas)
        db.session.commit()

        return redirect(url_for("home"))

    return render_template("registrar_cuotas.html", productos=productos)

