from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Producto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.Text, nullable=True)
    costo = db.Column(db.Float, nullable=False)
    precio_venta = db.Column(db.Float, nullable=False)
    stock_disponible = db.Column(db.Integer, nullable=False)
    proveedor = db.Column(db.String(100), nullable=True)
    url_imagen = db.Column(db.String(255), nullable=True)

class Cliente(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    direccion = db.Column(db.String(255), nullable=False)
    celular = db.Column(db.String(50), nullable=False)
    fecha = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    productos = db.Column(db.String(255), nullable=True)
    modo_pago = db.Column(db.String(50), nullable=False)
    bonificacion = db.Column(db.Float, nullable=True)
    total = db.Column(db.Float, nullable=False)

class ClienteCuotas(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    direccion = db.Column(db.String(255), nullable=False)
    celular = db.Column(db.String(50), nullable=False)
    fecha = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    productos = db.Column(db.String(255), nullable=True)
    plan = db.Column(db.Integer, nullable=False)
    valor_cuotas = db.Column(db.Float, nullable=False)
    cuotas_pagas = db.Column(db.Integer, nullable=False, default=0)
    cuotas_restantes = db.Column(db.Integer, nullable=False)
    saldo = db.Column(db.Float, nullable=False)

class Proveedor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    direccion = db.Column(db.String(255), nullable=False)
    celular = db.Column(db.String(50), nullable=False)
    descripcion = db.Column(db.Text, nullable=True)
