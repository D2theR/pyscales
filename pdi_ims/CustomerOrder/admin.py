from django.contrib import admin
from django.contrib.auth.models import User
# Register your models here.
from .models import FactoryOrder, OrderItem

class OrderItemInline(admin.StackedInline):
	model = OrderItem
	readonly_fields = ('last_updated',)
	fieldsets = [(None,{'fields':[('for_customer','products_ordered','lot_number','lbs_ordered'),('date_ordered','last_updated','order_done','date_completed')]})]
	extra = 1

class FactoryOrderAdmin(admin.ModelAdmin):
    def items_on_order(self, l):
        l = []
        for f in FactoryOrder.objects.all().values():
            i = OrderItem.objects.filter(foc_number=f['id'])
            for r in i:
                x = str(r).split("|")
                l.append(x[0]+'-'+x[1])
        return " | ".join(l)

    def save_model(self, request, obj, form, change): 
        obj.placed_by = request.user.username
        obj.save()

    inlines = [OrderItemInline]

    #list_select_related = ['items_ordered']
    list_display = ['factory_order_code','requested_ship_date', 'items_on_order']
    readonly_fields = ('placed_by',)
    
    fieldsets = [
        ('Customer Order Entry',{'fields': [('factory_order_code')]}),
        ('Audit Trail', {'fields': [('ordered_by','placed_by','requested_ship_date')]})
    ]

admin.site.register(FactoryOrder, FactoryOrderAdmin)