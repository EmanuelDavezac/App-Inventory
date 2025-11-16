from django.shortcuts import render, redirect
from .forms import ProductoForm, RegistroForm, FacturaForm, DetalleFacturaForm
from django.db.models import Sum, F, ExpressionWrapper, DecimalField
from .models import Cliente, Proveedor, Producto, Venta
from django.contrib.auth.decorators import login_required
from .models import Cliente, Proveedor, Producto, Venta, DetalleVenta, Categoria, Factura, DetalleFactura
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.forms import inlineformset_factory
from django.db import transaction



def dashboard(request):
    clientes_count = Cliente.objects.count()
    proveedores_count = Proveedor.objects.count()
    productos_count = Producto.objects.count()
    facturas_count = Venta.objects.count() # Asumo que Venta es tu modelo Factura

    existencia_total = Producto.objects.aggregate(total=Sum('stock_actual'))['total'] or 0
    
    # (Tu lógica de DetalleVenta)
    # NOTA: Asegúrate de que 'DetalleVenta' sea el nombre correcto de tu modelo de detalles.
    existencia_vendida = DetalleVenta.objects.aggregate(total=Sum('cantidad'))['total'] or 0
    existencia_actual = max(existencia_total - existencia_vendida, 0) # Esto puede no ser preciso, el stock_actual del producto es mejor

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

    
    productos_bajo_stock = Producto.objects.filter(
        stock_actual__lte=F('stock_minimo'), 
        activo=True
    )
    count_bajo_stock = productos_bajo_stock.count()

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
        'count_bajo_stock': count_bajo_stock,
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
    fields = ['nombre', 'correo_electronico', 'telefono', 'direccion']
    success_url = reverse_lazy('cliente_list')

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        placeholders = {
            'nombre': 'Nombre completo del cliente',
            'correo_electronico': 'Correo electrónico',
            'telefono': 'Teléfono',
            'direccion': 'Dirección'
        }
        for field_name, field in form.fields.items():
            field.widget.attrs['class'] = 'form-control'
            if field_name in placeholders:
                field.widget.attrs['placeholder'] = placeholders[field_name]
        return form

# Vista para actualizar (editar) un cliente
class ClienteUpdateView(UpdateView):
    model = Cliente
    template_name = 'cliente_form.html'
    fields = ['nombre', 'correo_electronico', 'telefono', 'direccion']
    success_url = reverse_lazy('cliente_list')

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        placeholders = {
            'nombre': 'Nombre completo del cliente',
            'correo_electronico': 'Correo electrónico',
            'telefono': 'Teléfono',
            'direccion': 'Dirección'
        }
        for field_name, field in form.fields.items():
            field.widget.attrs['class'] = 'form-control'
            if field_name in placeholders:
                field.widget.attrs['placeholder'] = placeholders[field_name]
        return form

# Vista para eliminar un cliente
class ClienteDeleteView(DeleteView):
    model = Cliente
    template_name = 'cliente_confirm_delete.html'
    success_url = reverse_lazy('cliente_list')


# === VISTAS PARA PROVEEDORES ===
class ProveedorListView(ListView):
    model = Proveedor
    template_name = 'proveedor_list.html'
    context_object_name = 'proveedores'

class ProveedorCreateView(CreateView):
    model = Proveedor
    template_name = 'proveedor_form.html'
    fields = ['nombre', 'email', 'telefono', 'direccion'] # Asegúrate que el campo sea 'email'
    success_url = reverse_lazy('proveedor_list')

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        # Diccionario con los placeholders para cada campo
        placeholders = {
            'nombre': 'Nombre del proveedor',
            'email': 'Correo electrónico',
            'telefono': 'Teléfono',
            'direccion': 'Dirección'
        }
        # Recorremos los campos para agregarles la clase y el placeholder
        for field_name, field in form.fields.items():
            field.widget.attrs['class'] = 'form-control'
            if field_name in placeholders:
                field.widget.attrs['placeholder'] = placeholders[field_name]
        return form


class ProveedorUpdateView(UpdateView):
    model = Proveedor
    template_name = 'proveedor_form.html'
    fields = ['nombre', 'email', 'telefono', 'direccion'] # Asegúrate que el campo sea 'email'
    success_url = reverse_lazy('proveedor_list')

    # Replicamos la misma lógica para la vista de edición
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        placeholders = {
            'nombre': 'Nombre del proveedor',
            'email': 'Correo electrónico',
            'telefono': 'Teléfono',
            'direccion': 'Dirección'
        }
        for field_name, field in form.fields.items():
            field.widget.attrs['class'] = 'form-control'
            if field_name in placeholders:
                field.widget.attrs['placeholder'] = placeholders[field_name]
        return form

class ProveedorDeleteView(DeleteView):
    model = Proveedor
    template_name = 'proveedor_confirm_delete.html'
    success_url = reverse_lazy('proveedor_list')

# === VISTAS PARA CATEGORIAS ===
class CategoriaListView(ListView):
    model = Categoria
    template_name = 'categoria_list.html'
    context_object_name = 'categorias'

class CategoriaCreateView(CreateView):
    model = Categoria
    template_name = 'categoria_form.html'
    fields = ['nombre'] # Solo necesitamos el campo nombre
    success_url = reverse_lazy('categoria_list')

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['nombre'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Nombre de la categoría'})
        return form

class CategoriaUpdateView(UpdateView):
    model = Categoria
    template_name = 'categoria_form.html'
    fields = ['nombre']
    success_url = reverse_lazy('categoria_list')

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['nombre'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Nombre de la categoría'})
        return form

class CategoriaDeleteView(DeleteView):
    model = Categoria
    template_name = 'categoria_confirm_delete.html'
    success_url = reverse_lazy('categoria_list')

# === VISTAS PARA PRODUCTOS ===
class ProductoListView(ListView):
    model = Producto
    template_name = 'producto_list.html'
    context_object_name = 'productos'

class ProductoCreateView(CreateView):
    model = Producto
    template_name = 'producto_form.html'
    # 1. Actualizamos la lista de campos a los de tu modelo
    fields = ['nombre', 'categoria', 'unidad_medida', 'precio_unitario', 'stock_actual', 'stock_minimo', 'activo']
    success_url = reverse_lazy('producto_list')

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        # 2. Aplicamos estilos y placeholders a los campos
        form.fields['nombre'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Ej: Gaseosa Coca-Cola 2.25L'})
        form.fields['categoria'].widget.attrs.update({'class': 'form-control'})
        form.fields['unidad_medida'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Ej: unidad, kg, caja'})
        form.fields['precio_unitario'].widget.attrs.update({'class': 'form-control'})
        form.fields['stock_actual'].widget.attrs.update({'class': 'form-control'})
        form.fields['stock_minimo'].widget.attrs.update({'class': 'form-control'})
        # El campo 'activo' (booleano) se renderiza como checkbox y no necesita la clase 'form-control'
        form.fields['activo'].widget.attrs.update({'class': 'form-check-input'})
        return form

class ProductoUpdateView(UpdateView):
    model = Producto
    template_name = 'producto_form.html'
    # Hacemos lo mismo para la vista de edición
    fields = ['nombre', 'categoria', 'unidad_medida', 'precio_unitario', 'stock_actual', 'stock_minimo', 'activo']
    success_url = reverse_lazy('producto_list')

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['nombre'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Ej: Gaseosa Coca-Cola 2.25L'})
        form.fields['categoria'].widget.attrs.update({'class': 'form-control'})
        form.fields['unidad_medida'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Ej: unidad, kg, caja'})
        form.fields['precio_unitario'].widget.attrs.update({'class': 'form-control'})
        form.fields['stock_actual'].widget.attrs.update({'class': 'form-control'})
        form.fields['stock_minimo'].widget.attrs.update({'class': 'form-control'})
        form.fields['activo'].widget.attrs.update({'class': 'form-check-input'})
        return form

class ProductoDeleteView(DeleteView):
    model = Producto
    template_name = 'producto_confirm_delete.html'
    success_url = reverse_lazy('producto_list')


def FacturaCreateView(request):
    """
    Vista para crear una nueva factura con sus detalles.
    """
    
    # Creamos el 'FormSet'. Esto maneja múltiples formularios de 'DetalleFactura'
    # relacionados con UNA 'Factura'.
    # extra=1: Muestra 1 formulario de detalle vacío por defecto.
    DetalleFacturaFormSet = inlineformset_factory(
        Factura, 
        DetalleFactura, 
        form=DetalleFacturaForm, 
        extra=1, 
        can_delete=True # Permite eliminar líneas
    )

    if request.method == 'POST':
        # Si el formulario se envió...
        form = FacturaForm(request.POST)
        formset = DetalleFacturaFormSet(request.POST, prefix='detalles')

        if form.is_valid() and formset.is_valid():
            # Usamos una transacción para que si algo falla, se deshaga todo.
            # No queremos una Factura sin detalles o viceversa.
            with transaction.atomic():
                # 1. Guardar la Factura (el encabezado)
                factura = form.save(commit=False)
                factura.creado_por = request.user # Asigna el usuario logueado
                factura.total = 0 # El total se calculará después
                factura.save() # Aquí se guarda la Factura y obtiene un ID

                # 2. Guardar los Detalles (el formset)
                detalles = formset.save(commit=False)
                total_factura = 0

                for detalle in detalles:
                    
                    detalle.precio_unitario = detalle.producto.precio_unitario 
                    
                    
                    detalle.subtotal = detalle.cantidad * detalle.precio_unitario 
                    
                    
                    total_factura += detalle.subtotal
                    
                    
                    detalle.factura = factura 
                    
                    
                    detalle.save()
                
                
                factura.total = total_factura
                factura.save()

            # Redirigir a alguna parte... (ej: a la lista de facturas, que aún no creamos)
            # Por ahora, redirigimos al dashboard
            return redirect('dashboard') # ¡Asegúrate de que 'dashboard' sea un name="" válido en tus urls.py!

    else:
        # Si es un GET (primera vez que se carga la página)
        form = FacturaForm()
        formset = DetalleFacturaFormSet(prefix='detalles')

    # Preparamos el contexto para la plantilla
    context = {
        'form': form,
        'formset': formset,
        'page_title': 'Nueva Factura' # Un título para tu base.html
    }
    
    # Usamos la plantilla 'factura_form.html' (que vamos a crear ahora)
    return render(request, 'factura_form.html', context)


class FacturaListView(ListView):
    model = Factura
    template_name = 'factura_list.html'  # La plantilla que vamos a crear
    context_object_name = 'facturas'     # Cómo se llamará la lista en el HTML
    ordering = ['-fecha_emision']        # Mostrar las más nuevas primero
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Historial de Facturas'
        return context
    

class FacturaDetailView(DetailView):
    model = Factura
    template_name = 'factura_detail.html' 
    context_object_name = 'factura'       

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        context['page_title'] = f'Detalle Factura #{self.get_object().id}'
        context['detalles'] = self.get_object().detalles.all()
        return context
    

class ReporteBajoStockView(ListView):
    model = Producto
    template_name = 'reporte_bajo_stock.html'
    context_object_name = 'productos'
    
    def get_queryset(self):
        queryset = Producto.objects.filter(
            stock_actual__lte=F('stock_minimo'),
            activo=True
        )
        
        queryset = queryset.annotate(
            # faltante = stock_minimo - stock_actual
            faltante=F('stock_minimo') - F('stock_actual')
        ).order_by('stock_actual')

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Reporte de Productos con Bajo Stock'
        return context
    
