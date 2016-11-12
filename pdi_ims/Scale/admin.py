from django.contrib import admin
# from import_export import resources
# from import_export.admin import ImportExportActionModelAdmin

# Register your models here.
from django.contrib.auth.models import User
from .models import ScaleManager,ScaleVerification

class ScaleManagerAdmin(admin.ModelAdmin):
	def save_model(self, request, obj, form, change):
		obj.added_by = request.user.username
		obj.save()
	
	list_display = ['scale_number','scale_name','date_last_serviced','added_by','last_updated']
	search_fields = ['scale_number','scale_name','added_by']

class ScaleVerifyAdmin(admin.ModelAdmin):
	def save_model(self, request, obj, form, change):
		obj.user_name = request.user.username
		obj.save()
	list_display = ['scale_verified','weight','user_name','date_recorded','tolerance','check_weight','verified']
	search_fields = ['scale_verified__scale_number','scale_verified__scale_name','user_name']

admin.site.register(ScaleManager, ScaleManagerAdmin)
admin.site.register(ScaleVerification, ScaleVerifyAdmin)