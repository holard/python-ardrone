
import pygame

import libardrone

# Each pair in the path should be (<command>, <duration in milliseconds>)
# Available commands: hover, forward, backward, left, right, up, down, turn_left, turn_right
path = [("hover", 1000), ("turn_left", 1500), ("hover", 1000), ("turn_right", 1500), ("hover", 1000)]

def main():
    drone = libardrone.ARDrone()
    drone.takeoff()
    pygame.time.delay(3000)
    drone.hover()
    pygame.time.delay(2000)
    for (action, duration) in path:
        print "next action:", action, "duration:", duration
        if action == "backward":
            drone.move_backward()
        elif action == "hover":
            drone.hover()
        elif action == "forward":
            drone.move_forward()
        elif action == "left":
            drone.move_left()
        elif action == "right":
            drone.move_right()
        elif action == "up":
            drone.move_up()
        elif action == "down":
            drone.move_down()
        elif action == "turn_left":
            drone.turn_left()
        elif action == "turn_right":
            drone.turn_right()
        pygame.time.delay(duration)
    drone.hover()
    pygame.time.delay(3000)
    drone.land()

if __name__ == '__main__':
    main()
