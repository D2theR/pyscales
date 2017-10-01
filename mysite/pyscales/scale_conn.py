import json
import serial
import time
from channels import Group


def ws_connect(message):
	vserial1 = serial.Serial(port='/dev/tnt1', baudrate=9600, bytesize=8, parity=serial.PARITY_EVEN, stopbits=1)
	n_bytes = 0
	Group('scale').add(message.reply_channel)
	while n_bytes >= 0:	
		if n_bytes == 0:
			n_bytes = vserial1.inWaiting()
			message.reply_channel.send({'text': json.dumps({'test': 'Waiting...'})})
			time.sleep(0.5)
		if n_bytes > 0:
			n_bytes = vserial1.inWaiting()
			message.reply_channel.send({
				'text': json.dumps({'scale_data':str(vserial1.read(n_bytes)).strip()})})
			time.sleep(0.5)