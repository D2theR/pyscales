from django.contrib import admin
from django.db.models import Sum, F
# Register your models here.
from django.contrib import admin
from django.contrib.auth.models import User
# Register your models hesre.
from .models import RecipeControl, RecipeIngredients, RecipeMixing
from chemicals import models as items

class IngredientInline(admin.StackedInline):
    model = RecipeIngredients
    readonly_fields = ('percentage', 'item_price','SPG')
    fieldsets = [(None,{'fields':[('ingredient','item_price','SPG','percentage','weight_tolerance','recipe_weight')]})]
    extra = 0
    template = 'admin/recipes/recipeingredients/edit_inline/stacked.html'

class MixingInline(admin.StackedInline):
    model = RecipeMixing
    #readonly_fields = ('')
    fieldsets = [(None,{'fields':[('step','category','step_form','mix_time','notes')]})]
    extra = 0
    template = 'admin/recipes/recipeingredients/edit_inline/stacked.html'

class RecipeView(admin.ModelAdmin):
    def save_model(self, request, obj, form, change): 
        obj.active_by = request.user.username
        obj.save()
    
    list_select_related = ['recipe_name']
    list_display = ['recipe_name','active_recipe','last_updated','active_by']
    list_display_links = ['recipe_name']
    search_fields = ['recipe_name__name','ingredients__name','ingredients__item_unique_code','ingredients__supplier','active_by']
    readonly_fields = ('last_updated','active_by','batch_weight','calculated_batch', 'recipe_gravity')

    fieldsets = [
        ('Recipe Information',{'fields': [('recipe_name','customer_recipe','active_recipe')]}),
        ('Audit Trail', {'fields': [('active_by','revision','last_updated')]}),
        ('Batch Weight Info',{'fields': [('batch_weight', 'mixer_volume', 'fill_factor','recipe_gravity', 'calculated_batch')]})
    ]
    inlines = [IngredientInline, MixingInline]

admin.site.register(RecipeControl, RecipeView)