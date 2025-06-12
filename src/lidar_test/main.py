# Adapted from : https://github.com/takamatsu-shyo/LIDAR_LD06_python_loder

import serial
import binascii
from CalcLidarData import CalcLidarData
# import matplotlib.pyplot as plt
import math

# COLOR = 'cyan'
# plt.rcParams['text.color'] = COLOR
# plt.rcParams['axes.labelcolor'] = COLOR
# plt.rcParams['xtick.color'] = COLOR
# plt.rcParams['ytick.color'] = COLOR

# fig = plt.figure(facecolor='black', figsize=(8,8))
# ax = fig.add_subplot(111, projection='polar')
# ax.set_title('LiDAR LD06 (exit: e)',fontsize=18)
# ax.set_facecolor('navy')
# ax.set_ylim([0,20])
# ax.xaxis.grid(True,color='blue',linestyle='dashed')
# ax.yaxis.grid(True,color='blue',linestyle='dashed')


# Eキーを押すと終了します。
# plt.connect('key_press_event', lambda event: exit(1) if event.key == 'e' else None)

# ser = serial.Serial(port='/dev/ttyUSB0',
#                     baudrate=230400,
#                     timeout=5.0,
#                     bytesize=8,
#                     parity='N',
#                     stopbits=1)

ser = serial.Serial(port='/dev/ttyAMA0', 
                    baudrate=230400, 
                    timeout=0.5)

print('Serial channel open')

tmpString = ""
lines = list()
angles = list()
distances = list()

i = 0
while True:
    loopFlag = True
    flag2c = False

    # print('angles: ', angles)
    # print('distances: ', distances)

    # if(i % 40 == 39):
    #     # if('line' in locals()):
    #     #     line.remove()
    #     # line = ax.scatter(angles, distances, c="cyan", s=5)

    #     # ax.set_theta_offset(math.pi / 2)
    #     # plt.pause(0.01)
    #     angles.clear()
    #     distances.clear()
    #     i = 0

    if len(angles) >= 1080:  # LD06 gives ~3-5 points per degree; 1080 = 360 x 3
        # Sort by angle
        angle_distance_pairs = sorted(zip(angles, distances), key=lambda x: x[0])
        angles, distances = zip(*angle_distance_pairs)

        # [Optional] Do something with the full 360° data here
        print("Collected full 360° data")
        print("Angles:", angles)
        print("Distances:", distances)

        # Reset for next cycle
        angles = []
        distances = []


    while loopFlag:
        b = ser.read()
        tmpInt = int.from_bytes(b, 'big')
        
        if (tmpInt == 0x54):
            tmpString +=  b.hex()+" "
            flag2c = True
            continue
        
        elif(tmpInt == 0x2c and flag2c):
            tmpString += b.hex()

            if(not len(tmpString[0:-5].replace(' ','')) == 90 ):
                tmpString = ""
                loopFlag = False
                flag2c = False
                continue

            lidarData = CalcLidarData(tmpString[0:-5])



            angles.extend(lidarData.Angle_i)
            distances.extend(lidarData.Distance_i)
                
            tmpString = ""
            loopFlag = False
        else:
            tmpString += b.hex()+" "
        
        flag2c = False
    
    i +=1

ser.close()
