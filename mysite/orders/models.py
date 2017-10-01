from django.db import models
from decimal import Decimal
from django.db.models import Sum, F
# Create your models here.
from recipes import models as product
from customers import models as customer
from suppliers import models as supply
from chemicals import models as items
from inventory.models import CompoundingChart

# Create your models here.

class FactoryOrder(models.Model):
	ORDER_LIST = [
	('PR', 'Production Order'),
	('ST', 'Stock Order'),
	('LS', 'Lab Sample'),
	('FT', 'Factory Trial'),
	('RMA', 'Return'),
	('INT', 'Internal')
	]
	factory_order_code = models.CharField(max_length=64, null=True)
	customer_po = models.CharField(max_length=64, null=True)
	items_ordered = models.ManyToManyField(product.RecipeControl, through='OrderItem')
	order_type = models.CharField(max_length=64, blank=False, null=True, choices=ORDER_LIST)
	ordered_by = models.ForeignKey(customer.CustomerProfile, null=False)
	bill_to = models.ForeignKey(customer.CustomerContacts, null=False)
	requested_ship_date = models.DateField(auto_now=False, editable=True)
	comments = models.TextField(blank=True, null=True)

	def __str__(self):
		return "%s | %s" % (self.factory_order_code, self.items_ordered)

	def _get_items(self):
		return " | ".join([str(i).split(' | ')[1] for i in self.items_ordered.all()])

	items_on_order = property(_get_items)

	class Meta:
		managed = True
		unique_together = ('id','factory_order_code')

class OrderItem(models.Model):
	foc_number = models.ForeignKey(FactoryOrder, related_name='foc_number')
	products_ordered = models.ForeignKey(product.RecipeControl, related_name='products_ordered')
	ship_to = models.ForeignKey(customer.CustomerProfile, null=False)
	lot_number = models.CharField(max_length=64, null=True)
	lbs_ordered = models.DecimalField(max_digits=16, decimal_places=2, blank=True, null=True)
	date_ordered = models.DateField(editable=True)
	order_done = models.BooleanField(default=False)
	date_completed = models.DateField(blank=True, null=True, editable=True)
	comments = models.TextField(blank=True, null=True)

	def __str__(self):
		return "%s | %s" % (self.products_ordered, self.lot_number)
	
	class Meta:
		managed = True
		unique_together = (('id','foc_number','lot_number'),)

class PurchaseOrder(models.Model):
	PO_LIST = [
		('RAW','Raw Material'),
		('CSM', 'Customer Supplied'),
		('PKG','Packaging'),
		('LBL','Labeling'),
		('LS', 'Lab Sample'),
		('MNT', 'Maintenance'),
		('OFC', 'Office Supplies'),
		('CPT', 'Capital Improvements'),
		('OTH', 'Other')
	]
	po_number = models.CharField(max_length=96, verbose_name="PO#")
	po_type = models.CharField(max_length=64, verbose_name='Category', blank=False, null=True, choices=PO_LIST)
	ordered_from = models.ForeignKey(supply.SupplierProfile, related_name='ordered_from')
	placed_with = models.ForeignKey(supply.SupplierContacts, related_name='placed_with')
	iuc_to_order = models.ManyToManyField(items.IngredientList, through='PO_Item')
	date_ordered = models.DateTimeField(auto_now_add=True, editable=False)
	comments = models.TextField(blank=True, null=True)

	def __str__(self):
		return "%s" % (self.po_number)

	class Meta:
		unique_together = (('id','po_number'),)
		managed = True

class PO_Item(models.Model):
	ITEM_LIST = [
	('OPEN','Open'),
	('RTN','Return'),
	('HOLD','On Hold'),
	('CNL','Cancelled'),
	('OTH','Other-See Comments'),
	]
	order_number = models.ForeignKey(PurchaseOrder, related_name='order_number')
	item_ordered = models.ForeignKey(items.IngredientList, related_name="item_ordered")
	item_status = models.CharField(max_length=64, verbose_name='Category', blank=False, null=True, choices=ITEM_LIST)
	lot_number = models.CharField(max_length=128, blank=True, null=True)
	lbs_ordered = models.DecimalField(max_digits=16, decimal_places=2, blank=True, null=True)
	lbs_received = models.DecimalField(max_digits=64, decimal_places=2, blank=True, null=True)
	date_received = models.DateTimeField()
	lab_approval = models.BooleanField(default=False)
	comments = models.TextField(blank=True, null=True)
	barcode_data = models.CharField(max_length=200, blank=True, null=True)

	def __str__(self):
		return "%s | %s | %s" % (self.order_number, self.item_ordered, self.lot_number)

	def _lbs_used(self):
		total = CompoundingChart.objects.filter(raw_material_id=self.id).aggregate(Sum(F('amount_used')))
		if total['amount_used__sum'] is None:
			return str('0.00')
		if isinstance(total['amount_used__sum'], Decimal):
			return round(total['amount_used__sum'], 2)
	lbs_used = property(_lbs_used)
	class Meta:
		unique_together = (('id','order_number','item_ordered'),)
		verbose_name = "P.O. Item"
		managed = True