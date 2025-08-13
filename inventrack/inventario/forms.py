from django import forms
from .models import Producto

class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = ['nombre', 'categoria', 'unidad_medida', 'precio_unitario', 'stock_actual', 'stock_minimo']