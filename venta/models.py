from django.db import models
from django.conf import settings
from django.utils import timezone
import random
import string


# ---------------------------------------------------------------------------
# Catálogo
# ---------------------------------------------------------------------------

class Categoria(models.Model):
    Id_categoria = models.AutoField(db_column='idCategoria', primary_key=True)
    categoria = models.CharField(unique=True, max_length=50)

    class Meta:
        verbose_name_plural = "Categorías"
        ordering = ["categoria"]

    def __str__(self):
        return str(self.categoria)


class Plataforma(models.Model):
    Id_plataforma = models.AutoField(db_column='idPlataforma', primary_key=True)
    plataforma = models.CharField(unique=True, max_length=50)

    class Meta:
        verbose_name_plural = "Plataformas"
        ordering = ["plataforma"]

    def __str__(self):
        return str(self.plataforma)


class Coleccion(models.Model):
    Id_coleccion = models.AutoField(db_column='idColeccion', primary_key=True)
    coleccion = models.CharField(unique=True, max_length=100)

    class Meta:
        verbose_name_plural = "Colecciones"
        ordering = ["coleccion"]

    def __str__(self):
        return str(self.coleccion)


class Inventario(models.Model):
    """Catálogo de juegos a la venta.

    NOTA DE CORRECCIÓN: antes 'disponible' era un CharField con choices
    ('disponible'/'no_disponible'), pero el código que creaba registros
    guardaba el string "1", que no coincidía con ninguna opción válida.
    Se reemplaza por un BooleanField, que es el tipo correcto y evita esa
    inconsistencia de datos.
    """
    Id_juego = models.AutoField(primary_key=True)
    Id_categoria = models.ForeignKey(
        Categoria, on_delete=models.CASCADE, db_column='idCategoria',
        related_name="juegos"
    )
    Id_plataforma = models.ForeignKey(
        Plataforma, on_delete=models.CASCADE, db_column='idPlataforma',
        related_name="juegos"
    )
    Id_coleccion = models.ForeignKey(
        Coleccion, on_delete=models.CASCADE, db_column='idColeccion',
        related_name="juegos"
    )
    nombre_juego = models.CharField(max_length=60)
    valor = models.DecimalField(max_digits=8, decimal_places=2)
    stock = models.PositiveIntegerField(default=100)
    disponible = models.BooleanField(default=True)
    imagen = models.CharField(
        max_length=150, blank=True,
        help_text="Nombre del archivo dentro de venta/static/IMG/"
    )

    class Meta:
        verbose_name_plural = "Inventario"
        ordering = ["nombre_juego"]

    def __str__(self):
        return f"{self.nombre_juego} ({self.Id_plataforma})"

    def en_stock(self):
        return self.disponible and self.stock > 0


# ---------------------------------------------------------------------------
# Pedido / Checkout simulado
#
# No existía NINGÚN modelo de carrito, pedido o pago en el proyecto
# original. El carrito en sí se maneja en la sesión de Django (ver
# venta/carrito.py) y solo se persiste en estas tablas cuando el cliente
# confirma la compra (checkout simulado, sin cobro real).
# ---------------------------------------------------------------------------

def generar_codigo_boleta():
    caracteres = string.ascii_uppercase + string.digits
    return "SHP-" + "".join(random.choices(caracteres, k=8))


class Pedido(models.Model):
    ESTADO_CHOICES = (
        ("pagado_simulado", "Pago simulado aprobado"),
        ("cancelado", "Cancelado"),
    )

    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="pedidos"
    )
    codigo_boleta = models.CharField(
        max_length=20, unique=True, default=generar_codigo_boleta, editable=False
    )
    fecha = models.DateTimeField(default=timezone.now)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    estado = models.CharField(
        max_length=20, choices=ESTADO_CHOICES, default="pagado_simulado"
    )

    class Meta:
        ordering = ["-fecha"]

    def __str__(self):
        return f"Pedido {self.codigo_boleta} - {self.usuario}"


class DetallePedido(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name="detalles")
    inventario = models.ForeignKey(Inventario, on_delete=models.PROTECT)
    nombre_juego = models.CharField(max_length=60)  # snapshot al momento de comprar
    cantidad = models.PositiveIntegerField(default=1)
    precio_unitario = models.DecimalField(max_digits=8, decimal_places=2)

    def subtotal(self):
        return self.cantidad * self.precio_unitario

    def __str__(self):
        return f"{self.cantidad} x {self.nombre_juego}"


# ---------------------------------------------------------------------------
# Contacto
#
# El formulario de contacto original no guardaba ni enviaba nada
# (action="#", method="#"). Se agrega un modelo simple para que los
# mensajes queden registrados y sean visibles desde /admin/.
# No se envía correo real porque el proyecto no trae credenciales SMTP.
# ---------------------------------------------------------------------------

class MensajeContacto(models.Model):
    MOTIVO_CHOICES = (
        ("soporte", "Soporte técnico"),
        ("reclamo", "Reclamo"),
        ("sugerencia", "Sugerencia"),
        ("otro", "Otro"),
    )

    email = models.EmailField()
    motivo = models.CharField(max_length=20, choices=MOTIVO_CHOICES)
    mensaje = models.TextField(max_length=500)
    fecha = models.DateTimeField(auto_now_add=True)
    atendido = models.BooleanField(default=False)

    class Meta:
        ordering = ["-fecha"]

    def __str__(self):
        return f"{self.email} - {self.get_motivo_display()}"
