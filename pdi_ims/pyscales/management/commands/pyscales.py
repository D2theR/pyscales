### Created by Dan Rerko: March 9th, 2016

### Python packagings to import
import os
import serial
from prettytable import PrettyTable
from datetime import datetime

### Django models to import
from Scale.models import ScaleManager, ScaleVerification
from CustomerOrder.models import OrderItem, FactoryOrder
from Recipe.models import RecipeControl, RecipeIngredients
from Inventory.models import InventoryItem, CompoundingChart
from Purchasing.models import PurchaseOrder, PO_Item
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

scale_number = 1

class Command(BaseCommand):
	def handle(self, *args, **options):
		### Starts scale calibration verification.
		while True:
			try:
				# Get user information and checks they exist in the system.
				print("Please scan your provided QR-Code User Badge to begin...")
				zbar = ZBar.get_cam()
				name = zbar[1].strip().split(' ')
				#print(name)
				usr = User.objects.get(last_name=name[1])
				if name[1] == usr.last_name:
					print("Verified! Hello {} {}".format(usr.first_name, usr.last_name))
					break
				elif zbar[1] is not usr.last_name:
					err
			except User.DoesNotExist as err:
				print(color.WARN+"The wrong type of QR-Code was scanned or the User you entered is not in the system."+color.END)
				print(color.WARN+"Please contact your supervisor or Q.C. if the problem persists further..."+color.END)
		###COMMENT THESE LINES TO ENABLE DEBUG MODE
		# while True:
		# 	if Scale.scale_verify(usr) == True:
		# 		print("Scale passed calibration!")
		# 		break
		# 	else:
		# 		print(color.FAIL+"This scale is out of calibration. Please notify your supervisor or Q.C. as soon as possible!"+color.END)
		# 		exit()
		# 		break
		###COMMENT THESE LINES TO ENABLE DEBUG MODE

		### Begins sequence to select weighment type based on user input.
		while True:
			Scale.scale_options(usr)
		
### Class that handles barcode webcam reading logic.
class ZBar():
	def get_cam():
		### Calls tex.sh to KILL any zbar task. Then starts camera and waits for input from user.
		os.system(os.path.join(os.getcwd(), 'tex.sh'))
		p=os.popen('/usr/bin/zbarcam --prescale=300x200','r')
		scan = p.readline()
		barcode = str(scan)[8:].split('_')
		#[1].strip().split(' ')
		os.system(os.path.join(os.getcwd(), 'tex.sh'))
		#print(barcode)
		return barcode

### Class that handles scale logic and connections.
### If connections to '/dev/ttyUSB0' fails try adding Django user to 'dialout', 'gpio', or 'input' groups in Linux.
class Scale():
	###DEBUG METHOD FOR RAW KEYBOARD INPUT RATHER THAN SCALE DATA...
	def connect():
		scale = input(color.WARN+"DEBUG: Enter data from keyboard==>: "+color.END)
		scalelist = scale.split("_")
		if len(scalelist) > 1:
			#print(scalelist)
			scalewt = round(float(scalelist[0].strip('-').strip('lbs.')),2)
			scaletare = round(float(scalelist[1].strip('-').strip('lbs.')),2)
			print(scalewt, type(scalewt))
			print(scaletare, type(scaletare))
			return [scalewt, scaletare]	
		if len(scalelist) == 1:
			print(str(scalelist[0]))
			return str(scalelist[0])

	### Opens connection to scale0/comm device and returns output within the commandline.
	# def connect():
	# 	### Scale connection parameters.
	# 	scale = serial.Serial('/dev/ttyUSB0', 9600, bytesize=serial.EIGHTBITS, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, 
	# 							xonxoff='False', rtscts='False', dsrdtr='False')
	# 	scaleread = scale.readline(100)
	# 	scaledata = str(scaleread, "ascii").strip()
	# 	scalelist = scaledata.split('_')
	# 	if len(scalelist) > 1:
	# 		print(scalelist)
	# 		scalewt = round(float(scalelist[0].strip('-').strip('lbs.')),2)
	# 		scaletare = round(float(scalelist[1].strip('-').strip('lbs.')),2)
	# 		print(scalewt, type(scalewt))
	# 		print(scaletare, type(scaletare))
	# 		scale.close
	# 		return [scalewt, scaletare]	
	# 	if len(scalelist) == 1:
	# 		print(str(scalelist[0]))
	# 		scale.close
	# 		return str(scalelist[0])
	### Checks scale calibration based on previous input by users on the same scale.
	### Note the global 'scale_number' variable that needs changed at the top for each scale.
	def scale_verify(usr):
		print("Beginning scale calibration verification...")
		sv = ScaleVerification.objects.values().filter(scale_verified_id=scale_number).order_by('-id')[0]
		mn = float(sv['check_weight']) - float(sv['tolerance'])
		mx = float(sv['check_weight']) + float(sv['tolerance'])
		while True:
			if sv['verified'] == True:
				print("Please verify this scale is calibrated correctly, by placing the proper {0} LB check weight on the scale and pressing the ''Print'' button.".format(float(sv['check_weight'])))
				f = sorted(list(sv.keys()))
				API.pt([f[4],'Min Wt.',f[0],'Max Wt.'],[float(sv['check_weight']),sv['scale_verified_id'],float(mn),float(mx)])
				break
			if sv['verified'] == False:
				print(color.FAIL+'This scale has previously failed calibration verification and has been placed in a suspended state.'+color.END)
				return False
		while True:
			scale = Scale.connect()
			print(scale)
			if scale[1] > 0:
				print(color.WARN+"Please remove this scales tare weight to continue..."+color.END)
			if scale[1] == 0:
				break
		while True:
			if scale[0] < mn or scale[0] > mx:
				print(color.FAIL+"FAIL!"+color.END)
				i = ScaleVerification(scale_verified_id=scale_number, weight=scale[0], tolerance=sv['tolerance'], check_weight=sv['check_weight'], verified=False, user_name=usr)
				i.save()
				return False
				break
			if scale[0] >= mn and scale[0] <= mx:
				print("PASS!")
				return True
				break
	
	### Checks if Raw Material is QC Verified.
	def raw_material_check(zbar):
		ing = InventoryItem.objects.values().filter(item_unique_code=zbar[1])
		po = PurchaseOrder.objects.values().filter(po_number=zbar[3])
		po_ing = PO_Item.objects.values().filter(order_number_id=po[0]['id'], item_ordered_id=ing[0]['id'])
		if po_ing[0]['lab_approval'] == True:
			return True
		else:
			print(color.FAIL+"This material has not been approved by the Q.C. Lab, please contact them before continuing..."+color.END)
			return False
	def recipe_check(zbar):
		recipe_info = InventoryItem.objects.values().filter(item_unique_code=zbar[1])
		recipe = RecipeIngredients.objects.values().filter(recipe_id=recipe_info[0]['id'])
		recipe_items = []
		for i in recipe:
			name = InventoryItem.objects.values().filter(id=i['ingredient_id'])
			list_item = [recipe_info[0]['name'],name[0]['item_unique_code'], name[0]['name'], name[0]['supplier'],float(i['min_weight']),float(i['max_weight'])]
			recipe_items.append(list_item)

		#print(recipe_items)
		fields = ['Recipe','IUC', 'Ingredient', 'Supplier', 'Min. Wt.', 'Max Wt.']
		rows = recipe_items
		API.pt(fields, rows)
		return fields, rows
	# Excepts scale value and recipe min & max values as arguments to check wieghment validity.
	def scale_check(data, mn, mx):
		try:
			if float(data) < mn or float(data) > mx:
				print(color.WARN+"WEIGHMENT ERROR!: Submitted weight beyond Min, or Max Range!"+color.END)
				return False
			if float(data) >= mn and float(data) <= mx:
				return True
		except ValueError as e:
			return 'ABORT'

	### Single material weighing
	def multi_batching(usr):
		while True:
			print("Please scan the QR-Code for the Recipe you are weighing for.")
			print("You can also scan your User QR-Code to restart and pick a different option...")
			zbar = ZBar.get_cam()
			print(zbar)
			if 'USR' in zbar[0]:
				Scale.scale_options(usr)
			if 'RAW' in zbar[0]:
				print(color.WARN+"This is a Raw Material QR-Code, please scan a Recipe QR-Code to continue."+color.END)
			if 'REC' in zbar[0]:
				print("Recipe Data : "+' | '.join(zbar))				
				rec = Scale.recipe_check(zbar)
				if len(rec) < 1:
					print(color.WARN+"The Recipe code scanned did not return a valid Recipe, "+color.END)
					print(color.WARN+"Please contact your supervisor or Q.C. to continue..."+color.END)
				if len(rec) > 1:
					print("Here is the Recipe you requested!")
					ingredient_list = []
					print("Please scan one or more of the Ingredients listed above to get started.")
					print(color.WARN+"When finished, scan your User QR-Code to begin the weighing the ingredients you scanned."+color.END)
					while True:
						zbar_raw = ZBar.get_cam()
						if 'USR' in zbar_raw[0]:
							print('Starting weighment process...')
							Scale.submit_batches(rows, fields, usr, zbar)
							break
						if 'REC' in zbar_raw[0]:
							print(color.WARN+"This is a Recipe QR-Code, you must scan a Raw Material QR-Codes to continue, or your User QR-Code to restart."+color.END)
						# Checks if barcode is Raw Material QR-Code
						if 'RAW' in zbar_raw[0]:
							# Checks for Q.C. Authorization to use the raw material
							raw_check = Scale.raw_material_check(zbar_raw)
							if raw_check == True:
								# Checks for ingredient in scanned zbar recipe.
								x = [i for i in rec[1:][0] if i[1] == zbar_raw[1]]
								for i in rec[1:][0]:
								    if len(x) == 0:
								        print(color.WARN+"This ingredient is not in recipe that was scanned!"+color.END)
								    if len(i) == 8 and x[0] == i:
								        print(color.WARN+"This ingredient was already scanned..."+color.END)
								    if len(i) == 6 and x[0] == i:
								        i.append(zbar_raw[3])
								        i.append(zbar_raw[4].strip())
								        break

								if len(rec[0]) == 6:
									rec[0].append('P.O. #')
									rec[0].append('Lot #')
								fields = rec[0]
								rows = [i for i in rec[1][1:] if len(i) == 8]
								print(rows)
								API.pt(fields, rows)

							if raw_check == False:
								Scale.scale_options(usr)
								break
	### Weighing processes and checks
	def submit_batches(rows, fields, usr, zbar):
		while True:
			for i in rows:
				print(color.WARN+'Please make sure that the Lot #(s) of the material(s) being compounded match the Lot #(s) you scanned into the system'+color.END)
				print(color.WARN+'If the Lot#(s) change or something goes wrong, press "ABORT" on the scale to start the ingredient scanning process over.'+color.END)
				print(color.WARN+'Notify your supervisor immediately of any problems with materials, weighments, or product process errors.'+color.END)
				while True:
					API.pt(fields, [i])
					print("Please submit a weight within the Min. and Max. limits listed above by pressing 'PRINT' on the scale")
					scale = Scale.connect()
					mn = i[4]
					mx = i[5]
					valid_wt = Scale.scale_check(scale[0], mn, mx)
					if valid_wt == False:
						print(color.WARN+"No data submitted! Please try again..."+color.END)
					if valid_wt == 'ABORT':
						Scale.multi_batching(usr)
						break
					if valid_wt == True:
						foc = FactoryOrder.objects.values().filter(factory_order_code=zbar[4].strip())
						oi = OrderItem.objects.values().filter(lot_number=zbar[3], foc_number_id=foc[0]['id'])
						po = PurchaseOrder.objects.values().filter(po_number=i[6])
						po_item = PO_Item.objects.values().filter(lot_number=i[7].strip(), order_number_id=po[0]['id'])
						data = CompoundingChart(finished_product_id=oi[0]['id'], raw_material_id=po_item[0]['id'], tare_wt=scale[1], amount_used=scale[0], user_name=usr)
						data.save()
						timestamp = data.timestamp.strftime("%Y-%m-%d %I:%M%p")
						cmpd_fields = ['PRODUCT', 'PRODUCT LOT#','INGREDIENT', 'INGREDIENT LOT#', 'TARE WT.', 'AMOUNT WT.', 'DATETIME', 'USER']
						cmpd_row = [i[0], zbar[3], i[2], i[7], scale[1], scale[0], timestamp, usr]
						API.pt(cmpd_fields, [cmpd_row])
						break
	
	def large_weighment(usr):
		while True:
			print("Please scan the QR-Code for the Recipe you are weighing for.")
			print("You can also scan your User QR-Code to restart and pick a different option...")
			zbar = ZBar.get_cam()
			print(zbar)
			if 'USR' in zbar[0]:
				Scale.scale_options(usr)
			if 'RAW' in zbar[0]:
				print(color.WARN+"This is a Raw Material QR-Code, please scan a Recipe QR-Code to continue."+color.END)
			if 'REC' in zbar[0]:
				print("Recipe Data : "+' | '.join(zbar))				
				rec = Scale.recipe_check(zbar)
				if len(rec) < 1:
					print(color.WARN+"The Recipe code scanned did not return a valid Recipe, "+color.END)
					print(color.WARN+"Please contact your supervisor or Q.C. to continue..."+color.END)
				if len(rec) > 1:
					print("Here is the Recipe you requested!")
					ingredient_list = []
					print("Please scan ONLY one of the Ingredients listed above to get started.")


	### Defines which type of weighing method the user needs based on scale input.
	### BATCHING: Currently activates large weighment system for large mixing operations eg. Littleford
	### PREWEIGH: Currently activates standard weighment system for things like mill & ross batches.
	### ADJUST: Currently does nothing, will eventually allow for batch adjustments based on supervisor badges.
	def scale_options(usr):
		while True:
			print("Please select an option on the scale to begin... ")
			scale = Scale.connect()
			if "BATCHING" in scale:
				print("Entering Large Scale Weighment System...")
				Scale.large_weighment(usr)
			if "PREWEIGH" in scale:
				print("Enter Single-Material/Batching Weighing System...")
				Scale.multi_batching(usr)
			if "ADJUST" in scale:
				print("Entering Batch Adjustment System...")
				break

class API():
	def pt(fields, rows):
		x = PrettyTable()
		x.field_names = fields
		x.padding_width = 1
		for r in rows:
			x.add_row(r)
		print(x)

class color:
	WARN = "\033[1;31;43m"
	FAIL = "\033[2;37;41m"
	END = "\033[0m"
