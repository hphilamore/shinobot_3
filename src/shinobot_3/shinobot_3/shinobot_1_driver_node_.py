#!/usr/bin/env python
from __future__ import print_function
import rospy
from dual_g2_hpmd_rpi import Motor, Motors, motors, MAX_SPEED
import time
from time import sleep
from std_msgs.msg import String
from std_msgs.msg import Float64
from geometry_msgs.msg import Twist
import message_filters
from rospy.numpy_msg import numpy_msg
from rospy_tutorials.msg import Floats
import numpy as np


# Define a custom exception to raise if a fault is detected.
class DriverFault(Exception):
    def __init__(self, driver_num):
        self.driver_num = driver_num

def raiseIfFault():
    if motors.motor1.getFault():
        raise DriverFault(1)
    if motors.motor2.getFault():
        raise DriverFault(2)

# # Set up sequences of motor speeds.
# test_forward_speeds = list(range(0, MAX_SPEED, 1)) + \
#   [MAX_SPEED] * 200 + list(range(MAX_SPEED, 0, -1)) + [0]  

# test_reverse_speeds = list(range(0, -MAX_SPEED, -1)) + \
#   [-MAX_SPEED] * 200 + list(range(-MAX_SPEED, 0, 1)) + [0]  

class Driver():
    def __init__(self):

        # Set variables for the GPIO motor pins
        self.motors = Motors()

        # Time for obstacle avoid operations
        self.Treverse = 2
        self.Tturn = 2 

        # Control variables 
        self.command = 'S'
        self.distance = None 
        self.obstacle = np.array([False, False, False], dtype=np.float32)

    def Stop(self):
        self.motors.motor1.setSpeed( 0 )
        self.motors.motor2.setSpeed( 0 )
        raiseIfFault()
        sleep(0.002)


    def Forwards(self):
        self.motors.motor1.setSpeed( MAX_SPEED/2 )
        self.motors.motor2.setSpeed( MAX_SPEED/2 )
        raiseIfFault()
        sleep(0.002)


    def Backwards(self):
        self.motors.motor1.setSpeed( -MAX_SPEED/2 )
        self.motors.motor2.setSpeed( -MAX_SPEED/2 )
        raiseIfFault()
        sleep(0.002)


    def Left(self):
        self.motors.motor1.setSpeed( MAX_SPEED/2 )
        self.motors.motor2.setSpeed( -MAX_SPEED/2 )
        raiseIfFault()
        sleep(0.002)


    def Right(self):
        self.motors.motor1.setSpeed( -MAX_SPEED/2 )
        self.motors.motor2.setSpeed( MAX_SPEED/2 )
        raiseIfFault()
        sleep(0.002)

    def drive(self):
        if self.command == 'F':
            print('Moving forwards')
            self.Forwards()
        elif self.command == 'B':
            print('Moving backwards')
            self.Backwards()
        elif self.command == 'L':
            print('Turning left')
            self.Left()
        elif self.command == 'R':
            print('Turning right')
            self.Right()
        elif self.command == 'S':
            print('Stopping')
            self.Stop()
        else:
            print('Unknown command, %s stopping instead' % self.command)
            self.Stop()


    def velocity_received_callback(self, message):
        """Handle new velocity command message."""
        #rospy.loginfo(rospy.get_caller_id() + "Linear vel = %s" + ", Angular vel = %s", message.linear.x, message.angular.z)
        #rospy.loginfo(rospy.get_caller_id() + "Angular vel = %s", message.angular.z)

        self._last_received = rospy.get_time()

        linear = message.linear.x
        angular = message.angular.z

        if ((linear>0) and (angular==0)):
            self.command = 'F'
        elif ((linear<0) and (angular==0)):
            self.command = 'B'
        elif ((linear==0) and (angular<0)):
            self.command = 'L'
        elif ((linear==0) and (angular>0)):
            self.command = 'R'
        elif ((linear==0) and (angular==0)):
            self.command = 'S'
        else:
            self.command = 'U'

        self.obstacleAvoid()
        #self.drive()

        #self.callback()

        # # Extract linear and angular velocities from the message
        # linear = message.linear.x
        # angular = message.angular.z

        # # Calculate wheel speeds in m/s
        # left_speed = linear - angular*self._wheel_base/2
        # right_speed = linear + angular*self._wheel_base/2

        # # Ideally we'd now use the desired wheel speeds along
        # # with data from wheel speed sensors to come up with the
        # # power we need to apply to the wheels, but we don't have
        # # wheel speed sensors. Instead, we'll simply convert m/s
        # # into percent of maximum wheel speed, which gives us a
        # # duty cycle that we can apply to each motor.
        # self._left_speed_percent = (100 * left_speed/self._max_speed)
        # self._right_speed_percent = (100 * right_speed/self._max_speed)


    def storeCommand(self, data):
        rospy.loginfo(rospy.get_caller_id() + "Command is %s", data.data)
        self.command = data.data
        print(self.command, self.distance)
        # self.callback()
        self.obstacleAvoid()


    def storeDistance(self, data):
        #rospy.loginfo(rospy.get_caller_id() + "Distance is %s", data.data)
        self.distance = data.data
        self.obstacle = self.distance<100 # any objects closer than 100mm
        #rospy.loginfo("cmd = %s" + ", dist = %s" + ", obs = %s" + ", !!! = %s", 
            #self.command, self.distance, self.obstacle, self.obstacle.any())
        #print(self.distance, self.command, self.obstacle)
        # self.callback()
        self.obstacleAvoid()


    


    def obstacleAvoid(self): 

        if self.command == 'S':
            print('Stopping')
            self.Stop()
        
        elif self.obstacle.any():
            rospy.loginfo("Obstacle!!!")

            # Back off a little 
            inittime = time.time() 
            now = time.time() 

            print("Reversing...") 
            while (now - inittime) <= self.Treverse:    
                self.Backwards() 
                now = time.time() 

            self.Stop() 
            inittime = time.time() 
            now = time.time() 

            print("Turning...") 
            while (now - inittime) <= self.Tturn:
                self.Right() 
                now = time.time() 

            self.Stop() 

        else:
            self.drive()



    # # Message handler
    # def callback(self):

    #     #if self.distance < 20:
    #     if self.distance != None:
    #         # print('Moving forwards')
    #         # Forwards()
    #         self.obstacleAvoid()

    #     else:

    #         if self.command == 'F':
    #             print('Moving forwards')
    #             self.Forwards()
    #         elif self.command == 'B':
    #             print('Moving backwards')
    #             self.Backwards()
    #         elif self.command == 'L':
    #             print('Turning left')
    #             self.Left()
    #         elif self.command == 'R':
    #             print('Turning right')
    #             self.Right()
    #         elif self.command == 'S':
    #             print('Stopping')
    #             self.Stop()
    #         else:
    #             print('Unknown command, %s stopping instead' % self.command)
    #             self.Stop()






    # def obstacleAvoid(self): 
    #     # Back off a little 
    #     inittime = time.time() 
    #     now = time.time() 

    #     print("Reversing...") 
    #     while (now - inittime) <= self.Treverse:    
    #         self.Backwards() 
    #         now = time.time() 

    #     self.Stop() 
    #     inittime = time.time() 
    #     now = time.time() 

    #     print("Turning...") 
    #     while (now - inittime) <= self.Tturn:
    #         self.Right() 
    #         now = time.time() 

    #     self.Stop() 



    def driver(self):
        rospy.init_node('driver')
        #rospy.Subscriber('command', String, self.storeCommand, queue_size=1)
        rospy.Subscriber('cmd_vel', Twist, self.velocity_received_callback)
        #rospy.Subscriber('distance_sense', Float64, self.storeDistance, queue_size=1)
        rospy.Subscriber('distance_sense', numpy_msg(Floats), self.storeDistance, queue_size=1)
        self.obstacleAvoid()
        #self.drive()
        rospy.spin()

        

if __name__ == '__main__':
    driver = Driver()
    try:
        driver.driver()


    except rospy.ROSInterruptException:
        pass

    except KeyboardInterrupt:
        # Reset GPIO settings 
        print('Shutting down: stopping motors')
        #StopMotors()
        motors.forceStop()
        sys.exit()