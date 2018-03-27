from RobotArm import *
import time

robot = RobotArm("Duc")

current_distance = robot.readDistance()
target_distance = 15

print("=====> START: ", current_distance)
robot.forwardExact(target_distance)
print("=====> END: ", current_distance - 15)
ev3.Sound.beep()
time.sleep(2)

current_distance = robot.readDistance()
print("=====> START: ", current_distance)
robot.backwardExact(target_distance)
print("=====> END: ", current_distance + 15)
ev3.Sound.beep()
time.sleep(2)

robot.moveUp(0.05, 3)
while robot.isGoingUpDown():
    pass
robot.turnExact(-30)
robot.forwardExact(target_distance)
