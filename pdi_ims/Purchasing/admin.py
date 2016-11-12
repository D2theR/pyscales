from django.contrib import admin
#from import_export import resources
from django.contrib.auth.models import User

# Register your models here.
from .models import CustomerProfile, SupplierProfile, PurchaseOrder, PO_Item

class CustomerView(admin.ModelAdmin):
	def save_model(self, request, obj, form, change): 
		obj.added_by = request.user.username
		obj.save()
		
	list_display = ('name','customer_code','address_line_1','address_line_2','city','state_or_region','last_updated')

	fieldsets = [
		('Customer Profile',        {'fields': ['name', 'customer_code']}),
        ('Address Info', {'fields': ['address_line_1','address_line_2','city','state_or_region','zip_or_region_code','country','comments']}),
        ('Audit Trail', {'fields': ['added_by','last_updated'],'classes':['collaspe']}),
    ]

	search_fields = ['name','customer_code','address_line_1','address_line_2','city','state_or_region']
	readonly_fields = ('last_updated','added_by')

class SupplierView(admin.ModelAdmin):
	def save_model(self, request, obj, form, change): 
		obj.added_by = request.user.username
		obj.save()
		
	list_display = ('name','supplier_code','address_line_1','address_line_2','city','state_or_region','last_updated')

	fieldsets = [
		('Supplier Profile',        {'fields': ['name', 'supplier_code']}),
        ('Address Info', {'fields': ['address_line_1','address_line_2','city','state_or_region','zip_or_region_code','country','comments']}),
        ('Audit Trail', {'fields': ['added_by','last_updated'],'classes':['collaspe']}),
    ]

	search_fields = ['name','supplier_code','address_line_1','address_line_2','city','state_or_region']
	readonly_fields = ('last_updated','added_by')

class PO_ItemInline(admin.TabularInline):
	model = PO_Item
	fieldsets = [(None,{'fields':[('item_ordered','lot_number','lbs_ordered','lbs_received','date_received','lab_approval')]})]
	extra = 1

class PurchaseOrderAdmin(admin.ModelAdmin):
	def save_model(self, request, obj, form, change):
		obj.placed_by = request.user.username
		obj.save()
	list_select_related = ['supplier']
	list_display = ['po_number','supplier','date_ordered','placed_by','comments']
	fieldsets = [
        ('P.O. Information',{'fields': [('po_number','supplier','date_ordered', 'placed_by'),'comments']})    ]

	readonly_fields = ('date_ordered','placed_by')
	inlines = [PO_ItemInline]

admin.site.register(CustomerProfile, CustomerView)
admin.site.register(SupplierProfile, SupplierView)
admin.site.register(PurchaseOrder, PurchaseOrderAdmin)