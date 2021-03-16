import serial
import binascii

import translatorNmea as tn
import translatorUbx as tu


## OPEN SERIAL PORT
ser = serial.Serial('/dev/tty.usbmodem14101', 9600)

# Flags for keeping track of syncing characters
readingMessage = False
readingPayload = False
readingChecksum = False
messageCounter = 0
payloadCounter = 0
checksumCounter = 0
payloadLength = 0

messageConcluded = False

# Temporary holding variable
previous_b_nmea = '00'
previous_b_ubx = '00'


# Message and payload holders
message = []
payload = []
checksum = []

# Let's set out syncinc characters
syncChar1 = 'b5'
syncChar2 = '62'

## READING LOOP
while True:
	## Read byte-by-byte
	b = ser.read()
	b_nmea = b
	# A bit of mix-and-match. If the $ byte is encountered, we read the full line, NMEA-style.
	# If not, we have to continue reading the byte, for UBX protocol.

	## NMEA READING
	if (previous_b_nmea == b'G') and (b_nmea == b'N'):
		# Bingo, it's a NMEA message, read the full payload
		bl = ser.readline()
		# Send it over to the NMEA translator
		tn.Translate(bl)
	
	## UBX READING 
	else:
		# Perform byte to hesxtring conversion, then decode to utf8 for convenience
		b_ubx = binascii.hexlify(b)
		b_ubx = b_ubx.decode('utf8')

		## Condition for frame reading
		if (previous_b_ubx == syncChar1) and (b_ubx == syncChar2):
			# Starting frame, setting flags and initialising
			messageCounter = 0
			payloadCounter = 0
			checksumCounter = 0
			message = []
			payload = []
			checksum = []
			readingMessage = True
			# Append syncing characters
			message.append(previous_b_ubx)
			message.append(b_ubx)

		## Reading UBX byte for class
		if readingMessage == True and messageCounter == 1:
			b_class = b_ubx
			message.append(b_ubx)

		## Reading UBX byte for class
		if readingMessage == True and messageCounter == 2:
			b_id = b_ubx
			message.append(b_ubx)

		## Reading UBX byte for payloadLength
		if readingMessage == True and messageCounter == 4:
			b_payloadLength = ''.join([b_ubx, previous_b_ubx])  # Little-endian
			payloadLength = int(b_payloadLength, 16)
			message.append(previous_b_ubx)
			message.append(b_ubx)
			## Starting payload, setting flags and initialising
			readingPayload = True
			payloadCounter = 0

		## Payload appending
		if readingPayload == True and messageCounter > 4:
			if payloadCounter < payloadLength:
				message.append(b_ubx)
				payload.append(b_ubx)
				payloadCounter += 1
			else:
				readingPayload = False
				readingChecksum = True
				checksumCounter = 0

		if payloadCounter == payloadLength and readingPayload == False and readingChecksum == True and checksumCounter < 2:
			message.append(b_ubx)
			checksum.append(b_ubx)
			checksumCounter += 1
		elif payloadCounter == payloadLength and readingPayload == False and readingChecksum == True and checksumCounter >= 2:
			messageConcluded = True

		if messageConcluded:
			readingMessage = False
			readingPayload = False
			readingChecksum = False
			messageCounter = 0
			payloadCounter = 0
			checksumCounter = 0

			messageConcluded = False

			tu.Translate(message,payload,checksum)
			print(message)

		
		### ENDING MATTERS
		# At the end of reading single bytes from UBX messages, update the counter
		if readingMessage == True:
			messageCounter += 1




	# Always update the previous byte
	previous_b_nmea = b_nmea
	previous_b_ubx = b_ubx






