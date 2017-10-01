import os
from django.db import models
from django.db.models.signals import post_save, pre_save
from django.utils.html import format_html, mark_safe
from mysite.settings import MEDIA_ROOT, MEDIA_URL
from django.db.models import Max, Sum, F
from datetime import datetime, timedelta
from decimal import Decimal
from recipes import models as recs
from customers import models as customer

def sample_directory(instance, filename):
	#filename = "file-%Y-%m-%d"
	return '%s_%s/%s' % (str(instance.lab_sample_number), str(instance.lab_recipe).split(" | ")[1], filename)

# Create your models here.
class LabSample(models.Model):
	def ls_num():
		num = LabSample.objects.aggregate(Max('lab_sample_number'))
		yy = int(str(datetime.now().year)[2:])
		if num['lab_sample_number__max'] is None or 0:
			return yy*1000	
		ny = int(str(num['lab_sample_number__max'])[2:])
		if ny - yy == 1:
			return ny*1000
		else:
			return num['lab_sample_number__max'] + 1

	lab_sample_number = models.IntegerField(verbose_name='LS #', unique=True, default=ls_num)
	lab_recipe = models.ForeignKey(recs.RecipeControl, related_name='lab_recipe')
	for_customer = models.ForeignKey(customer.CustomerContacts, verbose_name='customer', related_name='for_customer')
	category = models.CharField(max_length=64, blank=False, null=False, choices=[('QT','Quote'),('SM','Sample'),('SM-QT','Sample|Quote')])
	requested_by = models.ForeignKey(customer.CustomerContacts, related_name='requested_by')
	# request_date = models.DateTimeField(auto_now_add=True)
	request_date = models.DateField(blank=False, null=False)
	date_sent = models.DateField(blank=True, null=True)
	sample_mfg = models.DateField(verbose_name='Mfg. Date',blank=True, null=True)
	qty_sent = models.DecimalField(max_digits=8, decimal_places=2, default=Decimal(2.00))
	project_hours = models.DecimalField(max_digits=8, decimal_places=2, default=Decimal(2.00), blank=True, null=True)
	#project_hours = models.DurationField(blank=True, default=timedelta(hours=2))
	projected_volume = models.DecimalField(max_digits=8, decimal_places=2)
	volume_interval = models.CharField(max_length=64, blank=False, null=False, choices=[('ORD','Per Order'),('MON','Per Month'),('YR','Per Year'),('OTH','Other|See Notes')])
	material_application = models.TextField(verbose_name='End Application & Customer Info',blank=True, null=True)
	comments = models.TextField(blank=True, null=True)
	project_folder = models.FileField(upload_to=sample_directory, max_length=256)

	def __str__(self):
		return "%s | %s" % (self.lab_sample_number, self.lab_recipe)

	def recipe_name(self):
		ln = str(self.lab_recipe).split(' | ')
		return "%s | %s " % (ln[0], ln[1])
	
	def _project_files(self):
		name = self.lab_recipe
		return format_html('<a href="/labsamples/{}_{}">Project Files</a>', self.lab_sample_number, str(self.lab_recipe).split(" | ")[1])
	project_files = property(_project_files)

	class Meta:
		managed = True
		unique_together = (('id','lab_sample_number'),)

def get_project_folder(sender, **kwargs):
	i = kwargs['instance']
	print(str(i))
	s_path = str(i).split(" | ")
	if not os.path.exists(MEDIA_ROOT+str(s_path[0])+"_"+s_path[2]):
		os.makedirs(MEDIA_ROOT+str(s_path[0])+"_"+s_path[2])
		print("DIRECTORY MADE:"+MEDIA_ROOT+str(s_path[0])+"_"+s_path[2])

pre_save.connect(get_project_folder, sender=LabSample)

class DesignPlan(models.Model):
	sample_number = models.ForeignKey(LabSample, related_name='sample_number')
	new_design = models.BooleanField(default=False)
	project_purpose = models.CharField(max_length=256, blank=False, null=False)
	design_approval = models.BooleanField(default=False)
	technical_approval = models.BooleanField(default=False)
	customer_approval = models.DateField(blank=True,null=True)	
	factory_trial = models.BooleanField(default=False)
	notes = models.TextField(blank=True, null=True)

	class Meta:
		managed = True
		unique_together = (('id','sample_number'),)