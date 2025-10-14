from django.db import models
from django.contrib.auth.models import AbstractUser
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