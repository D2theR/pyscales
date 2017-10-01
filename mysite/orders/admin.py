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
	raw_id_fields = ['item_ordered']
	fieldsets = [(None,{'fields':[('item_ordered','lot_number','lbs_ordered','lbs_received','date_received','lab_approval')]})]
	extra = 1
	template = 'admin/recipes/recipeingredients/edit_inline/tabular.html'

# class PurchaseOrderAdmin(admin.ModelAdmin):
# 	list_select_related = ['ordered_from']
# 	list_display = ['po_number','ordered_from','date_ordered','comments']
# 	fieldsets = [
#         ('P.O. Information',{'fields': [('po_number','po_type','ordered_from','placed_with','date_ordered'),'comments']})    ]

# 	readonly_fields = ('date_ordered',)
# 	inlines = [PO_ItemInline]

class PurchaseOrderAdmin(admin.ModelAdmin):
	list_select_related = ['ordered_from']
	list_display = ['po_number','ordered_from','date_ordered','comments']
	fieldsets = [
        ('P.O. Information',{'fields': [('po_number','po_type','ordered_from','placed_with','date_ordered'),'comments']})    ]

	readonly_fields = ('date_ordered',)
	inlines = [PO_ItemInline]

class PO_ItemAdmin(admin.ModelAdmin):
	list_select_related = ['order_number', 'item_ordered']
	readonly_fields = ['lbs_used']
	list_display = ['order_number', 'item_ordered', 'item_status', 'lot_number', 'lbs_ordered', 'lbs_used' ,'date_received', 'lab_approval']
	search_fields = ['order_number__po_number', 'item_ordered__name', 'lot_number']
	list_filter = ['item_status', 'lab_approval']

	class Media:
		js = ['admin/js/list_filter_collaspe.js']

admin.site.register(FactoryOrder, FactoryOrderAdmin)
admin.site.register(PurchaseOrder, PurchaseOrderAdmin)
admin.site.register(PO_Item, PO_ItemAdmin)