from django.contrib import admin
from io import BytesIO
from django.http import HttpResponse
from django.db.models import Sum, Max, F
from django.views.generic import View
from datetime import datetime, date
from .models import LabSample, DesignPlan
from recipes.models import RecipeControl, RecipeIngredients
from chemicals.models import IngredientList, ItemPricing
from .utils import render_to_pdf
from django.utils.html import format_html, mark_safe
#import django_tables2 as tables
#from django_tables2 import A

### Admin Actions - Drop-down menu of change_list
### NOTE: 'tables.Table' class objects are used for rendering django_tables2 html tables when
### generating PDFs through the utils.py file.

def mark_sent(modeladmin, request, queryset):
		d = date.today()
		queryset.update(date_sent=d)

### HTML TABLES created through django_tables2.
# def sum_column(table):
# 	try:
# 		s = sum(i.recipe_weight for i in table.data)
# 		#print('total:', s)
# 	except Exception as e:
# 		print(str(e))
# 		raise e
# 	return s


# class IngredientTable(tables.Table):
# 	def __init__(self, *args, **kwargs):
# 		super(IngredientTable, self).__init__(*args, **kwargs)

# 	iuc_num = tables.Column(footer=' ',verbose_name="IUC #", accessor=A("ingredient.item_code"))
# 	ingredient = tables.Column(footer=' ')
# 	supplier = tables.Column(footer='Totals: ', accessor=A('ingredient.supplier'))
# 	item_price = tables.Column(footer=' ', verbose_name="Cost($)")
# 	ext_price = tables.Column(footer=' ', verbose_name="Cost($/%)", accessor=A('ext_price'))
# 	percentage = tables.Column(footer=' ',verbose_name="(%)")
# 	recipe_weight = tables.Column(footer=lambda table: sum(x.recipe_weight for x in table.data))
# 	SPG = tables.Column(footer=' ')
	
# 	def render_ingredient(self, value):
# 		return "%s" %str(value).split('|')[1]
# 	def render_supplier(self, value):
# 		return "%s | %s, %s" %(str(value).split('|')[0], str(value).split('|')[2], str(value).split('|')[3])

# 	class Meta:
# 		orderable = False
# 		attrs = {'class':'ingredients'}

# class RecipeTable(tables.Table):
# 	lab_recipe = tables.Column(verbose_name="Product", accessor=A('lab_recipe'))
# 	lab_sample_number = tables.Column(verbose_name="LS#")
# 	for_customer = tables.Column(verbose_name="Customer | Location")
# 	contact = tables.Column(verbose_name="Contact",accessor=A('for_customer'))

# 	def __init__(self, *args, **kwargs):
# 		super(RecipeTable, self).__init__(*args, **kwargs)

# 	def render_lab_recipe(self, value):
# 		return "%s" % str(value).split('|')[1]
# 	def render_for_customer(self, value):
# 		return "%s | %s, %s" % (str(value).split('|')[0], str(value).split('|')[2], str(value).split('|')[3])
# 	def render_contact(self, value):
# 		return "%s" % str(value).split('|')[4]

# 	class Meta:
# 		orderable = False
# 		attrs = {'class':'recipe_table'}

# def GeneratePdf(self, request, queryset):
# 	data = queryset.values()
# 	content = {}
# 	rec_i = RecipeIngredients.objects.filter(recipe_id=data.values()[0]['lab_recipe_id'])
# 	rec_c = RecipeControl.objects.filter(id=data.values()[0]['lab_recipe_id'])
# 	content.update(data[0])
# 	ingredient_table = IngredientTable(rec_i)
# 	recipe_table = RecipeTable(queryset)
# 	content.update({'ingredient_table':ingredient_table})
# 	content.update({'recipe_table':recipe_table})
# 	#print(content)
# 	pdf = render_to_pdf(request, 'pdf/quote_recipe.html', content)
# 	return HttpResponse(pdf, content_type='application/pdf', )

# mark_sent.short_description = "Mark samples as sent"
# GeneratePdf.short_description = 'Export Quotes as PDF'

### Register your models here.
class DesignPlanAdmin(admin.StackedInline):
	model = DesignPlan
	extra = 1	

	fieldsets = [
		(None, {'fields':[('new_design', 'project_purpose', 'design_approval')]}),
		(None, {'fields':[('technical_approval','customer_approval','factory_trial','notes')]})
	]

class LabSampleAdmin(admin.ModelAdmin):

	list_select_related = ['lab_recipe','requested_by','for_customer']
	list_filter = ['category','requested_by']
	list_display = ('lab_sample_number','lab_recipe', 'for_customer', 'request_date', 'date_sent')
	readonly_fields = ['request_date']
	search_fields = ['lab_sample_number', 'recipes__recipe_name', 'customers__company','customers__first_name', 'customers__last_name']
	fieldsets = [
		('Sample Info',{'fields':[('lab_sample_number','lab_recipe','for_customer','category')]}),
		('Request Info',{'fields':[('requested_by','request_date','date_sent','qty_sent','project_hours')]}),
		('Notes & Comments',{'fields':[('project_folder','projected_volume','volume_interval','material_application', 'comments')]})
	]

	inlines = [DesignPlanAdmin]
	actions = [mark_sent]

admin.site.register(LabSample, LabSampleAdmin)