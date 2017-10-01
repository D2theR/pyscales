from django.contrib import admin
from django.db.models import Sum, F
from django import forms
# Register your models here.
from import_export import resources
from django.contrib.auth.models import User
# Register your models hesre.
from .models import RecipeControl, RecipeIngredients, RecipeMixing, RecipePackaging
from chemicals import models as items

class IngredientInline(admin.TabularInline):
    model = RecipeIngredients
    raw_id_fields = ['ingredient']
    readonly_fields = ('percentage', 'item_price','ext_price','SPG')
    fieldsets = [(None,{'fields':[('ingredient','item_price','ext_price','SPG','percentage','weight_tolerance','recipe_weight')]})]
    extra = 0
    #formset = IngredientInlineFormset
    template = 'admin/recipes/recipeingredients/edit_inline/tabular.html'

class MixingInline(admin.TabularInline):
    model = RecipeMixing
    #readonly_fields = ('')
    fieldsets = [(None,{'fields':[('step','category','step_form','mix_time','mix_temp','mix_add','notes')]})]
    extra = 0
    template = 'admin/recipes/recipeingredients/edit_inline/tabular.html'

class PackagingInline(admin.TabularInline):
    model = RecipePackaging

    fieldsets = [(None,{'fields':[('recipe_packed','packaging_item','qty_per_pkg', 'item_needed')]})]
    extra = 0
    template = 'admin/recipes/recipeingredients/edit_inline/tabular.html'


class RecipeView(admin.ModelAdmin):
    def save_model(self, request, obj, form, change): 
        obj.active_by = request.user.username
        obj.save()
    
    list_select_related = ['recipe_name', 'customer_recipe']
    list_display = ['recipe_name','customer_recipe','active_recipe','last_updated','active_by']
    list_display_links = ['recipe_name']
    list_filter = ['active_recipe']
    search_fields = ['recipe_name__name', 'recipe_name__item_code','customer_recipe__name']
    readonly_fields = ('last_updated','active_by','batch_weight','calculated_batch', 'recipe_gravity')

    fieldsets = [
        ('Recipe Information',{'fields': [('recipe_name','customer_recipe','active_recipe')]}),
        ('Audit Trail', {'fields': [('active_by','revision','last_updated')]}),
        ('Batch Weight Info',{'fields': [('batch_weight', 'batch_adjust', 'mixer_volume', 'fill_factor','recipe_gravity', 'calculated_batch')]})
    ]
    inlines = [IngredientInline, MixingInline, PackagingInline]

    class Media:
        js = [
            '//ajax.googleapis.com/ajax/libs/jquery/3.2.1/jquery.min.js',
            'admin/js/recipe_calc.js',
            'admin/js/list_filter_collaspe.js'
        ]

admin.site.register(RecipeControl, RecipeView)