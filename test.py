import serial
from time import sleep

ser = serial.Serial('/dev/ttyACM0', 9600)

while True:
    b = ser.readline()
    print(b)
# i = 0
# while(1):

#     try:
#         ser = serial.Serial('/dev/ttyACM0', 9600)
#         print('SUCCESS')
#         portOpen = True
#     except:
#         print('FAILURE')
#         portOpen = False
#     if portOpen:
#         continue
#     sleep(1)
#     print(f'iter: {i}')
#     i += 1

# print('You made it!')
