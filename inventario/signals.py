# products/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import DetalleVenta

@receiver(post_save, sender=DetalleVenta)
def actualizar_stock_producto(sender, instance, created, **kwargs):
    """
    Actualiza el stock del producto después de que se crea un DetalleVenta.
    """
    if created: # Solo se ejecuta cuando se crea un nuevo detalle
        producto = instance.producto
        producto.stock_actual -= instance.cantidad
        producto.save()