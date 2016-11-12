from __future__ import unicode_literals
from datetime import date
from django.contrib.auth.models import User
from django.db import models
#from smart_selects.db_fields import ChainedForeignKey
from Recipe import models as product
from Purchasing import models as customers

# Create your models here.

class FactoryOrder(models.Model):
	factory_order_code = models.CharField(max_length=64, null=True)
	items_ordered = models.ManyToManyField(product.RecipeControl, through='OrderItem')
	ordered_by = models.CharField(max_length=64, null=False)
	placed_by = models.CharField(max_length=64, editable=False)
	requested_ship_date = models.DateField(auto_now=False, editable=True)

	def __str__(self):
		return "%s | %s" % (self.factory_order_code, self.items_ordered)

	class Meta:
		managed = True
		unique_together = (('id','factory_order_code',),)

class OrderItem(models.Model):
	foc_number = models.ForeignKey(FactoryOrder, related_name='foc_number')
	for_customer = models.ForeignKey(customers.CustomerProfile, related_name='for_customer')
	products_ordered = models.ForeignKey(product.RecipeControl, related_name='products_ordered')
	# products_ordered = ChainedForeignKey(
	# 	product.RecipeControl,
	# 	chained_field="for_customer",
	# 	chained_model_field="customer",
	# 	show_all=False,
	# 	auto_choose=True
	# 	)
	lot_number = models.CharField(max_length=64, null=True)
	lbs_ordered = models.DecimalField(max_digits=16, decimal_places=2, blank=True, null=True)
	date_ordered = models.DateField(editable=True)
	last_updated = models.DateTimeField(auto_now_add=True, editable=False)
	order_done = models.BooleanField(default=False)
	date_completed = models.DateField(blank=True, null=True, editable=True)

	def __str__(self):
		return "%s | %s" % (self.products_ordered, self.lot_number)
	
	class Meta:
		managed = True
		unique_together = (('id','foc_number','lot_number'),)