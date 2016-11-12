from __future__ import unicode_literals
from django.contrib.auth.models import User
from django.db import models
from Inventory import models as items
from Purchasing import models as customers

# Create your models here.
class RecipeControl(models.Model):
    #recipe_name choice field needs to be a query set of all records containing "FG-Finished Goods"
    recipe_name = models.ForeignKey(items.InventoryItem, related_name='recipe_name', limit_choices_to={'category': 'FG'})
    customer = models.ForeignKey(customers.CustomerProfile, related_name='customer')
    ingredients = models.ManyToManyField(items.InventoryItem, through='RecipeIngredients')
    active_recipe = models.BooleanField(default=False)
    active_by = models.CharField(max_length=64, editable=False)
    revision = models.IntegerField(default=0)
    last_updated = models.DateTimeField(auto_now_add=True, editable=False)

    def __str__(self):
        return "%s | %s" % (self.recipe_name, self.customer)

    class Meta:
        managed = True
        unique_together = (('id','recipe_name', 'customer'),)

class RecipeIngredients(models.Model):
    recipe = models.ForeignKey(RecipeControl, related_name='recipe')
    ingredient = models.ForeignKey(items.InventoryItem, related_name='ingredient')
    min_weight = models.DecimalField(max_digits=16, decimal_places=3, blank=True, null=True)
    max_weight = models.DecimalField(max_digits=16, decimal_places=3, blank=True, null=True)
    
    def __str__(self):
        return "%s" % (self.ingredient)

    class Meta:
        managed = True