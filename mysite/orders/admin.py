from django.contrib import admin
from django.contrib.auth.models import User
from .models import FactoryOrder, OrderItem, PurchaseOrder, PO_Item
# Register your models here.

class OrderItemInline(admin.StackedInline):
	model = OrderItem
	fieldsets = [(None,{'fields':[('products_ordered','ship_to','lot_number','lbs_ordered'),('date_ordered','order_done','date_completed')]})]
	extra = 1

class FactoryOrderAdmin(admin.ModelAdmin):
    inlines = [OrderItemInline]
    #list_select_related = ['items_ordered']
    list_display = ['factory_order_code', 'ordered_by','items_on_order', 'requested_ship_date']
    list_filter = ['order_type']
    fieldsets = [
        ('Customer Order Entry',{'fields': [('factory_order_code', 'order_type')]}),
        ('Audit Trail', {'fields': [('bill_to','ordered_by','requested_ship_date')]})
    ]

class PO_ItemInline(admin.TabularInline):
	model = PO_Item
	fieldsets = [(None,{'fields':[('item_ordered','lot_number','lbs_ordered','lbs_received','date_received','lab_approval')]})]
	extra = 1

class PurchaseOrderAdmin(admin.ModelAdmin):
	list_select_related = ['ordered_from']
	list_display = ['po_number','ordered_from','date_ordered','comments']
	fieldsets = [
        ('P.O. Information',{'fields': [('po_number','po_type','ordered_from','placed_with','date_ordered'),'comments']})    ]

	readonly_fields = ('date_ordered',)
	inlines = [PO_ItemInline]

admin.site.register(FactoryOrder, FactoryOrderAdmin)
admin.site.register(PurchaseOrder, PurchaseOrderAdmin)