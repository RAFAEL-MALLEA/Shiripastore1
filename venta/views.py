from django.contrib import messages
from django.contrib.auth import login as auth_login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db import transaction
from django.shortcuts import render, redirect, get_object_or_404

# ANTES: todo el panel de administración (crear/editar/borrar inventario,
# categorías, plataformas, colecciones) solo exigía @login_required, es
# decir, estar AUTENTICADO. No exigía ser staff/admin. La plantilla
# administrador.html ocultaba algunos botones con un hardcode frágil
# ({% if user.username == "admin" %}), pero el enlace a "Lista de
# Inventarios" NO estaba protegido por esa condición, y de todas formas
# ocultar un botón en el HTML no protege la URL: cualquier cliente
# registrado podía entrar directo a /listar_inventario, /agregar_inventario,
# etc. y modificar el catálogo real.
# AHORA: se exige is_staff (control real en el servidor, no solo en la UI).
staff_required = user_passes_test(lambda u: u.is_staff, login_url="login")

from .carrito import Carrito
from .forms import (
    PlataformaForm, CategoriaForm, ColeccionForm, InventarioForm,
    RegistroForm, MensajeContactoForm,
)
from .models import (
    Plataforma, Categoria, Inventario, Coleccion,
    Pedido, DetallePedido, MensajeContacto,
)


# ---------------------------------------------------------------------------
# Páginas públicas
# ---------------------------------------------------------------------------

def index(request):
    return render(request, "venta/index.html")


def nosotros(request):
    """La lista de 'empresas con las que trabajamos' antes se traía por
    AJAX desde un servidor mock externo (my-json-server.typicode.com) que
    dependía de un repositorio ajeno al proyecto. Se deja como datos fijos
    renderizados por el servidor para no depender de un servicio externo
    frágil para un contenido que casi no cambia."""
    empresas = [
        {"id": 1, "nombre": "Steam", "fecha": "06/03/2023", "descripcion": "Plataforma de distribución digital de videojuegos"},
        {"id": 2, "nombre": "Epic Games", "fecha": "06/03/2023", "descripcion": "Empresa desarrolladora de videojuegos"},
        {"id": 3, "nombre": "Ubisoft", "fecha": "06/03/2023", "descripcion": "Empresa desarrolladora de videojuegos"},
        {"id": 4, "nombre": "Capcom", "fecha": "06/03/2023", "descripcion": "Empresa desarrolladora y distribuidora de videojuegos"},
        {"id": 5, "nombre": "Bethesda", "fecha": "06/03/2023", "descripcion": "Empresa dedicada a la distribución y desarrollo de videojuegos"},
    ]
    return render(request, "venta/nosotros.html", {"empresas": empresas})


def tienda(request):
    """ANTES: los productos estaban escritos a mano en el HTML y no tenían
    relación con el inventario real administrado en /administrador/.
    AHORA: se listan los juegos disponibles directamente desde la BD,
    con filtro opcional por categoría y plataforma.
    """
    productos = Inventario.objects.filter(disponible=True, stock__gt=0)

    categoria_id = request.GET.get("categoria")
    plataforma_id = request.GET.get("plataforma")
    if categoria_id:
        productos = productos.filter(Id_categoria_id=categoria_id)
    if plataforma_id:
        productos = productos.filter(Id_plataforma_id=plataforma_id)

    context = {
        "productos": productos,
        "categorias": Categoria.objects.all(),
        "plataformas": Plataforma.objects.all(),
        "categoria_sel": categoria_id,
        "plataforma_sel": plataforma_id,
    }
    return render(request, "venta/tienda.html", context)


def contacto(request):
    """ANTES: el formulario tenía action="#" method="#" y la vista solo
    hacía render(); no se guardaba ni enviaba nada.
    AHORA: se valida y se persiste en MensajeContacto (visible en /admin/).
    """
    if request.method == "POST":
        form = MensajeContactoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "¡Gracias! Recibimos tu mensaje y te contactaremos pronto.")
            return redirect("contacto")
    else:
        form = MensajeContactoForm()
    return render(request, "venta/usuario/contacto.html", {"form": form})


def formRegistro(request):
    """ANTES: el formulario tenía onsubmit="return false" y la vista nunca
    procesaba POST; el modelo 'Usuarios' quedaba siempre vacío.
    AHORA: usa el sistema de autenticación real de Django (auth_user) y
    deja al cliente con sesión iniciada tras registrarse.
    """
    if request.user.is_authenticated:
        return redirect("micuenta")

    if request.method == "POST":
        form = RegistroForm(request.POST)
        if form.is_valid():
            usuario = form.save()
            auth_login(request, usuario)
            messages.success(request, f"¡Bienvenido/a, {usuario.first_name}! Tu cuenta fue creada.")
            return redirect("index")
    else:
        form = RegistroForm()
    return render(request, "venta/usuario/formRegistro.html", {"form": form})


@login_required
def micuenta(request):
    """ANTES: 'Mi cuenta' era un formulario de login falso (action="#"
    method="get") totalmente desconectado del login real de Django.
    AHORA: requiere sesión iniciada (si no, Django redirige al login real
    en /accounts/login/) y muestra el historial de pedidos del cliente.
    """
    pedidos = request.user.pedidos.all()
    return render(request, "venta/usuario/micuenta.html", {"pedidos": pedidos})


# ---------------------------------------------------------------------------
# Carrito y checkout simulado
# ---------------------------------------------------------------------------

def carrito_ver(request):
    carrito = Carrito(request)
    return render(request, "venta/carrito.html", {
        "items": carrito.items(),
        "total": carrito.total(),
    })


def carrito_agregar(request, pk):
    if request.method == "POST":
        producto = get_object_or_404(Inventario, Id_juego=pk, disponible=True)
        try:
            cantidad = int(request.POST.get("cantidad", 1))
        except ValueError:
            cantidad = 1
        cantidad = max(1, min(cantidad, producto.stock))
        Carrito(request).agregar(producto.Id_juego, cantidad)
        messages.success(request, f"'{producto.nombre_juego}' se agregó al carrito.")
    return redirect(request.POST.get("next") or "tienda")


def carrito_actualizar(request, pk):
    if request.method == "POST":
        try:
            cantidad = int(request.POST.get("cantidad", 1))
        except ValueError:
            cantidad = 1
        Carrito(request).actualizar_cantidad(pk, cantidad)
    return redirect("carrito")


def carrito_quitar(request, pk):
    Carrito(request).quitar(pk)
    return redirect("carrito")


@login_required
def checkout(request):
    """Checkout SIMULADO: no se cobra nada ni se contacta a ninguna
    pasarela real (Webpay/Mercado Pago/Stripe). Se eligió esta opción
    explícitamente para no requerir credenciales de un proveedor de pago.
    Al "pagar" se descuenta stock real y se genera un Pedido + boleta.
    """
    carrito = Carrito(request)
    items = carrito.items()

    if not items:
        messages.warning(request, "Tu carrito está vacío.")
        return redirect("tienda")

    if request.method == "POST":
        with transaction.atomic():
            # Revalida stock al momento de pagar (puede haber cambiado).
            for item in items:
                producto = Inventario.objects.select_for_update().get(
                    Id_juego=item["producto"].Id_juego
                )
                if producto.stock < item["cantidad"]:
                    messages.error(
                        request,
                        f"Stock insuficiente para '{producto.nombre_juego}' "
                        f"(disponible: {producto.stock})."
                    )
                    return redirect("carrito")

            pedido = Pedido.objects.create(usuario=request.user, total=carrito.total())
            for item in items:
                producto = Inventario.objects.select_for_update().get(
                    Id_juego=item["producto"].Id_juego
                )
                DetallePedido.objects.create(
                    pedido=pedido,
                    inventario=producto,
                    nombre_juego=producto.nombre_juego,
                    cantidad=item["cantidad"],
                    precio_unitario=producto.valor,
                )
                producto.stock -= item["cantidad"]
                if producto.stock == 0:
                    producto.disponible = False
                producto.save()

            carrito.vaciar()
        return redirect("boleta", pedido_id=pedido.id)

    return render(request, "venta/checkout.html", {"items": items, "total": carrito.total()})


@login_required
def boleta(request, pedido_id):
    pedido = get_object_or_404(Pedido, id=pedido_id, usuario=request.user)
    return render(request, "venta/boleta.html", {"pedido": pedido})


# ---------------------------------------------------------------------------
# Panel de administración (CRUD) — requiere staff
# ---------------------------------------------------------------------------

@staff_required
def administrador(request):
    context = {
        "inventario": Inventario.objects.all(),
        "categoria": Categoria.objects.all(),
        "plataforma": Plataforma.objects.all(),
    }
    return render(request, "venta/administrador.html", context)


# --- Inventario -------------------------------------------------------------

@staff_required
def lista_inventario(request):
    buscar = request.GET.get("buscar")
    inventario = Inventario.objects.all()
    if buscar:
        inventario = inventario.filter(nombre_juego__icontains=buscar)

    context = {
        "inventario": inventario,
        "plataformas": Plataforma.objects.all(),
        "categorias": Categoria.objects.all(),
        "colecciones": Coleccion.objects.all(),
    }
    return render(request, "venta/inventario/inventario_list.html", context)


@staff_required
def agregar_inventario(request):
    """ANTES: leía campos sueltos de request.POST sin validar nada
    (incluyendo 'disponible = "1"', que no coincidía con ningún choice).
    AHORA: usa InventarioForm (ModelForm), que valida tipos y respeta
    el nuevo campo booleano 'disponible'.
    """
    if request.method == "POST":
        form = InventarioForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Se guardó el juego en el inventario.")
            return redirect("crud_inventario")
    else:
        form = InventarioForm()

    context = {
        "form": form,
        "categorias": Categoria.objects.all(),
        "plataformas": Plataforma.objects.all(),
        "colecciones": Coleccion.objects.all(),
    }
    return render(request, "venta/inventario/inventario_add.html", context)


@staff_required
def buscar_inventario(request, pk):
    inventario = get_object_or_404(Inventario, Id_juego=pk)
    if request.method == "POST":
        form = InventarioForm(request.POST, instance=inventario)
        if form.is_valid():
            form.save()
            messages.success(request, "Se actualizó el juego.")
            return redirect("crud_inventario")
    else:
        form = InventarioForm(instance=inventario)

    context = {"form": form, "inventario": inventario}
    return render(request, "venta/inventario/inventario_edit.html", context)


@staff_required
def borrar_inventario(request, pk):
    inventario = get_object_or_404(Inventario, Id_juego=pk)
    inventario.delete()
    messages.success(request, "Se eliminó el juego.")
    return redirect("crud_inventario")


# --- Plataformas -------------------------------------------------------------

@staff_required
def mostrar_plataformas(request):
    buscar = request.GET.get("buscarplat")
    plataformas = Plataforma.objects.all()
    if buscar:
        plataformas = plataformas.filter(plataforma__icontains=buscar)
    return render(request, "venta/plataforma/plataforma_list.html", {"plataformas": plataformas})


@staff_required
def agregar_plataformas(request):
    """ANTES: `if form.is_valid:` (sin paréntesis) -> siempre verdadero,
    por lo que form.save() se ejecutaba incluso con datos inválidos."""
    if request.method == "POST":
        form = PlataformaForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Se guardó la plataforma.")
            return redirect("crud_plataformas")
    else:
        form = PlataformaForm()
    return render(request, "venta/plataforma/plataforma_add.html", {"form": form})


@staff_required
def borrar_plataformas(request, pk):
    plataforma = get_object_or_404(Plataforma, Id_plataforma=pk)
    plataforma.delete()
    messages.success(request, "Plataforma eliminada.")
    return redirect("crud_plataformas")


@staff_required
def actualizar_plataforma(request, pk):
    plataforma = get_object_or_404(Plataforma, Id_plataforma=pk)
    if request.method == "POST":
        form = PlataformaForm(request.POST, instance=plataforma)
        if form.is_valid():
            form.save()
            messages.success(request, "Se actualizó la plataforma.")
            return redirect("crud_plataformas")
    else:
        form = PlataformaForm(instance=plataforma)
    return render(request, "venta/plataforma/plataforma_edit.html", {"form": form, "plataforma": plataforma})


# --- Categorías -------------------------------------------------------------

@staff_required
def mostrar_categorias(request):
    return render(request, "venta/categoria/categoria_list.html", {"categorias": Categoria.objects.all()})


@staff_required
def agregar_categorias(request):
    if request.method == "POST":
        form = CategoriaForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Se guardó la categoría.")
            return redirect("crud_categorias")
    else:
        form = CategoriaForm()
    return render(request, "venta/categoria/categoria_add.html", {"form": form})


@staff_required
def borrar_categorias(request, pk):
    categoria = get_object_or_404(Categoria, Id_categoria=pk)
    categoria.delete()
    messages.success(request, "Categoría eliminada.")
    return redirect("crud_categorias")


@staff_required
def actualizar_categoria(request, pk):
    categoria = get_object_or_404(Categoria, Id_categoria=pk)
    if request.method == "POST":
        form = CategoriaForm(request.POST, instance=categoria)
        if form.is_valid():
            form.save()
            messages.success(request, "Se actualizó la categoría.")
            return redirect("crud_categorias")
    else:
        form = CategoriaForm(instance=categoria)
    return render(request, "venta/categoria/categoria_edit.html", {"form": form, "categoria": categoria})


# --- Colecciones -------------------------------------------------------------

@staff_required
def mostrar_colecciones(request):
    return render(request, "venta/colecciones/colecciones_list.html", {"colecciones": Coleccion.objects.all()})


@staff_required
def agregar_colecciones(request):
    if request.method == "POST":
        form = ColeccionForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Se guardó la colección.")
            return redirect("crud_colecciones")
    else:
        form = ColeccionForm()
    return render(request, "venta/colecciones/colecciones_add.html", {"form": form})


@staff_required
def borrar_colecciones(request, pk):
    coleccion = get_object_or_404(Coleccion, Id_coleccion=pk)
    coleccion.delete()
    messages.success(request, "Colección eliminada.")
    return redirect("crud_colecciones")


@staff_required
def actualizar_colecciones(request, pk):
    coleccion = get_object_or_404(Coleccion, Id_coleccion=pk)
    if request.method == "POST":
        form = ColeccionForm(request.POST, instance=coleccion)
        if form.is_valid():
            form.save()
            messages.success(request, "Se actualizó la colección.")
            return redirect("crud_colecciones")
    else:
        form = ColeccionForm(instance=coleccion)
    return render(request, "venta/colecciones/colecciones_edit.html", {"form": form, "coleccion": coleccion})
