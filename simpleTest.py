import serial
import datetime
import binascii
from textwrap import wrap

def StringHexToSignedInt(value):
	s = bytes.fromhex(value)
	i = int.from_bytes(s, 'big', signed=True)
	return i


def StudyMessage(message,payload,checksum):
	b_syncChar1 = message[0]
	b_syncChar2 = message[1]
	b_class = message[2]
	b_id = message[3]
	b_length = message[4:6]
	
	b_checksum1 = checksum[0]
	b_checksum2 = checksum[1]

	## Extract parameters
	b_towMs = payload[0:4]
	b_towSubMs = payload[4:8]
	b_qErr = payload[8:12]
	b_week = payload[12:14]
	b_flags = payload[14]
	b_refInfo = payload[15]

	## Little-endian conversion
	b_length = b_length[::-1]
	b_towMs = b_towMs[::-1]
	# b_towSubMs = b_towSubMs[::-1]
	b_qErr = b_qErr[::-1]
	b_week = b_week[::-1]

	## base-10 conversion
	length = int(''.join(b_length), 16)
	towMs = int(''.join(b_towMs), 16)
	towSubMs = int(''.join(b_towSubMs), 16)
	# qErr = int''.join(b_qErr), 16)
	qErr = StringHexToSignedInt(''.join(b_qErr))
	week = int(''.join(b_week), 16)

	## Print out diagnostics
	print(f'SyncChar: {b_syncChar1} {b_syncChar2}')
	print(f'Class: {b_class}')
	print(f'ID: {b_id}')
	print(f'Length: {length} \t {b_length}')
	print(f'Checksum: {b_checksum1} {b_checksum2}')
	print()
	print(f'TowMs: {towMs} ms \t {b_towMs}')
	print(f'TowSubMs: {towSubMs} ms \t {b_towSubMs}')
	print(f'qErr: {qErr} ps \t {b_qErr}')
	print(f'Week: {week} \t {b_week}')
	print()
	print(f'Flags: {b_flags}')
	print(f'RefInfo: {b_refInfo}')
	print()
	print("Full message:")
	print(message)


## Serial port
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
previous_b = '00'

# Message and payload holders
message = []
payload = []
checksum = []

# Let's set out syncinc characters
syncChar1 = 'b5'
syncChar2 = '62'


# Let's start reading
while True:
	## Read byte-by-byte
	b = ser.read()

	## Perform byte to hesxtring conversion, then decode to utf8 for convenience
	b = binascii.hexlify(b)
	b = b.decode('utf8')

	## Condition for frame reading
	if (previous_b==syncChar1) and (b==syncChar2):
		# Starting frame, setting flags and initialising
		messageCounter = 0
		payloadCounter = 0
		checksumCounter = 0
		message = []
		payload = []
		checksum = []
		readingMessage = True
		# Append syncing characters
		message.append(previous_b)
		message.append(b)

	## Reading UBX byte for class
	if readingMessage==True and messageCounter==1:
		b_class = b
		message.append(b)

	## Reading UBX byte for class
	if readingMessage==True and messageCounter==2:
		b_id = b
		message.append(b)

	## Reading UBX byte for payloadLength
	if readingMessage==True and messageCounter==4:
		b_payloadLength = ''.join([b,previous_b]) # Little-endian
		payloadLength = int(b_payloadLength,16)
		message.append(previous_b)
		message.append(b)
		## Starting payload, setting flags and initialising
		readingPayload = True
		payloadCounter = 0

	## Payload appending
	if readingPayload==True and messageCounter>4:
		if payloadCounter<payloadLength:
			message.append(b)
			payload.append(b)
			payloadCounter += 1
		else:
			readingPayload = False
			readingChecksum = True
			checksumCounter = 0

	if payloadCounter==payloadLength and readingPayload==False and readingChecksum==True and checksumCounter<2:
		message.append(b)
		checksum.append(b)
		checksumCounter += 1
	elif payloadCounter==payloadLength and readingPayload==False and readingChecksum==True and checksumCounter>=2:
		messageConcluded = True    

	if messageConcluded:
		readingMessage = False
		readingPayload = False
		readingChecksum = False
		messageCounter = 0
		payloadCounter = 0
		checksumCounter = 0

		messageConcluded = False

		print("Message concluded")
		StudyMessage(message, payload, checksum)
		print('===========================================================')

	### ENDING MATTERS
	# At the end of reading single bytes from UBX messages, update the counter
	if readingMessage==True:
			messageCounter += 1
	# Always update the previous byte
	previous_b = b
