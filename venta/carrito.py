"""
Carrito de compras basado en sesión de Django.

No existía ningún carrito en el proyecto original (carrito.html era solo
una imagen de "en construcción"). Se implementa aquí con la sesión en vez
de un modelo de BD porque un carrito "vivo" (antes de pagar) es estado
temporal por usuario/navegador; solo se escribe a la base de datos
(Pedido/DetallePedido) cuando el usuario confirma la compra en el checkout.
"""
from decimal import Decimal
from .models import Inventario

SESSION_KEY = "carrito"


class Carrito:
    def __init__(self, request):
        self.session = request.session
        carrito = self.session.get(SESSION_KEY)
        if carrito is None:
            carrito = self.session[SESSION_KEY] = {}
        self.carrito = carrito

    def agregar(self, inventario_id, cantidad=1):
        inventario_id = str(inventario_id)
        cantidad_actual = self.carrito.get(inventario_id, 0)
        self.carrito[inventario_id] = cantidad_actual + cantidad
        self.guardar()

    def actualizar_cantidad(self, inventario_id, cantidad):
        inventario_id = str(inventario_id)
        if cantidad <= 0:
            self.quitar(inventario_id)
            return
        self.carrito[inventario_id] = cantidad
        self.guardar()

    def quitar(self, inventario_id):
        inventario_id = str(inventario_id)
        if inventario_id in self.carrito:
            del self.carrito[inventario_id]
            self.guardar()

    def vaciar(self):
        self.session[SESSION_KEY] = {}
        self.guardar()

    def guardar(self):
        self.session[SESSION_KEY] = self.carrito
        self.session.modified = True

    def __len__(self):
        return sum(self.carrito.values())

    def items(self):
        """Devuelve la lista de items con sus datos de producto ya resueltos
        contra la base de datos (y respetando el stock real actual)."""
        ids = self.carrito.keys()
        productos = Inventario.objects.filter(Id_juego__in=ids)
        resultado = []
        for producto in productos:
            cantidad = self.carrito[str(producto.Id_juego)]
            subtotal = producto.valor * cantidad
            resultado.append({
                "producto": producto,
                "cantidad": cantidad,
                "subtotal": subtotal,
            })
        return resultado

    def total(self):
        return sum((item["subtotal"] for item in self.items()), Decimal("0.00"))
