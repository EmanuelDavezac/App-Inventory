from django import forms
from .models import Producto, Factura, DetalleFactura, Cliente
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = ['nombre', 'categoria', 'unidad_medida', 'precio_unitario', 'stock_actual', 'stock_minimo']

# inventario/forms.py
class LoginForm(forms.Form):
    username = forms.CharField(label='Usuario')
    password = forms.CharField(widget=forms.PasswordInput, label='Contraseña')
    remember_me = forms.BooleanField(required=False, label='Recuérdame')

class RegistroForm(UserCreationForm):
    username = forms.CharField(label='Usuario')
    password1 = forms.CharField(label='Contraseña', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Confirmar contraseña', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'password1', 'password2']


class FacturaForm(forms.ModelForm):
    """Formulario para el encabezado de la Factura."""
    
    # Usamos un ModelChoiceField para que el cliente sea un <select>
    cliente = forms.ModelChoiceField(
        queryset=Cliente.objects.filter(activo=True), # Asumiendo que tienes un campo 'activo'
        label="Cliente",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    class Meta:
        model = Factura
        fields = ['cliente'] # Por ahora solo necesitamos el cliente


class DetalleFacturaForm(forms.ModelForm):
    """Formulario para cada línea de producto en la factura."""
    
    # Hacemos que el producto sea un <select>
    producto = forms.ModelChoiceField(
        queryset=Producto.objects.filter(activo=True, stock_actual__gt=0),
        label="Producto",
        widget=forms.Select(attrs={'class': 'form-control producto-select'}) # 'producto-select' es para JS
    )

    cantidad = forms.IntegerField(
        label="Cantidad",
        min_value=1,
        widget=forms.NumberInput(attrs={'class': 'form-control cantidad-input', 'min': '1'}) # 'cantidad-input' para JS
    )

    class Meta:
        model = DetalleFactura
        fields = ['producto', 'cantidad']