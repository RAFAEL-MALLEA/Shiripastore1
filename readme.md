# Shiripa Store

Tienda de juegos digitales. Proyecto en **Django (Python) + SQLite + HTML/CSS/JavaScript**,
con panel de administración, catálogo, carrito de compras y checkout simulado.

> Esta es una versión reordenada y corregida de un proyecto previo. Más abajo, en
> **"Qué se corrigió y por qué"**, está el detalle completo de cada cambio.

---

## 1. Instalación

Requisitos: Python 3.10 o superior instalado (el proyecto usa Django 5.2 LTS,
que soporta Python 3.10 a 3.14).

```bash
# 1. Crear y activar un entorno virtual
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux / Mac:
source venv/bin/activate

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Configurar variables de entorno
cp .env.example .env
# (en Windows: copy .env.example .env)
# Abre .env y cambia DJANGO_SECRET_KEY por una clave propia.
# Puedes generar una con:
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

# 4. Crear la base de datos (se genera un db.sqlite3 vacío y limpio)
python manage.py migrate

# 5. Crear un usuario administrador (staff) para entrar al panel
python manage.py createsuperuser

# 6. Levantar el servidor
python manage.py runserver
```

Luego abre `http://127.0.0.1:8000/`.

- El usuario creado con `createsuperuser` puede entrar a `/admin/` (admin nativo de
  Django) y también a `/administrador/` (panel propio del proyecto: inventario,
  categorías, plataformas, colecciones).
- Cualquier persona puede registrarse como cliente desde "Crear cuenta" y comprar.

### Cargar algunos productos de prueba (opcional)

Entra a `/admin/` o a `/administrador/` con tu usuario staff y crea al menos una
Categoría, una Plataforma y una Colección antes de poder agregar un juego al
inventario (el juego depende de esas tres).

### Correr las pruebas

```bash
python manage.py test
```

---

## 2. Qué se corrigió y por qué

### 2.1 Funcionalidad que NO existía y ahora sí

| Antes | Ahora |
|---|---|
| `carrito.html` era solo una imagen "en construcción" | Carrito real basado en sesión (`venta/carrito.py`): agregar, cambiar cantidad, quitar, ver total |
| No existía ninguna pasarela de pago | **Checkout simulado** (`/checkout/`): sin cobro real, pero genera un `Pedido` + `DetallePedido`, descuenta stock y muestra una boleta con código |
| `tienda.html` tenía 11 productos escritos a mano en el HTML, sin relación con la base de datos | La tienda lista el `Inventario` real desde la BD, con filtro por categoría/plataforma |
| El formulario de registro tenía `onsubmit="return false"` y la vista nunca procesaba el `POST`; el modelo `Usuarios` quedaba siempre vacío | Registro real usando el sistema de usuarios de Django (`auth_user`), con inicio de sesión automático al registrarse |
| El formulario de contacto tenía `action="#" method="#"` | Guarda el mensaje en `MensajeContacto`, visible desde `/admin/` |
| "Mi cuenta" era un formulario de login **falso** (`action="#" method="get"`), desconectado del login real | Ahora es el panel de historial de pedidos del cliente; usa el login real de Django (`/accounts/login/`) |

### 2.2 Bugs corregidos

- **`if form.is_valid:`** (sin paréntesis) en `agregar_categorias`, `agregar_colecciones` y
  `agregar_plataformas`: al faltar los paréntesis, la condición siempre era verdadera
  (un método es "truthy"), por lo que la validación nunca se ejecutaba de verdad.
  Corregido a `if form.is_valid():` en los tres casos.
- **`Inventario.disponible`** era un `CharField` con choices `'disponible'/'no_disponible'`,
  pero el código que creaba juegos guardaba el string `"1"`, que no coincidía con ninguna
  opción válida. Se cambió a `BooleanField`, el tipo correcto.
- **Rutas duplicadas**: la app `usuarios` definía las mismas URLs que `venta` (`nosotros/`,
  `carrito/`, `tienda/`, etc.), quedando como código muerto porque `venta.urls` se incluía
  primero. Se eliminó la app `usuarios` completa (ver más abajo).

### 2.3 Falla de seguridad encontrada y corregida durante la limpieza

El panel de administración (crear/editar/borrar inventario, categorías, plataformas,
colecciones) solo exigía `@login_required`, es decir, **estar autenticado**, no ser
**staff/administrador**. La plantilla ocultaba algunos botones con un hardcode
(`{% if user.username == "admin" %}`), pero eso no protege nada del lado del servidor, y
el enlace a "Lista de Inventario" ni siquiera estaba oculto. Cualquier cliente que se
registrara podía entrar directo a `/listar_inventario`, `/agregar_inventario`, etc. y
modificar el catálogo real.

**Corrección:** todas las vistas de administración ahora usan un decorador
`staff_required` que exige `user.is_staff = True` (ver `venta/views.py`), verificado en el
servidor, no solo ocultando botones en el HTML.

### 2.4 Unificación del sistema de usuarios

El proyecto tenía **dos sistemas de usuario en paralelo**:

1. El sistema real de Django (`auth_user`), usado para el login que sí funcionaba
   (acceso al panel de administración).
2. Un modelo propio `Usuarios` (app `usuarios`), con contraseña en texto plano
   (`CharField(max_length=20)`, sin hash) y que nunca se usaba: el formulario de registro
   no lo conectaba con nada, y la tabla estaba siempre vacía.

**Se eliminó el modelo `Usuarios` y toda la app `usuarios`.** Ahora todo —administradores
y clientes— usa el sistema de autenticación de Django, con contraseñas hasheadas
correctamente (`pbkdf2_sha256`) y las vistas de registro/login reales.

### 2.5 Seguridad general (`settings.py`)

- `SECRET_KEY` ya no está escrita en el código ni versionada: se lee desde una variable
  de entorno (`DJANGO_SECRET_KEY` en `.env`, ver `.env.example`).
- `DEBUG` y `ALLOWED_HOSTS` también se leen desde variables de entorno, con valores por
  defecto seguros para desarrollo local (`DEBUG=True` solo si no se especifica otra cosa;
  **en un despliegue real, define `DJANGO_DEBUG=False` y tu dominio real en
  `DJANGO_ALLOWED_HOSTS`**).
- El `db.sqlite3` original (que tenía contraseñas reales hasheadas de dos usuarios) y
  `db.json` (datos huérfanos, no referenciados en ningún `.py` ni `.html`) se eliminaron.
  `db.sqlite3` ahora se genera vacío al correr `migrate`, y **no se versiona** (está en
  `.gitignore`).

### 2.6 Limpieza de estructura y archivos

- **`myvenv/` (79 MB) eliminado** del proyecto: un entorno virtual nunca debe
  versionarse; para eso existe `requirements.txt`.
- **Duplicación eliminada**: antes existían hasta 3-4 copias idénticas de los mismos
  archivos CSS/JS/imágenes (`CSS/`, `Javascript/`, `IMG/`, `JSON/` en la raíz, más
  `static/`, `venta/static/`, `usuarios/static/`), y las plantillas vivían duplicadas
  byte a byte en `templates/venta/` y `venta/templates/venta/`. Ahora hay una sola copia
  de cada cosa, en `venta/static/` y `venta/templates/venta/` (la ubicación estándar de
  Django para los estáticos/plantillas de una app).
- **Carpeta `main/` eliminada**: era un prototipo HTML estático anterior a la migración a
  Django, con contenido casi idéntico a las plantillas reales.
- **Plantilla base (`venta/templates/venta/base.html`) agregada**: antes el navbar y el
  footer estaban copiados y pegados en ~15 archivos HTML distintos (con enlaces
  relativos frágiles tipo `../../../contacto` que se rompían fácilmente al mover un
  archivo de carpeta). Ahora todas las páginas extienden `base.html` y usan
  `{% url 'nombre' %}` para los enlaces.
- **Dependencia externa frágil eliminada**: la sección "Empresas con las que trabajamos"
  de `nosotros.html` se llenaba por AJAX desde un servidor mock personal
  (`my-json-server.typicode.com/.../db`) usando un plugin jQuery (`$.validate`) que ni
  siquiera estaba cargado en la página. Ahora se renderiza directamente desde el
  servidor Django.
- **Código comentado y muerto eliminado**: el modelo `Boleta` comentado, funciones
  `generar_codigo_licencia()` y `save()` sin usar en `models.py`/`views.py`.
- **`.gitignore` agregado**: ignora `venv/`, `.env`, `db.sqlite3`, `__pycache__/`, etc.

### 2.7 Checkout simulado: alcance y limitaciones

Se eligió explícitamente un **checkout simulado** (no una pasarela de pago real) para no
requerir credenciales de un proveedor externo. Esto significa:

- No se realiza ningún cobro real ni se contacta a ningún proveedor de pago.
- Al "pagar" sí se valida stock real, se descuenta del inventario y se genera un pedido
  con código de boleta, visible en "Mi cuenta".
- Si más adelante quieres conectar una pasarela real (Webpay Plus, Mercado Pago, Stripe,
  etc.), la vista `checkout()` en `venta/views.py` es el único lugar que habría que
  modificar: ya deja separados el cálculo del total, la creación del pedido y el
  descuento de stock.
- El envío de productos "por correo electrónico de manera instantánea" que se menciona
  en la sección "Sobre nosotros" es únicamente texto de marketing: el proyecto no
  envía correos reales (no hay configuración SMTP). Si lo necesitas, es un paso aparte.

### 2.8 Versión de Django

Se fijó `Django==5.2.8` (rama LTS, soporte hasta ~2028) en `requirements.txt`.
La versión original de este proyecto usaba Django 4.1, que **no es compatible con
Python 3.14** (ni con versiones de Python posteriores a 3.11): intentar correrlo con
un Python más nuevo produce errores internos confusos de Django al generar la página
de depuración de errores, que tapan el error real. Si en tu máquina tienes una versión
de Python distinta, revisa la tabla oficial de compatibilidad antes de fijar otra
versión de Django: https://docs.djangoproject.com/en/dev/faq/install/

### 2.9 Qué se mantuvo igual a propósito

- El stack completo: Django, SQLite, HTML/CSS/JS, Bootstrap 5, FontAwesome.
- La estructura general del proyecto (apps `shiripaStore` + `venta`, carpetas
  `templates`/`static` dentro de la app).
- Los nombres de modelos y de la mayoría de los campos del catálogo
  (`Categoria`, `Plataforma`, `Coleccion`, `Inventario`), para no romper compatibilidad
  con el resto del código y la lógica de negocio tal como estaba pensada.
- El diseño visual (Bootstrap + `style.css` original), textos e imágenes del sitio.

---

## 3. Estructura del proyecto

```
ShiripaStore/
├── manage.py
├── requirements.txt
├── .env.example          # copiar a .env y completar
├── .gitignore
├── shiripaStore/          # configuración del proyecto Django
│   ├── settings.py
│   ├── urls.py
│   └── ...
├── templates/
│   └── registration/
│       └── login.html     # plantilla que usa el login nativo de Django
└── venta/                 # única app: catálogo, carrito, checkout, administración
    ├── models.py
    ├── forms.py
    ├── views.py
    ├── urls.py
    ├── carrito.py          # lógica del carrito (sesión)
    ├── context_processors.py
    ├── admin.py
    ├── tests.py
    ├── migrations/
    ├── static/
    │   ├── css/style.css
    │   ├── js/
    │   └── IMG/
    └── templates/venta/
        ├── base.html
        ├── index.html, tienda.html, nosotros.html, carrito.html
        ├── checkout.html, boleta.html
        ├── administrador.html
        ├── categoria/, plataforma/, colecciones/, inventario/
        └── usuario/ (contacto, formRegistro, micuenta)
```
