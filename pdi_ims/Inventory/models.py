
from __future__ import unicode_literals
from django.contrib.auth.models import User
from django.db import models
from django.conf import settings

# Create your models here.
class InventoryItem(models.Model):
    item_unique_code = models.CharField(max_length=256, blank=False, null=False)
    category = models.CharField(max_length=256, blank=False, null=False,choices=[('RAW','Raw Material'),('FG','Finished Good'),('PKG','Packaging')])
    name = models.CharField(max_length=64, blank=False, null=False)
    supplier = models.CharField(max_length=96, blank=False,null=False)
    approved_by = models.CharField(max_length=64, editable=False)
    date_approved = models.DateTimeField(auto_now_add=True, editable=False)
    comments = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return "%s | %s | %s" % (self.item_unique_code,self.name,self.supplier)
    
    def show_recipes(self):
        return self.objects.get(category='FG')
    show_recipes.admin_order_field = 'category'
    show_recipes.short_description = 'Filter by category'


    class Meta:
        managed = True
        unique_together = (('item_unique_code', 'category', 'name', 'supplier'),)

class CompoundingChart(models.Model):
    finished_product = models.ForeignKey('CustomerOrder.OrderItem', related_name='finished_product')
    raw_material = models.ForeignKey('Purchasing.PO_Item', related_name='raw_material')
    tare_wt = models.DecimalField(max_digits=16, decimal_places=2, blank=True, null=True)
    amount_used = models.DecimalField(max_digits=16, decimal_places=2, blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True, editable=False)
    user_name = models.CharField(max_length=64, editable=False)

    class Meta:
        managed = True
        unique_together = (('id', 'finished_product', 'raw_material'),)