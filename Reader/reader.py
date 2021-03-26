import serial
import socket
import binascii
import subprocess
from datetime import datetime as dt

from Translator import translatorNmea as tn
from Translator import translatorUbx as tu


## OPEN SERIAL PORT FOR USB READING
ser = serial.Serial('/dev/ttyACM0', 9600)

## OPEN SOCKET FOR UDP COMMUNICATION
UDP_IP = "130.92.128.187" # argoncube27.aec.unibe.ch
UDP_PORT = 5005
sock = socket.socket(socket.AF_INET,  # Internet
                     socket.SOCK_DGRAM)  # UDP

# Message and payload holders
nmeaMessage = []
ubxMessage = []
misreadMessage_hex = []
misreadMessage_asc = []

# Let's set out syncinc characters
ubx_syncChar1 = 'b5'
ubx_syncChar2 = '62'
nmea_syncChar1 = '24'
nmea_syncChar2 = '47'
nmea_closeChar1 = '0d'
nmea_closeChar2 = '0a'

## READING LOOP
# The first time we read the message, the previous b gets a null value
prev_asc = ''
prev_hex = ''
while True:
	b = ser.read()
	b_asc = b.decode('ascii', 'replace')
	b_hex = binascii.hexlify(b).decode('ascii', 'replace')

	# NMEA MESSAGE CONDITION
	if prev_hex == nmea_syncChar1 and b_hex == nmea_syncChar2:

		# Let's check if there was any misread bits and reset the message
		if len(misreadMessage_hex)>1:
			print("ERROR! Misread characters!")
			print(f"HEX: {''.join(misreadMessage_hex[:-1])}")
			print(f"ASCII: {''.join(misreadMessage_asc[:-1])}")
		misreadMessage_hex = []
		misreadMessage_asc = []

		# We started a NMEA message
		nmeaMessage = []
		nmeaMessage.append(prev_asc)
		nmeaMessage.append(b_asc)
		stopNmea = False

		# We're looping a NMEA message
		while not stopNmea:
			
			# Let's keep reading bits in a loop
			b = ser.read()
			b_asc = b.decode('ascii', 'replace')
			b_hex = binascii.hexlify(b).decode('ascii', 'replace')

			# Keep appending bits to the message
			nmeaMessage.append(b_asc)

			# Two condition for stop reading. Either we reached the two closing characters
			# Or the string is getting too long and something's wrong
			endOfMessageCondition = (prev_hex==nmea_closeChar1) and (b_hex==nmea_closeChar2)
			tooLongCondition = len(nmeaMessage)>100
			stopNmea = endOfMessageCondition or tooLongCondition

			if stopNmea:
				print(f"{dt.now()}: fully read NMEA message")
				print(''.join(nmeaMessage))
				tn.Translate(''.join(nmeaMessage))

			### END-OF-NMEA-LOOP CONDITION
			prev_hex = b_hex

	# UBX MESSAGE CONDITION
	elif prev_hex==ubx_syncChar1 and b_hex==ubx_syncChar2:
		# Let's check if there was any misread bits and reset the message
		if len(misreadMessage_hex) > 1:
			print("ERROR! Misread characters!")
			print(f"HEX: {''.join(misreadMessage_hex[:-1])}")
			print(f"ASCII: {''.join(misreadMessage_asc[:-1])}")
		misreadMessage_hex = []
		misreadMessage_asc = []

		# We started a UBX message
		ubxMessage = []
		ubxMessage.append(prev_hex)
		ubxMessage.append(b_hex)
		stopUbx = False

		# We're setting an unrealistic message length
		# When the actual message length we'll be encountered
		# we will reduce this value to proper length
		payloadLength = 100

		# We're looping a NMEA message
		while not stopUbx:
			# Let's keep reading bits in a loop
			b = ser.read()
			b_asc = b.decode('ascii', 'replace')
			b_hex = binascii.hexlify(b).decode('ascii', 'replace')

			# Keep appending bits to the message
			ubxMessage.append(b_hex)
			if len(ubxMessage)==6:
				payloadLength = int(''.join([ubxMessage[-1],ubxMessage[-2]]),16) # Little-endian

			# Total messge length (2xsync/class/id/2xlength + payload + 2xchecksum)
			messageLength = 6 + payloadLength + 2

			# Two condition for stop reading. Either we reached the two closing characters
			# Or the string is getting too long and something's wrong
			endOfMessageCondition = len(ubxMessage)==messageLength
			tooLongCondition = len(ubxMessage) > 100
			stopUbx = endOfMessageCondition or tooLongCondition

			if stopUbx:
				print(f"{dt.now()}: fully read UBX message")
				print(''.join(ubxMessage),'\n')
				timestamp = tu.Translate(ubxMessage,payloadLength)
				sock.sendto(bytes(str(timestamp),'utf8'), (UDP_IP, UDP_PORT))

			### END-OF-NMEA-LOOP CONDITION
			prev_hex = b_hex

	# MIS-READ MESSAGE CONDITION
	else:
		misreadMessage_hex.append(b_hex)
		misreadMessage_asc.append(b_asc)

	# END-OF-LOOP CONDITION
	prev_hex = b_hex











 
