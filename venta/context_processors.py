from .carrito import Carrito


def carrito_total(request):
    """Expone la cantidad de items del carrito a todas las plantillas,
    para poder mostrar un contador junto al ícono del carrito en el navbar."""
    try:
        return {"carrito_cantidad": len(Carrito(request))}
    except Exception:
        return {"carrito_cantidad": 0}
