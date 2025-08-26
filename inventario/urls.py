from django.urls import path
from . import views
from .views import login_view

urlpatterns = [
    path('crear/', views.crear_producto, name='crear_producto'),
    path('', views.listar_productos, name='listar_productos'),
    path('login/', login_view, name='login'),
    path('registro/', views.registro, name='registro'),
    path('dashboard/', views.dashboard, name='dashboard'),  # Nueva ruta para el dashboard  
]