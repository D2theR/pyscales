from django.contrib import admin
from django.contrib.auth.models import User

# Register your models here.
from .models import CustomerProfile, CustomerContacts

class ContactsView(admin.StackedInline):
    model = CustomerContacts
    fieldsets = [
    	(None,{'fields':[('first_name', 'last_name', 'title', 'position')]}),
    	(None,{'fields':[('email','phone_number')]})
    ]
    extra = 1

class CustomerView(admin.ModelAdmin):	
	def save_model(self, request, obj, form, change): 
		obj.added_by = request.user.username
		obj.save()
		
	list_display = ('name','customer_code','address_line_1','address_line_2','city','state_or_region','last_updated')

	fieldsets = [
		('Customer Profile',        {'fields': ['name', 'customer_code']}),
        ('Address Info', {'fields': ['address_line_1','address_line_2','city','state_or_region','zip_or_region_code','country','website','comments']}),
        ('Audit Trail', {'fields': ['added_by','last_updated'],'classes':['collaspe']}),
    ]

	search_fields = ['name','customer_code','address_line_1','address_line_2','city','state_or_region']
	readonly_fields = ('last_updated','added_by')

	inlines = [ContactsView]

admin.site.register(CustomerProfile, CustomerView)