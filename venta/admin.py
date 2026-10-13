from django.contrib import admin
from .models import (
    Inventario, Plataforma, Categoria, Coleccion,
    Pedido, DetallePedido, MensajeContacto,
)


@admin.register(Inventario)
class InventarioAdmin(admin.ModelAdmin):
    list_display = ("nombre_juego", "Id_categoria", "Id_plataforma", "valor", "stock", "disponible")
    list_filter = ("disponible", "Id_categoria", "Id_plataforma")
    search_fields = ("nombre_juego",)


admin.site.register(Plataforma)
admin.site.register(Categoria)
admin.site.register(Coleccion)


class DetallePedidoInline(admin.TabularInline):
    model = DetallePedido
    extra = 0
    readonly_fields = ("inventario", "nombre_juego", "cantidad", "precio_unitario")


@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ("codigo_boleta", "usuario", "fecha", "total", "estado")
    list_filter = ("estado", "fecha")
    search_fields = ("codigo_boleta", "usuario__username")
    inlines = [DetallePedidoInline]


@admin.register(MensajeContacto)
class MensajeContactoAdmin(admin.ModelAdmin):
    list_display = ("email", "motivo", "fecha", "atendido")
    list_filter = ("motivo", "atendido")
    search_fields = ("email", "mensaje")
