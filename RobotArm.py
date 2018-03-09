import ev3dev.ev3 as ev3
import time


class RobotArm(object):
    """The class to create a robot arm manager object."""

    # ---------------------------------------------------------------------------
    # Constants for the configDict
    TURNING_MOTOR = 'turning-motor'
    VERTICAL_MOVE_MOTOR = 'vertical-move-motor'
    HAND = 'hand'
    BOTTOM_TOUCH_SENSOR = 'bottom-touch'
    COLOR_SENSOR = 'color-sensor'
    GYRO_SENSOR = 'gyro-sensor'
    # ---------------------------------------------------------------------------

    # ---------------------------------------------------------------------------
    # The default config that the program will use if no config is given
    DEFAULT_CONFIG = {COLOR_SENSOR: "in3", BOTTOM_TOUCH_SENSOR: "in1",
                      TURNING_MOTOR: "outC", VERTICAL_MOVE_MOTOR: "outB", HAND: "outA", GYRO_SENSOR: "in2"}

    # ---------------------------------------------------------------------------

    def __init__(self, name, configDict=DEFAULT_CONFIG):
        """Take the configuration and set up the robot arm."""
        super(RobotArm, self).__init__()
        self.name = name
        self.turning_motor = None
        self.vertical_move_motor = None
        self.hand = None
        self.bottom_touch_sensor = None
        self.color_sensor = None
        self.gyro_sensor = None

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
            elif item == self.HAND:
                self.setUpMotor(item, port)
            elif item == self.BOTTOM_TOUCH_SENSOR:
                self.setUpTouchSensor(item, port)
            elif item == self.COLOR_SENSOR:
                self.setUpColorSensor(port)
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
        elif motorName == self.HAND:
            self.hand = ev3.MediumMotor(port)
        else:
            print("Cannot find the motor name: ", motorName)

    def setUpTouchSensor(self, touchSensorName, port):
        """Set up the touch sensor with given port."""
        if touchSensorName == self.BOTTOM_TOUCH_SENSOR:
            self.bottom_touch_sensor = ev3.TouchSensor(port)
        else:
            print("No device found named: ", touchSensorName)

    def setUpColorSensor(self, port):
        """Set up the color sensor with given port."""
        self.color_sensor = ev3.ColorSensor(port)

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

    def armRelease(self):
        """Method to release the arm from holding its position to coast.
        This method should be called when the arm does not need to hold its vertical
        position anymore, since it is bad to the motor"""
        self.vertical_move_motor.stop_action = "coast"
        self.vertical_move_motor.stop()

    def turnRight(self, speed, time=None):
        """Method to turn the arm to the right with speed from 0 to 1.
        If there is no given time, the arm will turn forever.
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
        self.turning_motor.wait_until_not_moving()

    def turnLeft(self, speed, time=None):
        """Method to turn the arm to the left with speed from 0 to 1.
        If there is no given time, the arm will turn forever.
        """
        self.turnRight(-speed, time)

    def turnMotorRelease(self):
        """Method to release the turning motor from holding"""
        self.turning_motor.stop_action = "coast"
        self.turning_motor.stop()
