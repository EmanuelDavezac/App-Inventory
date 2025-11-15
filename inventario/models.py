from django.db import models
from django.contrib.auth.models import AbstractUser, User
from django.core.exceptions import ValidationError

class Categoria(models.Model):
    nombre = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre

class Producto(models.Model):
    nombre = models.CharField(max_length=100)
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE)
    unidad_medida = models.CharField(max_length=20)  # ej: unidad, kg, caja
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    stock_actual = models.IntegerField()
    stock_minimo = models.IntegerField()
    activo = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre

    def clean(self):
        # Validación para evitar stock negativo
        if self.stock_actual < 0:
            raise ValidationError('El stock actual no puede ser negativo.')

class Cliente(models.Model):
    nombre = models.CharField(max_length=100)
    telefono = models.CharField(max_length=20, blank=True)
    correo_electronico = models.CharField(max_length=255, blank=True, null=True)
    direccion = models.CharField(max_length=255, blank=True, null=True)
    activo = models.BooleanField(default=True, verbose_name="Activo")

    def __str__(self):
        return self.nombre

class Proveedor(models.Model):
    nombre = models.CharField(max_length=100)
    email = models.EmailField(blank=True, null=True)
    telefono = models.CharField(max_length=20, blank=True)
    direccion = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.nombre

class Venta(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    fecha = models.DateTimeField(auto_now_add=True)
    creado_por = models.CharField(max_length=100, blank=True, null=True)  # Auditoría
    modificado_en = models.DateTimeField(auto_now=True)  # Auditoría

    def __str__(self):
        return f"Venta a {self.cliente} - {self.fecha}"

class DetalleVenta(models.Model):
    venta = models.ForeignKey(Venta, on_delete=models.CASCADE, related_name='detalles')
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField()
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)  # Guarda el precio al momento de la venta

    def __str__(self):
        return f"{self.producto} x {self.cantidad}"

    def clean(self): # Validación para evitar vender más stock del disponible
        if self.cantidad > self.producto.stock_actual:
            from django.core.exceptions import ValidationError
            raise ValidationError('No hay suficiente stock para este producto.')
        
class Factura(models.Model):
    """
    Modelo para el encabezado de la factura.
    Contiene la info general de la transacción.
    """
    # Estados posibles de una factura
    ESTADO_CHOICES = (
        ('PAGADA', 'Pagada'),
        ('PENDIENTE', 'Pendiente'),
        ('ANULADA', 'Anulada'),
    )

    # Relación: Una factura pertenece a UN cliente.
    # on_delete=models.SET_NULL: Si borras al cliente, la factura se mantiene
    # pero el campo 'cliente' queda en Nulo. No queremos perder facturas.
    cliente = models.ForeignKey('Cliente', on_delete=models.SET_NULL, null=True, blank=True)
    
    # auto_now_add=True: Pone la fecha y hora actual SÓLO cuando se crea el registro.
    fecha_emision = models.DateTimeField(auto_now_add=True)
    
    # Usamos DecimalField para dinero. Nunca FloatField.
    # max_digits=10: Total de dígitos (antes y después del punto)
    # decimal_places=2: Dígitos después del punto
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    # Campo para guardar el estado, usando las 'choices' de arriba.
    estado = models.CharField(max_length=10, choices=ESTADO_CHOICES, default='PENDIENTE')
    
    # (Opcional) Quién la registró en el sistema
    creado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='facturas_creadas')

    def __str__(self):
        # Texto que aparecerá en el Admin de Django
        return f"Factura #{self.id} - {self.cliente.nombre if self.cliente else 'Sin Cliente'} - ${self.total}"

    class Meta:
        verbose_name = "Factura"
        verbose_name_plural = "Facturas"


class DetalleFactura(models.Model):
    """
    Modelo para los ítems (renglones) dentro de una factura.
    Cada producto en la factura es un registro aquí.
    """
    
    # Relación: El detalle pertenece a UNA factura.
    # related_name='detalles': Nos permitirá hacer 'factura.detalles.all()'
    # on_delete=models.CASCADE: Si se borra la factura, se borran sus detalles. Lógico.
    factura = models.ForeignKey(Factura, related_name='detalles', on_delete=models.CASCADE)
    
    # Relación: El detalle apunta a UN producto.
    # on_delete=models.SET_NULL: Si borras el producto de tu inventario,
    # el detalle de la factura no se borra, solo queda "Sin producto".
    producto = models.ForeignKey('Producto', on_delete=models.SET_NULL, null=True)
    
    # Cantidad que se vendió
    cantidad = models.PositiveIntegerField(default=1)
    
    # ¡IMPORTANTE! Copiamos el precio al momento de la venta.
    # No enlazamos al precio del producto, porque si ese precio cambia,
    # el precio en esta factura histórica NO debe cambiar.
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    
    # El subtotal (cantidad * precio_unitario)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.cantidad} x {self.producto.nombre if self.producto else 'Producto Eliminado'}"

    def save(self, *args, **kwargs):
        # Lógica de negocio:
        # 1. Copiamos el precio actual del producto al crear el detalle
        if not self.id: # Solo al crear
            self.precio_unitario = self.producto.precio_unitario
            
        # 2. (Re)calculamos el subtotal siempre
        self.subtotal = self.cantidad * self.precio_unitario
        
        super().save(*args, **kwargs)
        
        # 3. (Opcional pero recomendado) Actualizar el total en la factura
        #    Podríamos hacer esto aquí o mejor con un 'signal' (lo vemos luego).
        #    Por ahora, lo dejamos así para no complicarlo.

    class Meta:
        verbose_name = "Detalle de Factura"
        verbose_name_plural = "Detalles de Factura"