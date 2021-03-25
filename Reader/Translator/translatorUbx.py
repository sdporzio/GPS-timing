
from datetime import datetime
from datetime import timedelta

from Database.sendMeasurements import SendMeasurement

def StringHexToSignedInt(value):
	s = bytes.fromhex(value)
	i = int.from_bytes(s, 'big', signed=True)
	return i


def Translate(message,payloadLength):
	b_syncChar1 = message[0]
	b_syncChar2 = message[1]
	b_class = message[2]
	b_id = message[3]
	b_length = message[4:6]

	b_payload = message[6:6+payloadLength]
	
	b_checksum1 = message[6+payloadLength]
	b_checksum2 = message[6+payloadLength+1]

	## Extract parameters
	b_towMs = b_payload[0:4]
	b_towSubMs = b_payload[4:8]
	b_qErr = b_payload[8:12]
	b_week = b_payload[12:14]
	b_flags = b_payload[14]
	b_refInfo = b_payload[15]

	## Little-endian conversion
	b_length = b_length[::-1]
	b_towMs = b_towMs[::-1]
	b_towSubMs = b_towSubMs[::-1]
	b_qErr = b_qErr[::-1]
	b_week = b_week[::-1]

	## base-10 conversion
	length = int(''.join(b_length), 16)
	towMs = int(''.join(b_towMs), 16)
	towSubMs = int(''.join(b_towSubMs), 16)
	# qErr = int''.join(b_qErr), 16)
	qErr = StringHexToSignedInt(''.join(b_qErr))
	week = int(''.join(b_week), 16)

	flag_binary = format(int(b_flags, 16), "08b")
	flag_qErrInvalid = flag_binary[3]
	flag_raim = flag_binary[4:6]
	flag_utc = flag_binary[6]
	flag_timebase = flag_binary[7]

	# Do some time conversion
	gps_startTime = datetime(1980, 1, 6, 0, 0, 0)
	tnow = gps_startTime + timedelta(weeks=week,milliseconds=towMs)
	utc_startTime = datetime(1970, 1, 1, 0, 0, 0)
	tnow_utc = (tnow-utc_startTime).total_seconds()

	tnow_sub = towSubMs*2^(-32)

	# Just to be on the safe side, send entire message
	SendMeasurement(f"ubx_message,message={''.join(message)}", 0)
	SendMeasurement("pulseTime", tnow_utc)
	SendMeasurement("pulseTime_sub", tnow_sub)
	SendMeasurement("qErr", qErr)
	SendMeasurement("flag_utc", flag_utc)
	SendMeasurement("flag_timebase", flag_timebase)
	SendMeasurement("flag_qErrInvalid", flag_qErrInvalid)
	# print(f'UBX {tnow_utc}')

	# Return the timestamp for reference
	return towMs

	# # Print out diagnostics
	# print(f'SyncChar: {b_syncChar1} {b_syncChar2}')
	# print(f'Class: {b_class}')
	# print(f'ID: {b_id}')
	# print(f'Length: {length} \t {b_length}')
	# print(f'Checksum: {b_checksum1} {b_checksum2}')
	# print()
	# print(f'TowMs: {towMs} ms \t {b_towMs}')
	# print(f'TowSubMs: {towSubMs} ms \t {b_towSubMs}')
	# print(f'qErr: {qErr} ps \t {b_qErr}')
	# print(f'Week: {week} \t {b_week}')
	# print()
	# print(f'Flags: {b_flags}')

	# print(f'RefInfo: {b_refInfo}')
	# print()
	# print("Full message:")
	# print(message)

