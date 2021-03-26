import binascii
from textwrap import wrap
from datetime import datetime

from Database.sendMeasurements import SendMeasurement

## HEADER WORDS
headerWord1 = 'GNGSA'  # Quality of fix on field 2
headerWord2 = 'GNGNS' # Number of satellites on field 7

def Translate(payload):
	numSv = -1 # Set parameter to default error value
	posMode = -1 # Set parameter to default error value

	# Case for QUALITY OF FIX (GSA)
	if headerWord1 in payload:
		# Split the message in separate values
		values = payload.split(',')

		# Make sure you have all elements
		if len(values) < 18:
			print(f'CORRUPTED MESSAGE! -> {values}')
			print(values)
			print(f'len(GSA): {len(values)}<20')
			return
		# Extract values
		posMode = values[2]
		try:
			posMode = int(posMode)
		except:
			print(f'CORRUPTED MESSAGE! -> {values}')
			return
		# Finally send the measurement if everything is ok
		SendMeasurement('posMode',str(posMode))

	# Case for NUMBER OF SATELLITES (GNS)
	if headerWord2 in payload:
		# Split the message in separate values
		values = payload.split(',')

		# Make sure you have all elements
		if len(values) < 13:
			print(f'CORRUPTED MESSAGE! -> {values}')
			print(values)
			print(f'len(GSA): {len(values)}<20')
			return
		# Extract values
		numSv = values[7]
		try:
			numSv = int(numSv)
		except:
			print(f'CORRUPTED MESSAGE! -> {values}')
			return
		# Finally send the measurement if everything is ok
		SendMeasurement('numSv', str(numSv))
	
	return
