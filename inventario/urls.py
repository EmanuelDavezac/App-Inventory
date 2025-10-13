from django.urls import path
from . import views
from .views import login_view
from .views import ClienteListView, ClienteCreateView, ClienteUpdateView, ClienteDeleteView

urlpatterns = [
    path('crear/', views.crear_producto, name='crear_producto'),
    path('', views.listar_productos, name='listar_productos'),
    path('login/', login_view, name='login'),
    path('registro/', views.registro, name='registro'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('clientes/', ClienteListView.as_view(), name='cliente_list'),
    # Ruta para crear un nuevo cliente
    path('clientes/nuevo/', ClienteCreateView.as_view(), name='cliente_create'),
    # Ruta para editar un cliente existente
    path('clientes/<int:pk>/editar/', ClienteUpdateView.as_view(), name='cliente_update'),
    # Ruta para eliminar un cliente
    path('clientes/<int:pk>/eliminar/', ClienteDeleteView.as_view(), name='cliente_delete'), 
]