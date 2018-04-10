from RobotArm import *
import time


# ==============Setting for tests======================
robot = RobotArm("Duc")

current_distance = robot.readDistance()
target_distance = 15

# ===============Test for forwardExact=================
print("=====> START: ", current_distance)
robot.forwardExact(target_distance)
print("=====> END: ", current_distance - 15)
# Wait before moving on to next test
ev3.Sound.beep()
time.sleep(2)

# =================Test for backwardExact================
current_distance = robot.readDistance()
print("=====> START: ", current_distance)
robot.backwardExact(target_distance)
print("=====> END: ", current_distance + 15)
# Wait before moving on to next test
ev3.Sound.beep()
time.sleep(2)

# =================Test for a series of motions============
robot.moveUp(0.05, 3)
while robot.isGoingUpDown():
    pass
robot.turnExact(-30)
robot.moveDown(0.05, 3)
while robot.isGoingUpDown():
    pass
robot.handHold()
robot.handRelease()
robot.moveUp(0.05,3)
while robot.isGoingUpDown():
    pass
robot.forwardExact(target_distance)
robot.turnExact(30)
robot.backwardExact(target_distance)

# TODO: COPY THIS FILE TO THE ROBOT BEFORE BEGINNING TO WORK

# ==========================================================
# =============== ALL TESTS DONE ===========================
ev3.Sound.speak("All tests completed!")
