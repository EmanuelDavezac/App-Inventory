from django.shortcuts import render, redirect
from .models import Producto
from .forms import ProductoForm
from django.db.models import Sum
from .models import Cliente, Proveedor, Producto, Venta

def dashboard(request):
    clientes_count = Cliente.objects.count()
    proveedores_count = Proveedor.objects.count()
    productos_count = Producto.objects.count()
    facturas_count = Venta.objects.count()

    existencia_total = Producto.objects.aggregate(total=Sum('stock_actual'))['total'] or 0
    existencia_vendida = getattr(Venta.objects.aggregate(total=Sum('cantidad')), 'total', 0) or 0
    existencia_actual = max(existencia_total - existencia_vendida, 0)

    importe_vendido = Venta.objects.aggregate(total=Sum('producto'))['total'] or 0
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
    return render(request, 'inventario/listar_productos.html')

def crear_producto(request):
    if request.method == 'POST':
        form = ProductoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('listar_productos')
    else:
        form = ProductoForm()
    return render(request, 'inventario/crear_producto.html', {'form': form})

def listar_productos(request):
    productos = Producto.objects.all().order_by('nombre')
    return render(request, 'inventario/listar_productos.html', {'productos': productos})

# inventario/views.py
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from .forms import LoginForm
from django.contrib.auth.models import User

def login_view(request):
    form = LoginForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        email = form.cleaned_data['email']
        password = form.cleaned_data['password']
        remember = form.cleaned_data['remember_me']

        try:
            user = User.objects.get(email=email)
            user = authenticate(request, username=user.username, password=password)
            if user:
                login(request, user)
                if not remember:
                    request.session.set_expiry(0)  # Cierra sesión al cerrar navegador
                return redirect('listar_productos')  # Redirige al panel principal
            else:
                form.add_error(None, 'Credenciales incorrectas')
        except User.DoesNotExist:
            form.add_error('email', 'Correo no registrado')

    return render(request, 'inventario/login.html', {'form': form})

from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm

def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'register.html', {'form': form})