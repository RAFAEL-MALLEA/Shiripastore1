from django.urls import path
from . import views

urlpatterns = [
    # --- Público ---
    path('', views.index, name='index'),
    path('index/', views.index, name='index'),
    path('nosotros/', views.nosotros, name='nosotros'),
    path('tienda/', views.tienda, name='tienda'),
    path('contacto/', views.contacto, name='contacto'),
    path('formRegistro/', views.formRegistro, name='formRegistro'),
    path('micuenta/', views.micuenta, name='micuenta'),

    # --- Carrito / checkout simulado ---
    path('carrito/', views.carrito_ver, name='carrito'),
    path('carrito/agregar/<int:pk>/', views.carrito_agregar, name='carrito_agregar'),
    path('carrito/actualizar/<int:pk>/', views.carrito_actualizar, name='carrito_actualizar'),
    path('carrito/quitar/<int:pk>/', views.carrito_quitar, name='carrito_quitar'),
    path('checkout/', views.checkout, name='checkout'),
    path('boleta/<int:pedido_id>/', views.boleta, name='boleta'),

    # --- Panel de administración ---
    path('administrador/', views.administrador, name='administrador'),

    path('listar_plataformas', views.mostrar_plataformas, name='crud_plataformas'),
    path('agregar_plataformas', views.agregar_plataformas, name='plataformasAdd'),
    path('borrar_plataformas/<str:pk>', views.borrar_plataformas, name='plataformas_del'),
    path('actualizar_plataformas/<str:pk>', views.actualizar_plataforma, name='plataformas_edit'),

    path('listar_categorias', views.mostrar_categorias, name='crud_categorias'),
    path('agregar_categorias', views.agregar_categorias, name='categoriasAdd'),
    path('borrar_categorias/<str:pk>', views.borrar_categorias, name='categorias_del'),
    path('actualizar_categorias/<str:pk>', views.actualizar_categoria, name='categorias_edit'),

    path('listar_colecciones', views.mostrar_colecciones, name='crud_colecciones'),
    path('agregar_colecciones', views.agregar_colecciones, name='coleccionesAdd'),
    path('borrar_colecciones/<str:pk>', views.borrar_colecciones, name='colecciones_del'),
    path('actualizar_colecciones/<str:pk>', views.actualizar_colecciones, name='colecciones_edit'),

    path('listar_inventario', views.lista_inventario, name='crud_inventario'),
    path('agregar_inventario', views.agregar_inventario, name='inventarioAdd'),
    path('buscar_inventario/<str:pk>', views.buscar_inventario, name='inventarioFindEdit'),
    path('borrar_inventario/<str:pk>', views.borrar_inventario, name='inventario_del'),
]
