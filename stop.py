# Small script to stop the robot
from RobotArm import *

robot = RobotArm("Duc")

robot.armRelease()
robot.stopMoving()
robot.stopTurning()
