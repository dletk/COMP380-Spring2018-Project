from RobotArm import *
import time
robot = RobotArm("Robot")


robot.armRelease()
robot.turnMotorRelease()

in_command = input("Enter Y when ready: ")

if in_command.lower() == "y":
    robot.moveUp(0.05, 4)
    while robot.isGoingUpDown():
        pass
    time.sleep(1)
    robot.turnExact(-90)
    robot.moveDown(0.05, 2)
