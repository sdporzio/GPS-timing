import serial
import binascii
import subprocess
from datetime import datetime as dt

from Translator import translatorNmea as tn
from Translator import translatorUbx as tu


## OPEN SERIAL PORT
ser = serial.Serial('/dev/ttyACM0', 9600)

# Flags for keeping track of syncing characters
readingMessage = False
readingPayload = False
readingChecksum = False
messageCounter = 0
payloadCounter = 0
checksumCounter = 0
payloadLength = 0

# Flags for ensuring ubx timestamp is not missing a step
numberUbxTimestamps = 0
previousTimestamp = 0
isOneSecondApart = True

messageConcluded = False

# Temporary holding variable
previous_b_nmea = '00'
previous_b_ubx = '00'
b_register = []


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
	b_register.append(binascii.hexlify(b).decode('ascii','replace'))
	b_nmea = b
	# A bit of mix-and-match. If the $ byte is encountered, we read the full line, NMEA-style.
	# If not, we have to continue reading the byte, for UBX protocol.

	## NMEA READING
	if (previous_b_nmea == b'G') and (b_nmea == b'N'):
		# Bingo, it's a NMEA message, read the full payload
		bl = ser.readline()
		# Send it over to the NMEA translator
		tn.Translate(bl)
		print(f"{dt.now()} NMEA: {bl}")
		print(f"|- Previous line: {''.join(b_register)}")
		print()
		b_register = []
		# Shorten the log
		# subprocess.Popen(["/home/lhep/GPS-timing/Reader/Log/logCleaner.sh"],shell=True)
	
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

		if payloadCounter == payloadLength and readingPayload == False and readingChecksum == True and checksumCounter < 1:
			message.append(b_ubx)
			checksum.append(b_ubx)
			checksumCounter += 1
		elif payloadCounter == payloadLength and readingPayload == False and readingChecksum == True and checksumCounter >= 1:
			message.append(b_ubx)
			checksum.append(b_ubx)
			checksumCounter += 1
			messageConcluded = True

		if messageConcluded:
			readingMessage = False
			readingPayload = False
			readingChecksum = False
			messageCounter = 0
			payloadCounter = 0
			checksumCounter = 0

			messageConcluded = False

			currentTimestamp = tu.Translate(message,payload,checksum)
			numberUbxTimestamps += 1

			print(f"{dt.now()} UBX: {''.join(message)}")
			print(f"|- Timestamp: {currentTimestamp}")
			print(f"|- Previous line: {''.join(b_register)}")
			print()
			b_register = []
			# Shorten the log
			# subprocess.Popen(["/home/lhep/GPS-timing/Reader/Log/logCleaner.sh"],shell=True)

			### FINAL UBX TIMESTAMP CHECK
			# If we have read at least two timestamps, check that they are one second apart, if they are not flag it
			if numberUbxTimestamps > 1:
				timestampDiff = currentTimestamp-previousTimestamp
				isOneSecondApart = (timestampDiff < 2000)
			# Actual safe valve, if two timestamps are more than one second apart alt the whole thing
			if isOneSecondApart == False:
				print("Error: two consecutive timestamps are more than one second apart!")
				print(
					f"CurrT {currentTimestamp} - PrevT {previousTimestamp} = {timestampDiff}")
				break
			# If we have read at least one timestamp, we can start associating the current timestamp to the previous one
			if numberUbxTimestamps > 0:
				previousTimestamp = currentTimestamp


		
		### ENDING STUFF
		# At the end of reading single bytes from UBX messages, update the counter
		if readingMessage == True:
			messageCounter += 1


	# Always update the previous byte
	previous_b_nmea = b_nmea
	previous_b_ubx = b_ubx






