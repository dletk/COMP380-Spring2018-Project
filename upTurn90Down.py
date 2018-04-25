from RobotArm import *
import time
robot = RobotArm("Robot")


robot.armRelease()
robot.turnMotorRelease()

in_command = input("Enter Y when ready: ")

if in_command.lower() == "y":
    robot.pickUp()
    while robot.isGoingUpDown():
        pass

    robot.turnExact(60)
    robot.dropDown()
