import serial
import binascii
from textwrap import wrap
from datetime import datetime

from Database.sendMeasurements import SendMeasurement

## HEADER WORDS
headerWord1 = b'GSA'  # Quality of fix on field 2
headerWord2 = b'GNS' # Number of satellites on field 7

def Translate(payload):
	numSv = -1 # Set parameter to default error value
	posMode = -1 # Set parameter to default error value

	# Case for QUALITY OF FIX (GSA)
	if headerWord1 in payload:
		failedMessage = False
		# Decode message and split it in values
		s = payload.decode('ascii', 'replace')
		values = s.split(',')
		# Find the position of the header
		headerIndex = 0
		for i, v in enumerate(values):
			if headerWord1.decode('ascii') in v:
				headerIndex = i
		# Make sure you have all elements
		if len(values) < 18:
			failedMessage = True
			print(f'CORRUPTED MESSAGE! -> {s}')
			print(values)
			print(f'len(GSA): {len(values)}<20')
			return
		# Extract values
		posMode = values[headerIndex+2]
		try:
			posMode = int(posMode)
		except:
			failedMessage = True
			print(f'CORRUPTED MESSAGE! -> {s}')
			return
		# Finally send the measurement if everything is ok
		# print(datetime.now(), 'posMode', posMode)
		SendMeasurement('posMode',str(posMode))

	# Case for NUMBER OF SATELLITES (GNS)
	if headerWord2 in payload:
		failedMessage = False
		# Decode message and split it in values
		s = payload.decode('ascii','replace')
		values = s.split(',')
		# Find the position of the header
		headerIndex = 0
		for i,v in enumerate(values):
			if headerWord2.decode('ascii') in v:
				headerIndex = i
		# Make sure you have all elements
		if len(values)<13:
			failedMessage = True
			print(f'CORRUPTED MESSAGE! -> {s}')
			print(f'len(GNS): {len(values)}<15')
			return
		# Extract values
		numSv = values[headerIndex+7]
		try:
			numSv = int(numSv)
		except:
			failedMessage = True
			print(f'CORRUPTED MESSAGE! -> {s}')
			return
		# Finally send the measurement if everything is ok
		# print(datetime.now(), 'numSv', numSv)
		SendMeasurement('numSv', str(numSv))
	
	return
