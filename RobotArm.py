import ev3dev.ev3 as ev3
import time


class RobotArm(object):
    """The class to create a robot arm manager object."""

    # ---------------------------------------------------------------------------
    # Constants for the configDict
    TURNING_MOTOR = 'turning-motor'
    VERTICAL_MOVE_MOTOR = 'vertical-move-motor'
    SURFACE_MOVE_MOTOR = "surface-move-motor"
    HAND = 'hand'
    BOTTOM_TOUCH_SENSOR = 'bottom-touch'
    ULTRASONIC_SENSOR = 'ultrasonic-sensor'
    GYRO_SENSOR = 'gyro-sensor'
    # ---------------------------------------------------------------------------

    # ---------------------------------------------------------------------------
    # The default config that the program will use if no config is given
    DEFAULT_CONFIG = {ULTRASONIC_SENSOR: "in3", BOTTOM_TOUCH_SENSOR: "in2",
                      TURNING_MOTOR: "outC", VERTICAL_MOVE_MOTOR: "outB", HAND: "outD", GYRO_SENSOR: "in4", SURFACE_MOVE_MOTOR: "outA"}

    # ---------------------------------------------------------------------------

    def __init__(self, name="Duc", configDict=DEFAULT_CONFIG):
        """Take the configuration and set up the robot arm."""
        super(RobotArm, self).__init__()
        self.name = name
        self.turning_motor = None
        self.vertical_move_motor = None
        self.surface_move_motor = None
        self.hand = None
        self.bottom_touch_sensor = None
        self.ultrasonic_sensor = None
        self.gyro_sensor = None

        # ====== Variable to control the state of the arm
        self.handIsHolding = False
        self.pickingUpMode = False

        if configDict is not None:
            # Call the set up method with configDict
            self.setUpMotorsSensors(configDict)
        else:
            # Call the set up method with DEFAULT_CONFIG
            self.setUpMotorsSensors(self.DEFAULT_CONFIG)

    def setUpMotorsSensors(self, configDict):
        """Set up the motors and sensors based on configDict input."""
        for item in configDict:
            port = configDict[item]
            if item == self.TURNING_MOTOR:
                self.setUpMotor(item, port)
            elif item == self.VERTICAL_MOVE_MOTOR:
                self.setUpMotor(item, port)
            elif item == self.SURFACE_MOVE_MOTOR:
                self.setUpMotor(item, port)
            elif item == self.HAND:
                self.setUpMotor(item, port)
            elif item == self.BOTTOM_TOUCH_SENSOR:
                self.setUpTouchSensor(item, port)
            elif item == self.ULTRASONIC_SENSOR:
                self.setUpUltrasonicSensor(port)
            elif item == self.GYRO_SENSOR:
                self.setUpGyroSensor(port)
            else:
                print("Error while setting, no device name: ", item)

    def setUpMotor(self, motorName, port):
        """Set upt the motor with given port."""
        if motorName == self.TURNING_MOTOR:
            self.turning_motor = ev3.LargeMotor(port)
        elif motorName == self.VERTICAL_MOVE_MOTOR:
            self.vertical_move_motor = ev3.LargeMotor(port)
        elif motorName == self.SURFACE_MOVE_MOTOR:
            self.surface_move_motor = ev3.LargeMotor(port)
            # The movement should hold position all the time for accurate calculation
            self.surface_move_motor.stop_action = "hold"
        elif motorName == self.HAND:
            self.hand = ev3.MediumMotor(port)
            self.hand.speed_sp = self.hand.max_speed // 10
        else:
            print("Cannot find the motor name: ", motorName)

    def setUpTouchSensor(self, touchSensorName, port):
        """Set up the touch sensor with given port."""
        if touchSensorName == self.BOTTOM_TOUCH_SENSOR:
            self.bottom_touch_sensor = ev3.TouchSensor(port)
        else:
            print("No device found named: ", touchSensorName)

    def setUpUltrasonicSensor(self, port):
        """Set up the ultrasonic sensor with given port."""
        self.ultrasonic_sensor = ev3.UltrasonicSensor(port)
        self.ultrasonic_sensor.mode = "US-DIST-CM"

    def setUpGyroSensor(self, port):
        """Set up the gyro sensor with given port."""
        self.gyro_sensor = ev3.GyroSensor(port)
        self.setHeading()

    def setHeading(self):
        """Set the heading of the robot to the current direction"""
        if self.gyro_sensor is not None:
            self.gyro_sensor.mode = "GYRO-CAL"
            time.sleep(0.2)
            self.gyro_sensor.mode = "GYRO-ANG"
            self.gyro_sensor.mode = "GYRO-CAL"
            time.sleep(0.2)
            self.gyro_sensor.mode = "GYRO-ANG"
        else:
            print("Cannot find gyro sensor")

    def readDistance(self):
        """Method to read the current distance to the nearest wall in front"""
        if self.ultrasonic_sensor is not None:
            return self.ultrasonic_sensor.distance_centimeters
        else:
            print("Cannot find the ultrasonic sensor")

    def readTouch(self):
        """Method to read the current value of the touch sensor"""
        if self.bottom_touch_sensor is not None:
            return self.bottom_touch_sensor.value()
        else:
            print("Cannot find the touch sensor")

    def readHeading(self):
        """Read the heading of the robot from 0 to 359, the origin is set at the
        last time setHeading is called
        The heading is to the right side of the origin
        """
        if self.gyro_sensor is not None:
            angle = self.gyro_sensor.angle
            if angle < 0:
                # With the current design, the left direction will be negative result
                return 360 - abs(angle) % 360
            else:
                # If the angle is positive, that means the robot has turned right
                return angle % 360

        else:
            print("Cannot find gyro sensor")

    def moveUp(self, speed, time=None):
        """Method to move the arm up with speed from 0 to 1. If there is no given
        time (in seconds), the arm will move up forever.
        The arm will hold its position with stop_action="hold"
        """
        # Calculate the speed to move up
        # Speed is negative to go up
        speed = -(self.vertical_move_motor.max_speed * speed)

        # Set the speed of motor
        self.vertical_move_motor.speed_sp = speed
        # Hold the position after moving up
        self.vertical_move_motor.stop_action = "hold"

        if time is None:
            self.vertical_move_motor.run_forever()
        else:
            # Time is in seconds, so convert it to miliseconds
            self.vertical_move_motor.run_timed(time_sp=time * 1000)
        self.vertical_move_motor.wait_until_not_moving()

    def moveDown(self, speed, time=None):
        """Method to move the arm down with speed from 0 to 1. If there is no given
        time (in seconds), the arm will move down forever.
        The arm will hold its position with stop_action="hold"
        """
        self.moveUp(speed=-speed, time=time)

    def forward(self, speed, time=None, wait_until_not_moving=True):
        """Method to move the arm forward. If there is no given time, the arm will move
        forward forever."""
        # Calculate speed to move
        # With the design of the robot, negative speed will make it forward
        self.surface_move_motor.speed_sp = \
            -(self.surface_move_motor.max_speed * speed)

        if time is None:
            self.surface_move_motor.run_forever()
        else:
            # Time is in seconds, so convert it to miliseconds
            self.surface_move_motor.run_timed(time_sp=time * 1000)
        if wait_until_not_moving:
            self.surface_move_motor.wait_until_not_moving()

    def backward(self, speed, time=None, wait_until_not_moving=True):
        """Method to move the arm backward. If there is no given time, the arm will move
        backward forever"""
        self.forward(-speed, time, wait_until_not_moving)

    def forwardExact(self, distance, speed=0.05):
        """Method to move the arm forward with the exact distance in cm. The speed
        of movement is optional, and should NOT be provided unless there is an absolute need."""
        if distance <= 0:
            print("Incorrect input for distance, distance should be larger than 0.")
            return

        current_distance_to_wall = self.readDistance()
        target_distance = current_distance_to_wall - distance

        # Begin movement
        self.forward(speed, wait_until_not_moving=False)
        # Check for distance
        while True:
            current_distance = self.readDistance()

            if current_distance <= target_distance:
                self.stopMoving()
                return

    def backwardExact(self, distance, speed=0.05):
        """Method to move the arm backward with the exact distance in cm. The speed
        of movement is optional and should NOT be provided unless there is there is
        an absolute need."""
        if distance <= 0:
            print("Incorrect input for distance, distance should be larger than 0.")
            return

        current_distance_to_wall = self.readDistance()
        target_distance = current_distance_to_wall + distance

        # Begin movement
        self.backward(speed, wait_until_not_moving=False)
        # Check for distance
        while True:
            current_distance = self.readDistance()

            if current_distance >= target_distance:
                self.stopMoving()
                return

    def stopMoving(self):
        """Method to stop the surface movement"""
        self.surface_move_motor.stop()
        return True

    def armRelease(self):
        """Method to release the arm from holding its position to coast.
        This method should be called when the arm does not need to hold its vertical
        position anymore, since it is bad to the motor"""
        self.vertical_move_motor.stop_action = "coast"
        self.vertical_move_motor.stop()
        self.pickingUpMode = False

    def armToStraightPosition(self):
        """
        Method to move the arm to the straight position to prepare for picking up
        Notice: Only call after armRelease and the hand is rested on surface.
        """
        self.moveUp(0.05, 5)
        self.pickingUpMode = True

    def turnRight(self, speed, time=None, wait_until_not_moving=True):
        """
        Method to turn the arm to the right with speed from 0 to 1.
        If there is no given time, the arm will turn forever.
        wait_until_not_moving will make sure the robot stop before doing the next command, set this
        to False if needed to do some checking while turning
        """
        # In the current setting, a positive speed will make the robot turn right
        speed = self.turning_motor.max_speed * speed
        self.turning_motor.speed_sp = speed

        # Set the arm to hold its position after turning
        self.turning_motor.stop_action = "hold"

        if time is None:
            self.turning_motor.run_forever()
        else:
            self.turning_motor.run_timed(time_sp=time * 1000)
        if wait_until_not_moving:
            self.turning_motor.wait_until_not_moving()

    def turnLeft(self, speed, time=None, wait_until_not_moving=True):
        """Method to turn the arm to the left with speed from 0 to 1.
        If there is no given time, the arm will turn forever.
        wait_until_not_moving will make sure the robot stop before doing the next command, set this
        to False if needed to do some checking while turning
        """
        self.turnRight(-speed, time, wait_until_not_moving)

    def turnMotorRelease(self):
        """Method to release the turning motor from holding"""
        self.turning_motor.stop_action = "coast"
        self.turning_motor.stop()

    def handHold(self):
        """Method to wrap an object"""
        if not self.handIsHolding:
            self.hand.speed_sp = -self.hand.speed_sp
            self.hand.stop_action = "hold"
            self.hand.run_timed(time_sp=1000)
            self.handIsHolding = True

            # Make sure to wait_until_not_moving
            self.hand.wait_until_not_moving()

    def handRelease(self):
        """Method to release an object from hand"""
        if self.handIsHolding:
            # Find the current sign of speed in order to reset the speed later
            current_sign_of_speed = 1 if abs(
                self.hand.speed_sp) == self.hand.speed_sp else -1

            # Make sure the hand is not in hold for too long (getting hot)
            self.hand.stop_action = "coast"
            self.hand.stop()

            # Use the opposite speed to release object
            self.hand.speed_sp = - self.hand.speed_sp
            self.hand.run_timed(time_sp=500)

            # Reset the speed with correct sign so handHold can work properly
            self.hand.speed_sp = current_sign_of_speed * self.hand.max_speed // 10
            self.handIsHolding = False

            # Make sure to wait until not moving
            self.hand.wait_until_not_moving()

    def stopTurning(self):
        """Method to stop the turning_motor"""
        self.turning_motor.stop()
        return True

    def turnExact(self, angle, speed=0.05):
        """Method to turn the arm to left or right with the exact angle
        If the angle value is positive, turn to the right.
        If the angle value is negative, tur to the left.
        """
        # Make sure there will be no turn if angle = 0
        if angle == 0:
            return
        # Set the current heading to be origin 0
        self.setHeading()

        # Find out the targeted angle
        targetHeading = angle if angle > 0 else 360 - abs(angle)
        print("=====> TARGET HEADING: ", targetHeading)
        acceptedRange = range(targetHeading - 1, targetHeading + 2)
        print("=====> ACCEPTED RANGE: ", acceptedRange)
        if angle < 0:
            # Initiate the left turn
            self.turnLeft(speed, wait_until_not_moving=False)
        else:
            # Initiate the right turn
            self.turnRight(speed, wait_until_not_moving=False)
        while True:
            # Accept error of 1 degree
            currentHeading = self.readHeading()
            print("===> CURRENT HEADING: ", currentHeading)
            if currentHeading in acceptedRange:
                self.stopTurning()
                break

    def turnToStartPosition(self):
        """Method to turn the arm to the starting position (until touch the Touch sensor)"""
        self.turnRight(0.05, time=None, wait_until_not_moving=False)
        while not self.readTouch():
            pass
        self.turning_motor.stop()


    def pickUp(self):
        """Method to pick up an object"""
        if not self.pickingUpMode:
            # If the robot is not in the ready state for picking up object, prepare for it
            # Move the robot to the position
            self.armToStraightPosition()
            print("Ready to conduct pickUp")
        # Ready to do the pick up work
        self.moveDown(0.05, 1.8)

        while self.isGoingUpDown():
            pass
        self.handHold()

        while self.isUsingHand():
            pass

        self.moveUp(0.05, 2)
        while self.isGoingUpDown():
            pass

    def dropDown(self):
        """Method to drop an object"""
        if self.pickingUpMode:
            # Only work when the robot is in picking mode
            self.moveDown(0.05, 1.8)

            while self.isGoingUpDown():
                pass
            self.handRelease()

            while self.isUsingHand():
                pass

            self.moveUp(0.05, 2)
            while self.isGoingUpDown():
                pass

    def isTurning(self):
        """Method to check whether the arm is turning"""
        return self.turning_motor.is_running

    def isMoving(self):
        """Method to check whether the arm is moving on the surface"""
        return self.surface_move_motor.is_running

    def isGoingUpDown(self):
        """Method to check whether the arm is moving up or down"""
        return self.vertical_move_motor.is_running

    def isUsingHand(self):
        """Method to check whether the hand is being used"""
        return self.hand.is_running
