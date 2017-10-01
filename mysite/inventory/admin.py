from django.contrib import admin
from django.contrib.admin.views.main import ChangeList
from django.db.models import Sum
from .models import CompoundingChart, ScaleManager, ScaleVerification
from django.contrib.auth.models import User

class MyChangeList(ChangeList):

    def get_results(self, *args, **kwargs):
        super(MyChangeList, self).get_results(*args, **kwargs)
        q = self.result_list.aggregate(amount_sum=Sum('amount_used'))
        self.amount_used = q['amount_sum']

class CompoundChartAdmin(admin.ModelAdmin):
	change_list_template = 'admin/inventory/change_list.html'

	# def get_total(self):
	# 	#functions to calculate whatever you want...
	# 	total = CompoundingChart.objects.all().aggregate(Sum('amount_used'))
	# 	return total

	# def changelist_view(self, request, extra_context=None):
	# 	my_context = {'total': self.get_total()}
	# 	return super(CompoundChartAdmin, self).changelist_view(request, extra_context=my_context)

	def get_changelist(self, request):
		return MyChangeList

	class Meta:
		model = CompoundingChart

	list_select_related = ['finished_product','raw_material', 'raw_material__item_ordered']
	list_display = ['finished_product', 'raw_material', 'tare_wt', 'amount_used', 'timestamp', 'user_name']
	#list_filter = ['made_today']
	search_fields = ['finished_product__lot_number', 'raw_material__item_ordered__name','raw_material__item_ordered__item_code', 'raw_material__lot_number', 'user_name']
	#actions = [changelist_view]

#CompoundChartAdmin.changelist_view.short_description = "Update Totals"

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