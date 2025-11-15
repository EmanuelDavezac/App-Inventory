# products/signals.py
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import DetalleVenta, DetalleFactura, Producto

@receiver(post_save, sender=DetalleVenta)
def actualizar_stock_producto(sender, instance, created, **kwargs):
    """
    Actualiza el stock del producto después de que se crea un DetalleVenta.
    """
    if created: # Solo se ejecuta cuando se crea un nuevo detalle
        producto = instance.producto
        producto.stock_actual -= instance.cantidad
        producto.save()

@receiver(post_save, sender=DetalleFactura)
def actualizar_stock_post_save(sender, instance, created, **kwargs):
    """
    Señal que se dispara DESPUÉS de guardar (crear o actualizar) un DetalleFactura.
    """
    
    # El 'instance' es el objeto DetalleFactura que se acaba de guardar
    producto = instance.producto
    cantidad_vendida = instance.cantidad

    if created:
        # Si se CREÓ un nuevo detalle (nueva venta)
        producto.stock_actual -= cantidad_vendida
        print(f"STOCK: Venta de {cantidad_vendida} de {producto.nombre}. Nuevo stock: {producto.stock_actual}")
    else:
        # Si se ACTUALIZÓ un detalle existente (ej: cambió la cantidad de 2 a 3)
        # Necesitamos la cantidad ANTERIOR para hacer el ajuste
        try:
            # Obtenemos el valor 'viejo' de la base de datos
            cantidad_anterior = DetalleFactura.objects.get(id=instance.id).cantidad
        except DetalleFactura.DoesNotExist:
            cantidad_anterior = 0 # No debería pasar, pero por si acaso
            
        diferencia = cantidad_vendida - cantidad_anterior
        producto.stock_actual -= diferencia
        print(f"STOCK: Ajuste de {diferencia} de {producto.nombre}. Nuevo stock: {producto.stock_actual}")

    producto.save()


@receiver(post_delete, sender=DetalleFactura)
def reponer_stock_post_delete(sender, instance, **kwargs):
    
    # El 'instance' es el objeto DetalleFactura que se acaba de borrar
    producto = instance.producto
    cantidad_devuelta = instance.cantidad
    
    producto.stock_actual += cantidad_devuelta
    producto.save()
    print(f"STOCK: Devolución de {cantidad_devuelta} de {producto.nombre}. Nuevo stock: {producto.stock_actual}")