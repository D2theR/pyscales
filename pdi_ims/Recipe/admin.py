from django.contrib import admin
#from import_export import resources
#from import_export.admin import ImportExportActionModelAdmin
from django.contrib.auth.models import User
# Register your models here.
from .models import RecipeControl, RecipeIngredients
from Inventory import models as items

class IngredientInline(admin.StackedInline):
    model = RecipeIngredients
    fieldsets = [(None,{'fields':[('ingredient','min_weight','max_weight')]})]
    extra = 1

class RecipeView(admin.ModelAdmin):
    def save_model(self, request, obj, form, change): 
        obj.active_by = request.user.username
        obj.save()
    
    list_select_related = ['recipe_name','customer']
    list_display = ['recipe_name','customer','active_recipe','last_updated','active_by']
    list_editable = ['recipe_name','customer','active_recipe']
    search_fields = ['recipe_name__name','customer__name','ingredients__name','ingredients__item_unique_code','ingredients__supplier','active_by']
    readonly_fields = ('last_updated','active_by')

    fieldsets = [
        ('Recipe Information',{'fields': [('recipe_name','active_recipe'), 'customer']}),
        ('Audit Trail', {'fields': [('active_by','revision','last_updated')],'classes':['collaspe']}),
    ]
    inlines = [IngredientInline]

admin.site.register(RecipeControl, RecipeView)