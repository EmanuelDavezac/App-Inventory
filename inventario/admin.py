from django.contrib import admin
from .models import Producto, Categoria, Factura, DetalleFactura, Cliente

admin.site.register(Producto)
admin.site.register(Categoria)


class DetalleFacturaInline(admin.TabularInline):
    """
    Esto nos permite agregar y editar los 'DetalleFactura'
    directamente desde el formulario de 'Factura'.
    """
    model = DetalleFactura
    extra = 1  # Cuántos formularios vacíos mostrar (ej: para agregar 1 producto)
    # (Opcional) Campos que no quieres que se editen aquí
    readonly_fields = ('subtotal',) 
    
    # (Opcional) Para que 'producto' sea un buscador y no un dropdown gigante
    # raw_id_fields = ('producto',) 


@admin.register(Factura)
class FacturaAdmin(admin.ModelAdmin):
    list_display = ('id', 'cliente', 'fecha_emision', 'total', 'estado')
    list_filter = ('estado', 'fecha_emision')
    search_fields = ('id', 'cliente__nombre')
    
    # Campos que se calculan o no deben ser editados directamente
    readonly_fields = ('fecha_emision', 'total')
    
    # Aquí "incrustamos" el inline de los detalles
    inlines = [DetalleFacturaInline]

    def save_model(self, request, obj, form, change):
        # Asignar el usuario actual al crear
        if not obj.pk: # Si es un objeto nuevo
            obj.creado_por = request.user
        super().save_model(request, obj, form, change)

    def save_formset(self, request, form, formset, change):
        # Al guardar los inlines (los detalles), recalculamos el total de la factura
        instances = formset.save(commit=False)
        total_factura = 0
        for instance in instances:
            # Nos aseguramos de guardar cada instancia primero
            instance.save()
            total_factura += instance.subtotal
        
        # Si también se guardaron detalles eliminados, los descontamos
        for obj in formset.deleted_objects:
             total_factura -= obj.subtotal

        # Guardamos el total en la factura principal
        form.instance.total = total_factura
        form.instance.save()
        formset.save_m2m()