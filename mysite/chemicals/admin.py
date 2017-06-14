from django.contrib import admin
# Register your models here.
from .models import IngredientList, ItemPricing
from suppliers.models import SupplierProfile
from django.contrib.auth.models import User

class PricingAdmin(admin.StackedInline):
	model = ItemPricing
	extra = 1
	readonly_fields = ('date',)
	fieldsets = [
		('Pricing', {'fields':[('item', 'packaging_type', 'unit_type', 'min_qty', 'max_qty', 'price','best_price','date')]}),
		('Freight Info',{'fields':[('lead_time','fob_point', 'freight_type', 'freight_cost', 'notes')]})
	]

class IngredientAdmin(admin.ModelAdmin):
	list_select_related = ['supplier']
	list_filter = ['category', 'customer_supplied']
	list_display = ('item_code','name','category','customer_supplied','supplier','manufacturer')
	readonly_fields = ['pubchem_search','chemID_search','approved_by', 'date_approved']
	#search_fields = ['user__username']
	search_fields = ['item_code','name','chemical_name','synonyms','supplier__name','manufacturer','comments']
	fieldsets = [
		('Name Info',{'fields':[('name','chemical_name','synonyms','pubchem_search', 'chemID_search')]}),
		('Item/Chemical Info',{'fields':[('item_code','customer_supplied','category','specific_gravity','cas_number', 'comments')]}),
		('Supplier Info',{'fields':[('supplier', 'manufacturer','origin_country')]}),
		('NAFTA Info',{'fields':('nafta_tariff','nafta_last_updated')}),
		('Audit Trail & Misc.',{'classes':('collapse',),'fields':[('approved_by','date_approved')]})
	]
	inlines = [PricingAdmin]

admin.site.register(IngredientList, IngredientAdmin)