from django.contrib import admin
# Register your models here.
from .models import InventoryItem, CompoundingChart
from django.contrib.auth.models import User

class ItemManager(admin.ModelAdmin):
	def save_model(self, request, obj, form, change):
		obj.approved_by = request.user.username
		obj.save()

	list_filter = ['category']
	list_display = ('item_unique_code','name','category','supplier','approved_by','date_approved','comments')
	#search_fields = ['user__username']
	search_fields = ['item_unique_code','name','approved_by','supplier','comments']

class CompoundChartAdmin(admin.ModelAdmin):
	def save_model(self, request, obj, form, change):
		obj.user_name = request.user.username
		obj.save()

	list_select_related = ['finished_product','raw_material']
	list_display = ['finished_product', 'raw_material', 'tare_wt', 'amount_used', 'timestamp', 'user_name']

admin.site.register(InventoryItem, ItemManager)
admin.site.register(CompoundingChart, CompoundChartAdmin)