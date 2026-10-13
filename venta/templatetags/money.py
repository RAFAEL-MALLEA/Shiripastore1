"""
Filtro propio para mostrar precios en formato de peso chileno ($10.000).

Se evitó depender de {% load humanize %} + intcomma porque, desde
Django 4.2, el separador de miles de TODOS los locales de la familia
español (incluido es-CL) es un espacio no separable (\xa0), y ni
siquiera definir THOUSAND_SEPARATOR en settings.py lo sobreescribe
(es un cambio de comportamiento conocido de Django, reportado en
https://code.djangoproject.com/ticket/34543). Por eso se formatea el
número a mano, con punto como separador de miles, sin pasar por el
sistema de localización de Django.
"""
from decimal import Decimal, InvalidOperation

from django import template

register = template.Library()


@register.filter(name="clp")
def clp(valor):
    """Formatea un número como pesos chilenos: sin decimales, con
    punto cada tres dígitos. Ej: 1234567 -> "1.234.567"."""
    try:
        entero = int(Decimal(valor).quantize(Decimal("1")))
    except (InvalidOperation, TypeError, ValueError):
        return valor

    signo = "-" if entero < 0 else ""
    digitos = str(abs(entero))
    grupos = []
    while digitos:
        grupos.insert(0, digitos[-3:])
        digitos = digitos[:-3]
    return signo + ".".join(grupos)
