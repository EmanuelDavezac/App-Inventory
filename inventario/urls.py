from django.urls import path
from . import views
from .views import login_view
from .views import (ClienteListView, ClienteCreateView, ClienteUpdateView, ClienteDeleteView,
                    ProveedorListView, ProveedorCreateView, ProveedorUpdateView, ProveedorDeleteView,
                    CategoriaListView, CategoriaCreateView, CategoriaUpdateView, CategoriaDeleteView,
                    ProductoListView, ProductoCreateView, ProductoUpdateView, ProductoDeleteView)

urlpatterns = [
    path('crear/', views.crear_producto, name='crear_producto'),
    path('', views.listar_productos, name='listar_productos'),
    path('login/', login_view, name='login'),
    path('registro/', views.registro, name='registro'),
    path('dashboard/', views.dashboard, name='dashboard'),

    path('clientes/', ClienteListView.as_view(), name='cliente_list'),
    path('clientes/nuevo/', ClienteCreateView.as_view(), name='cliente_create'),
    path('clientes/<int:pk>/editar/', ClienteUpdateView.as_view(), name='cliente_update'),
    path('clientes/<int:pk>/eliminar/', ClienteDeleteView.as_view(), name='cliente_delete'), 

    path('proveedores/', ProveedorListView.as_view(), name='proveedor_list'),
    path('proveedores/nuevo/', ProveedorCreateView.as_view(), name='proveedor_create'),
    path('proveedores/<int:pk>/editar/', ProveedorUpdateView.as_view(), name='proveedor_update'),
    path('proveedores/<int:pk>/eliminar/', ProveedorDeleteView.as_view(), name='proveedor_delete'),

    path('categorias/', CategoriaListView.as_view(), name='categoria_list'),
    path('categorias/nueva/', CategoriaCreateView.as_view(), name='categoria_create'),
    path('categorias/<int:pk>/editar/', CategoriaUpdateView.as_view(), name='categoria_update'),
    path('categorias/<int:pk>/eliminar/', CategoriaDeleteView.as_view(), name='categoria_delete'),

    path('productos/', ProductoListView.as_view(), name='producto_list'),
    path('productos/nuevo/', ProductoCreateView.as_view(), name='producto_create'),
    path('productos/<int:pk>/editar/', ProductoUpdateView.as_view(), name='producto_update'),
    path('productos/<int:pk>/eliminar/', ProductoDeleteView.as_view(), name='producto_delete'),
]