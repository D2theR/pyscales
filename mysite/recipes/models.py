from numbers import Number
from decimal import Decimal
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.db import models
from django.db.models import Sum, Max, F, Q
from django.forms import ModelForm, Textarea
from chemicals import models as items
from customers import models as custmods

# Create your models here.
class RecipeControl(models.Model):
    #recipe_name choice field needs to be a query set of all records containing "FG-Finished Goods"
    recipe_name = models.ForeignKey(items.IngredientList, related_name='recipe_name', limit_choices_to={'category': 'FG'})
    customer_recipe = models.ForeignKey(custmods.CustomerProfile, verbose_name='customer', related_name='customer_recipe')
    ingredients = models.ManyToManyField(items.IngredientList, through='RecipeIngredients')
    active_recipe = models.BooleanField(default=False)
    active_by = models.CharField(max_length=64, editable=False)
    revision = models.IntegerField(default=0)
    last_updated = models.DateTimeField(auto_now_add=True, editable=False)
    mixer_volume = models.DecimalField(verbose_name='Mixer Volume(L)', max_digits=16,decimal_places=3, blank=True, null=True)
    fill_factor = models.DecimalField(verbose_name='Fill %', max_digits=6,decimal_places=2,blank=True,null=True)
    batch_adjust = models.DecimalField(verbose_name='Adjust', max_digits=6,decimal_places=2,blank=True,null=True, default=1)
    
    def __str__(self):
        return "%s" % (self.recipe_name)

    def _get_total(self):
        #functions to calculate whatever you want...
        total = RecipeIngredients.objects.filter(recipe_id=self.id).aggregate(Sum(F('recipe_weight')))

        if total['recipe_weight__sum'] is None:
            return str('0.00')
        if isinstance(total['recipe_weight__sum'], Decimal):
            return round(total['recipe_weight__sum'], 4)

    def _get_calc_batch(self):
        spg_calc = []
        if self.mixer_volume is 0 or None:
            return "Error!"
        if self.fill_factor is 0 or None:
            return "Error!"
        if self.mixer_volume and self.fill_factor is not None:
            for i in RecipeIngredients.objects.filter(recipe_id=self.id).values():
                spg = list(items.IngredientList.objects.filter(id=i['ingredient_id']).values_list('specific_gravity', flat=True))[0]
                i['SPG'] = spg
                grav_calc = round(i['recipe_weight']/i['SPG'],4)
                i['GVC'] = grav_calc
                spg_calc.append(i)
                batch_sum = sum(ing['recipe_weight'] for ing in spg_calc)
                grav_sum = sum(g['GVC'] for g in spg_calc)
            return round(self.mixer_volume*Decimal(2.2046)*(self.fill_factor/100)*(batch_sum/grav_sum),3)

    
    def _get_finished_spg(self):
        i = RecipeIngredients.objects.filter(recipe_id=self.id).prefetch_related('ingredient').all()
        if len(i) == 0:
            return 0
        if len(i) > 0:
            f = [x.percentage/x.SPG for x in i]
            return round(100/sum(f),3)

    
    ### Calculated fields must be defined after their property method.
    batch_weight = property(_get_total)
    calculated_batch = property(_get_calc_batch)
    recipe_gravity = property(_get_finished_spg)

    class Meta:
        managed = True
        unique_together = (('id','recipe_name'),)

class AllMethodCachingQueryset(models.query.QuerySet):
    def all(self, get_from_cache=True):
        if get_from_cache:
            return self
        else:
            return self._clone()


class AllMethodCachingManager(models.Manager):
    def get_query_set(self):
        return AllMethodCachingQueryset(self.model, using=self._db)

class RecipeIngredients(models.Model):
    recipe = models.ForeignKey(RecipeControl, related_name='recipe')
    ingredient = models.ForeignKey(items.IngredientList, related_name='ingredient')
    weight_tolerance = models.DecimalField(verbose_name="PPH Tolerance",max_digits=8, decimal_places=3, blank=True, null=False, default=round(Decimal(0.01),2))
    recipe_weight = models.DecimalField(verbose_name="PPH",max_digits=16, decimal_places=3, blank=True, null=False)

    def __str__(self):
        return "%s" % (self.ingredient)

    def _recipe_percent(self):
        total = RecipeIngredients.objects.filter(recipe__id=self.recipe_id).aggregate(Sum(F('recipe_weight')))
        if isinstance((self.recipe_weight), Number) == True:
            percent = self.recipe_weight/total['recipe_weight__sum']
            return round(percent*100, 3)
    
    def _get_price(self):
        p = list(items.ItemPricing.objects.filter(item_id=self.ingredient_id, best_price=True).values_list('price',flat=True))
        if len(p) == 0:
            return "0.00"
        if isinstance(p[0], Decimal) == True:
            return '$ '+str(round(p[0], 3))
    
    def _get_spg(self):
        spg = list(items.IngredientList.objects.filter(id=self.ingredient_id).values_list('specific_gravity', flat=True))
        if len(spg) == 0:
            return "Error!"
        if isinstance(spg[0], Decimal) == True:
            return round(spg[0], 3)

    def _ext_price(self):
        p = items.ItemPricing.objects.filter(item_id=self.ingredient_id, best_price=True).values_list('price',flat=True)
        total = RecipeIngredients.objects.filter(recipe__id=self.recipe_id).aggregate(Sum(F('recipe_weight')))       
        
        if total['recipe_weight__sum'] is None:
            return str('0.00')
        if isinstance(self.recipe_weight, Decimal) == True:
            percent = self.recipe_weight/total['recipe_weight__sum']*100
            price = (p[0]*percent)/100
            return round(price,3)

    def ingredient_notes_json(self):
        pricing = items.ItemPricing.objects.filter(item_id=self.ingredient_id).values('packaging_type','unit_type','min_qty','max_qty', 'price', 'freight_type', 'fob_point', 'freight_cost', 'notes')[:5]
        js = JsonResponse({'pricing': list(pricing)})
        return js.content
        

    ### Calculated fields
    percentage = property(_recipe_percent)
    item_price = property(_get_price)
    SPG = property(_get_spg)
    ext_price = property(_ext_price)

    cache_all_method = AllMethodCachingQueryset()
    
    class Meta:
        verbose_name = 'Recipe Ingredient'
        managed = True


class RecipeMixing(models.Model):
    MACHINE_LIST = [
    ('25G','25G Ross'),
    ('75G','75G Ross'),
    ('42ML','42" Mill'),
    ('60ML','60" Mill'),
    ('75L-T','75L Tilt'),
    ('200MM-EXT','200mm Extruder'),
    ('LAB-MIX','3.8L Lab Mixer'),
    ('LAB-EXT','Lab Extruder'),
    ('130L-LF','130L Littleford'),
    ('600L-LF','600L Littleford'),
    ('1200L-LF','1200L Littleford'),
    ('2000L-LF','2000L Littleford'),
    ('DAY','Day Mixer'),
    ('HEN','Henschel'),
    ('DICE','Dicer'),
    ('OVEN','Oven'),
    ('PW','Pre-Weighed Bag'),
    ('BAGR','Auto Bagger'),
    ('OTHER','Other-See Notes')]
    MATERIAL_FORMS = [
    ('PWDR','Powder'),
    ('SLAB','Polymeric Slab'),
    ('PASTE','Paste'),
    ('5MM-CB','5mm Cubes'),
    ('3MM-PLT','3mm Pellets'),
    ('6MM-PLT','6mm Pellets'),
    ('LQD','Liquid'),
    ('OTHER','Other-See Notes')
    ]

    for_recipe = models.ForeignKey(RecipeControl, related_name='for_recipe')
    step = models.IntegerField(unique=False, default=1)
    category = models.CharField(max_length=64, blank=False, null=True, choices=MACHINE_LIST)
    step_form = models.CharField(max_length=64, blank=False, null=True, choices=MATERIAL_FORMS)
    mix_time = models.DecimalField(verbose_name="Mix Time(mins.)",max_digits=6, decimal_places=2, blank=True, null=True)
    mix_temp = models.DecimalField(verbose_name="Mix Temp(F)",max_digits=6, decimal_places=2, blank=True, null=True)
    mix_add = models.TextField(verbose_name="Mixing Order", blank=True, null=True)
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return "# %s" % (self.step)

    class Meta:
        verbose_name = 'Mixing Instruction'
        managed = True

class RecipePackaging(models.Model):
    recipe_packed = models.ForeignKey(RecipeControl, related_name='recipe_packed')
    qty_per_pkg = models.DecimalField(verbose_name='Qty/Package',max_digits=8, decimal_places=3,blank=True, null=True)
    packaging_item = models.ForeignKey(items.IngredientList, limit_choices_to=Q(category='PKG')|Q(category="LBL"))
    item_needed = models.DecimalField(verbose_name="Item/Package",max_digits=6, decimal_places=2, blank=True, null=True)

    def __str__(self):
        return "%s | %s" % (self.recipe_packed, self.packaging_item)

    class Meta:
        managed = True