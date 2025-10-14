from django.shortcuts import render, redirect
from .forms import ProductoForm, RegistroForm
from django.db.models import Sum, F, ExpressionWrapper, DecimalField
from .models import Cliente, Proveedor, Producto, Venta
from django.contrib.auth.decorators import login_required
from .models import Cliente, Proveedor, Producto, Venta, DetalleVenta, Producto
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView

def dashboard(request):
    clientes_count = Cliente.objects.count()
    proveedores_count = Proveedor.objects.count()
    productos_count = Producto.objects.count()
    facturas_count = Venta.objects.count()

    existencia_total = Producto.objects.aggregate(total=Sum('stock_actual'))['total'] or 0
    existencia_vendida = DetalleVenta.objects.aggregate(total=Sum('cantidad'))['total'] or 0
    existencia_actual = max(existencia_total - existencia_vendida, 0)

    # Corrección aquí:
    importe_vendido = DetalleVenta.objects.aggregate(
        total=Sum(
            ExpressionWrapper(
                F('cantidad') * F('precio_unitario'),
                output_field=DecimalField()
            )
        )
    )['total'] or 0

    importe_pagado = importe_vendido
    importe_restante = max(importe_vendido - importe_pagado, 0)
    beneficio_bruto = 0  
    beneficio_neto = beneficio_bruto

    ctx = {
        'clientes_count': clientes_count,
        'proveedores_count': proveedores_count,
        'productos_count': productos_count,
        'facturas_count': facturas_count,
        'existencia_total': existencia_total,
        'existencia_vendida': existencia_vendida,
        'existencia_actual': existencia_actual,
        'importe_vendido': importe_vendido,
        'importe_pagado': importe_pagado,
        'importe_restante': importe_restante,
        'beneficio_bruto': beneficio_bruto,
        'beneficio_neto': beneficio_neto,
    }
    return render(request, 'dashboard.html', ctx)

def crear_producto(request):
    if request.method == 'POST':
        form = ProductoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('listar_productos')
    else:
        form = ProductoForm()
    return render(request, 'crear_producto.html', {'form': form})

def listar_productos(request):
    productos = Producto.objects.all().order_by('nombre')
    return render(request, 'listar_productos.html', {'productos': productos})

# inventario/views.py
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from .forms import LoginForm
from django.contrib.auth.models import User

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username') # O como se llame tu campo
            password = form.cleaned_data.get('password')

            # authenticate se encarga de todo por vos
            user = authenticate(request, username=username, password=password)

            if user is not None:
                # Si el usuario es válido, lo logueamos
                login(request, user)
                return redirect('dashboard') # Redirigir a la página principal
            else:
                # Si user es None, las credenciales son incorrectas
                form.add_error(None, 'El usuario o la contraseña son incorrectos.')
    else:
        form = LoginForm()

    return render(request, 'login.html', {'form': form})


def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'registro.html', {'form': form})

def registro(request):
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')  # o redirigí al panel
    else:
        form = RegistroForm()
    return render(request, 'registro.html', {'form': form})


from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def dashboard(request):
    return render(request, 'dashboard.html')

# Vista para listar todos los clientes
class ClienteListView(ListView):
    model = Cliente
    template_name = 'cliente_list.html'
    context_object_name = 'clientes'

class ClienteCreateView(CreateView):
    model = Cliente
    template_name = 'cliente_form.html'
    fields = ['nombre', 'correo_electronico', 'telefono', 'direccion'] # Campos que aparecerán en el form
    success_url = reverse_lazy('cliente_list') # A dónde ir después de crear con éxito

# Vista para actualizar (editar) un cliente
class ClienteUpdateView(UpdateView):
    model = Cliente
    template_name = 'cliente_form.html'
    fields = ['nombre', 'correo_electronico', 'telefono', 'direccion']
    success_url = reverse_lazy('cliente_list')

# Vista para eliminar un cliente
class ClienteDeleteView(DeleteView):
    model = Cliente
    template_name = 'cliente_confirm_delete.html'
    success_url = reverse_lazy('cliente_list')

class ProveedorListView(ListView):
    model = Proveedor
    template_name = 'proveedor_list.html'
    context_object_name = 'proveedores'

class ProveedorCreateView(CreateView):
    model = Proveedor
    template_name = 'proveedor_form.html'
    fields = ['nombre', 'telefono', 'email', 'direccion']
    success_url = reverse_lazy('proveedor_list')

class ProveedorUpdateView(UpdateView):
    model = Proveedor
    template_name = 'proveedor_form.html'
    fields = ['nombre', 'telefono', 'email', 'direccion']
    success_url = reverse_lazy('proveedor_list')

class ProveedorDeleteView(DeleteView):
    model = Proveedor
    template_name = 'proveedor_confirm_delete.html'
    success_url = reverse_lazy('proveedor_list')

