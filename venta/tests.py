"""
ANTES el proyecto no tenía ninguna prueba automatizada real (tests.py
solo tenía el stub por defecto de Django). Se agregan pruebas mínimas
para las partes más sensibles que se corrigieron: el carrito, el
checkout simulado y que el panel de administración exija ser staff.
"""
from decimal import Decimal

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import Categoria, Plataforma, Coleccion, Inventario, Pedido


class SetupMixin:
    def setUp(self):
        self.categoria = Categoria.objects.create(categoria="Accion")
        self.plataforma = Plataforma.objects.create(plataforma="PC")
        self.coleccion = Coleccion.objects.create(coleccion="General")
        self.juego = Inventario.objects.create(
            Id_categoria=self.categoria,
            Id_plataforma=self.plataforma,
            Id_coleccion=self.coleccion,
            nombre_juego="Juego de prueba",
            valor=Decimal("10000.00"),
            stock=3,
            disponible=True,
        )
        self.cliente = User.objects.create_user(username="cliente", password="clienteClave123")
        self.staff = User.objects.create_user(username="staff", password="staffClave123", is_staff=True)


class CarritoYCheckoutTests(SetupMixin, TestCase):
    def test_tienda_muestra_inventario_real(self):
        """Antes la tienda mostraba productos hardcodeados; ahora debe
        reflejar el catálogo real de la base de datos."""
        resp = self.client.get(reverse("tienda"))
        self.assertContains(resp, "Juego de prueba")

    def test_agregar_al_carrito_y_ver_total(self):
        self.client.login(username="cliente", password="clienteClave123")
        self.client.post(
            reverse("carrito_agregar", args=[self.juego.Id_juego]),
            {"cantidad": 2},
        )
        resp = self.client.get(reverse("carrito"))
        self.assertContains(resp, "Juego de prueba")
        # Los precios se muestran como pesos chilenos: sin decimales,
        # con punto de miles (ver venta/templates: filtro floatformat:0|intcomma).
        self.assertContains(resp, "20.000")

    def test_checkout_simulado_crea_pedido_y_descuenta_stock(self):
        self.client.login(username="cliente", password="clienteClave123")
        self.client.post(reverse("carrito_agregar", args=[self.juego.Id_juego]), {"cantidad": 2})
        resp = self.client.post(reverse("checkout"))
        self.assertEqual(resp.status_code, 302)  # redirige a la boleta

        self.juego.refresh_from_db()
        self.assertEqual(self.juego.stock, 1)
        self.assertEqual(Pedido.objects.count(), 1)
        self.assertEqual(Pedido.objects.first().usuario, self.cliente)

    def test_checkout_requiere_login(self):
        resp = self.client.get(reverse("checkout"))
        self.assertEqual(resp.status_code, 302)
        self.assertIn(reverse("login"), resp.url)


class PanelAdminRequiereStaffTests(SetupMixin, TestCase):
    """Antes cualquier usuario autenticado (incluso un cliente común)
    podía entrar a /listar_inventario y modificar el catálogo, porque la
    vista solo exigía @login_required, no ser staff."""

    def test_cliente_normal_no_puede_entrar_al_crud(self):
        self.client.login(username="cliente", password="clienteClave123")
        resp = self.client.get(reverse("crud_inventario"))
        self.assertEqual(resp.status_code, 302)

    def test_staff_si_puede_entrar_al_crud(self):
        self.client.login(username="staff", password="staffClave123")
        resp = self.client.get(reverse("crud_inventario"))
        self.assertEqual(resp.status_code, 200)

    def test_formulario_invalido_no_guarda_categoria(self):
        """Antes `if form.is_valid:` (sin paréntesis) era siempre verdadero
        y podía intentar guardar datos inválidos."""
        self.client.login(username="staff", password="staffClave123")
        resp = self.client.post(reverse("categoriasAdd"), {"categoria": ""})
        self.assertEqual(resp.status_code, 200)  # vuelve a mostrar el form
        self.assertEqual(Categoria.objects.count(), 1)  # no se creó una nueva
