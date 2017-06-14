
from django.contrib import admin
from .models import CompoundingChart, ScaleManager, ScaleVerification
from django.contrib.auth.models import User

class CompoundChartAdmin(admin.ModelAdmin):
	list_select_related = ['finished_product','raw_material', 'raw_material__item_ordered']
	list_display = ['finished_product', 'raw_material', 'tare_wt', 'amount_used', 'timestamp', 'user_name']
	#list_filter = ['made_today']
	search_fields = ['finished_product__lot_number', 'raw_material__item_ordered__name','raw_material__item_ordered__item_code', 'raw_material__lot_number', 'user_name']

class ScaleManagerAdmin(admin.ModelAdmin):
	
	list_display = ['scale_number','scale_name','date_last_serviced','last_updated']
	list_filter = ['scale_number']
	search_fields = ['scale_number','scale_name']

class ScaleVerifyAdmin(admin.ModelAdmin):

	list_display = ['scale_verified','weight','user_name','date_recorded','tolerance','check_weight','verified']
	search_fields = ['scale_verified__scale_number','scale_verified__scale_name','user_name']

# Register your models here.
admin.site.register(CompoundingChart, CompoundChartAdmin)
admin.site.register(ScaleManager, ScaleManagerAdmin)
admin.site.register(ScaleVerification, ScaleVerifyAdmin)