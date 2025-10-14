from django.urls import path
from . import views
from .views import login_view
from .views import (ClienteListView, ClienteCreateView, ClienteUpdateView, ClienteDeleteView,
                    ProveedorListView, ProveedorCreateView, ProveedorUpdateView, ProveedorDeleteView)

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
]