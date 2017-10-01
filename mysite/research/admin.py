from django.contrib import admin
from django.http import HttpResponse
from django.db.models import Sum, Max, F
from django.views.generic import View
from datetime import datetime, date
from .models import LabSample, DesignPlan
from recipes.models import RecipeControl, RecipeIngredients, RecipeMixing, RecipePackaging
from chemicals.models import IngredientList, ItemPricing
#from .utils import render_to_pdf
from django.utils.html import format_html, mark_safe
import django_tables2 as tables
from django_tables2 import A, RequestConfig
from django.views.generic.base import TemplateView
from django.template import loader, RequestContext
from django.conf import settings
from django.shortcuts import render

### Admin Actions - Drop-down menu of change_list
### NOTE: 'tables.Table' class objects are used for rendering django_tables2 html tables when
### generating PDFs through the utils.py file.

def mark_sent(modeladmin, request, queryset):
		d = date.today()
		queryset.update(date_sent=d)

### HTML TABLES created through django_tables2.

class MixingTable(tables.Table):
	step = tables.Column()
	category = tables.Column()
	step_form = tables.Column()
	mix_time = tables.Column()
	mix_temp = tables.Column()
	notes = tables.Column()
	#extra = tables.rows

	class Meta:
		order_by = ('step')
		attrs = {'class' : 'customred'}

class PackagingTable(tables.Table):
	recipe_packed = tables.Column(verbose_name="Item Packaged")
	packaging_item = tables.Column()
	qty_per_pkg = tables.Column()
	item_needed = tables.Column()

	def render_recipe_packed(self, value):
		return "%s" % (str(value).split('|')[1])

	def render_packaging_item(self, value):
		return "%s | %s" % (str(value).split('|')[0],str(value).split('|')[1])

	class Meta:
		attrs = {'class': 'customred'}

class IngredientTable(tables.Table):
	## Reorder columns according to number system below.
	iuc_num = tables.Column(footer=' ',verbose_name="IUC #", accessor=A("ingredient.item_code"))
	ingredient = tables.Column(footer=' ')
	supplier = tables.Column(footer='Totals: ', accessor=A('ingredient.supplier'))
	#1
	item_price = tables.Column(footer=' ', verbose_name="Cost ($/lb.)")
	#2
	percentage = tables.Column(footer=lambda table: round(sum(x.percentage for x in table.data),3),verbose_name="( % )")
	#3
	ext_price = tables.Column(footer=lambda table: round(sum(x.ext_price for x in table.data),3), verbose_name="Ext Cost")
	#4
	recipe_weight = tables.Column(footer=lambda table: sum(x.recipe_weight for x in table.data))
	#5
	SPG = tables.Column(footer=lambda table: round(100/sum(x.percentage/x.SPG for x in table.data),3))
	#6
	csm = tables.Column(verbose_name='CSM?', accessor=A('ingredient.customer_supplied'))
	#7
	ingredient_notes_json = tables.Column(verbose_name='Notes & Pricing Info')

	def render_ext_price(self, value):
		return "$ "+str(value)

	def render_csm(self, value):
		if value == True:
			return "YES"
		if value == False:
			return "NO"
	#def render_ext_price(self, value):
	#	return "$ %s" % str(value)
	def render_ingredient(self, value):
		return "%s" %str(value).split('|')[1]
	def render_supplier(self, value):
		return "%s" %str(value).split('|')[0]

	class Meta:
		#model = RecipeIngredients
		#exclude = ('id', 'recipe', 'weight_tolerance')
		order_by = ('-recipe_weight')
		#orderable = False
		attrs = {'class':'customgray'}

# class IngredientTable(tables.Table):
# 	## Reorder columns according to number system below.
# 	iuc_num = tables.Column(verbose_name="IUC #", accessor=A("ingredient.item_code"))
# 	ingredient = tables.Column()
# 	supplier = tables.Column(accessor=A('ingredient.supplier'))
# 	#1
# 	csm = tables.Column(verbose_name='CSM?', accessor=A('ingredient.customer_supplied'))
# 	#2
# 	item_price = tables.Column(verbose_name="Cost ($/lb.)")
# 	#3
# 	ext_price = tables.Column(verbose_name="($/%)")
# 	#4
# 	percentage = tables.Column(verbose_name="( % )")
# 	#5
# 	recipe_weight = tables.Column()
# 	#6
# 	SPG = tables.Column()
# 	#7
# 	#ext_price = tables.Column(footer=lambda table: round(sum(x.ext_price for x in table.data),3), verbose_name="Cost ($/%)")
	
# 	comments = tables.Column(verbose_name='Notes', accessor=A('ingredient.comments'))

# 	def render_csm(self, value):
# 		if value == True:
# 			return "YES"
# 		if value == False:
# 			return "NO"
# 	#def render_ext_price(self, value):
# 	#	return "$ %s" % str(value)
# 	def render_ingredient(self, value):
# 		return "%s" %str(value).split('|')[1]
# 	def render_supplier(self, value):
# 		return "%s | %s, %s" %(str(value).split('|')[0], str(value).split('|')[2], str(value).split('|')[3])

# 	class Meta:
# 		#model = RecipeIngredients
# 		#exclude = ('id', 'recipe', 'weight_tolerance')
# 		orderable = False
# 		attrs = {'class':'customgray'}

###Recipe Info table for Django-Tables2
class RecipeTable(tables.Table):
	lab_recipe = tables.Column(verbose_name="Product", accessor=A('lab_recipe'))
	lab_sample_number = tables.Column(verbose_name="LS#")
	requested_by = tables.Column(accessor=A('requested_by.info'))
	for_customer = tables.Column(verbose_name="Customer", accessor=A('for_customer.company.address'))
	contact_info = tables.Column(verbose_name="Contact",accessor=A('for_customer.info'))
	category = tables.Column(verbose_name="Sample Sent?")
	projected_volume = tables.Column("Volume(lbs.)")
	volume_interval = tables.Column("Frequency")
	material_application = tables.Column("End Use")
	comments = tables.Column("Notes")

	def __init__(self, *args, **kwargs):
		super(RecipeTable, self).__init__(*args, **kwargs)
			
	def render_lab_recipe(self, value):
		return "%s" % str(value).split('|')[1]
	#def render_contact(self, value):
	#	return "%s" % str(value).split('|')[4]

	class Meta:
		orderable = False
		attrs = {'class':'customred'}

###Exports Information to Quote Recipe Form
def GeneratePdf(self, request, queryset):
	data = queryset.values()
	content = {}
	rec_i = RecipeIngredients.objects.filter(recipe_id=data.values()[0]['lab_recipe_id'])
	rec_c = RecipeControl.objects.filter(id=data.values()[0]['lab_recipe_id'])
	mix_data = RecipeMixing.objects.filter(for_recipe=data.values()[0]['lab_recipe_id'])
	pkg_data = RecipePackaging.objects.filter(recipe_packed=data.values()[0]['lab_recipe_id'])
	content.update(data[0])
	mixing_table = MixingTable(mix_data)
	pkg_table = PackagingTable(pkg_data)
	ingredient_table = IngredientTable(rec_i)
	recipe_table = RecipeTable(queryset)
	content.update({'mixing_table':mixing_table})
	content.update({'ingredient_table':ingredient_table})
	content.update({'recipe_table':recipe_table})
	content.update({'pkg_table':pkg_table})
	content.update({'datetime': datetime.now()})
	RequestConfig(request).configure(recipe_table)
	return render(request, 'pdf/quote_recipe.html', content)

mark_sent.short_description = "Mark samples as sent"
GeneratePdf.short_description = 'Export Quote as PDF'

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
	list_display = ('lab_sample_number','recipe_name', 'for_customer', 'request_date', 'date_sent')
	readonly_fields = ['project_files']
	search_fields = ['lab_sample_number', 'lab_recipe__recipe_name__name', 'for_customer__company__name','for_customer__first_name', 'for_customer__last_name']
	fieldsets = [
		('Sample Info',{'fields':[('lab_sample_number','lab_recipe','for_customer','category')]}),
		('Request Info',{'fields':[('requested_by','request_date','date_sent','sample_mfg','qty_sent','project_hours')]}),
		('Notes & Comments',{'fields':[('project_folder','project_files' ,'projected_volume','volume_interval','material_application', 'comments')]})
	]

	inlines = [DesignPlanAdmin]
	actions = [mark_sent, GeneratePdf]

	class Media:
		js = ['admin/js/list_filter_collaspe.js']

admin.site.register(LabSample, LabSampleAdmin)