
import cv2
import imutils
import libardrone
import pygame

# Windows dependencies
# - Python 2.7.6: http://www.python.org/download/
# - OpenCV: http://opencv.org/
# - Imutils 0.4.3: https://pypi.python.org/pypi/imutils
# - Pygame 1.9.3: https://pypi.python.org/pypi/Pygame/1.9.3

# Mac Dependencies
# - brew install python
# - pip install imutils
# - pip install pygame
# - brew tap homebrew/science
# - brew install opencv

# This program controls a connected Parrot AR Drone and tracks objects of a
# specified color range (currently blue). It uses OpenCV to find the object in
# the drone's camera frame, and moves to follow it based on size/position.
#
# Known Issues: 
# - Matching color can be sensitive to lighting and poor camera quality. 
# - Altitude sensors sometimes report incorrect values, and cause drone to
#       dip or fly too high. The libardrone library does not provide the raw
#       ultrasonic sensor readings, but only the final computed altitude.

# Constants:
WIDTH = 400                 # Width on screen
W2 = WIDTH/2
TIMEOUT_FRAMES = 900        # Lands after this many frames (30 fps)
colorLower = (100, 80, 80)   # Lower bound for color tracking, in HSV (0-180, 0-255, 0-255)
colorUpper = (135, 255, 255) # Upper bound for color tracking, in HSV (0-180, 0-255, 0-255)
BACK_THRESHOLD = 60         # Drone backs up if object in frame is larger than this threshold
FORWARD_THRESHOLD = 25      # Drone moves forward if object in frame is smaller
MIN_ALTITUDE = 800          # Keep drone above this height in mm
MAX_ALTITUDE = 1500         # Keep drone below this height in mm
    
# moves up or down if drone's reported altitude is outside of the defined range
def manage_altitude(drone):
    altitude = drone.navdata.get(0, dict()).get('altitude', 0)
    print "altitude:", altitude
    if altitude < MIN_ALTITUDE:
        drone.move_up()
        print "up"
    elif altitude > MAX_ALTITUDE:
        drone.move_down()
        print "down"
    else:
        print "hover"
        drone.hover()

# decides whether to turn or move based on tracked object's position and size
def handle_movement(drone, x, radius):
    if x < WIDTH / 3:
        if radius > BACK_THRESHOLD:
            drone.speed = 0.1
            drone.move_backward()
            print "moving backard"
        else:
            drone.speed = 0.2
            drone.turn_left()
            print "turning left"
    elif x > (WIDTH / 3) * 2:
        if radius > BACK_THRESHOLD:
            drone.speed = 0.1
            drone.move_backward()
            print "moving backard"
        else:
            drone.speed = 0.2
            drone.turn_right()
            print "turning right"
    else:
        if radius < FORWARD_THRESHOLD:
            drone.speed = 0.1
            drone.move_forward()
            print "moving forward"
        elif radius > BACK_THRESHOLD:
            drone.speed = 0.1
            drone.move_backward()
            print "moving backward"
        else:
            manage_altitude(drone)

def main():
    cap = cv2.VideoCapture('tcp://192.168.1.1:5555')
    
    drone = libardrone.ARDrone()
    drone.takeoff()
    pygame.time.delay(2000)
    drone.hover()
    pygame.time.delay(2000)
    
    running = True
    fcount = 0
    tick = 0
    
    ((x, y), radius) = ((0,0), 10)
    
    center = None
    
    while(running):
        fcount += 1
        if fcount > TIMEOUT_FRAMES:
            drone.land()
            print "Reached", TIMEOUT_FRAMES, "frames, now landing!"
            break
    
        tick += 1
        ret, image = cap.read()
        width = min(WIDTH, image.shape[1])
        height = (image.shape[0] * width) / image.shape[1]
        image = imutils.resize(image, width=width)
    
        # Only send commands every 5 frames
        if tick >= 5:
            tick -= 5
        if tick != 0:
            cv2.circle(image, (int(x), int(y)), int(radius),
                    (0, 255, 255), 2)
            cv2.circle(image, center, 5, (0, 0, 255), -1)
            cv2.imshow('frame', image)
            continue
    
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        
        mask = cv2.inRange(hsv, colorLower, colorUpper)
        mask = cv2.erode(mask, None, iterations=2)
        mask = cv2.dilate(mask, None, iterations=2)
        cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,
                        cv2.CHAIN_APPROX_SIMPLE)[-2]
        if len(cnts) > 0:
            # find the largest contour in the mask, then use
            # it to compute the minimum enclosing circle and
            # centroid
            c = max(cnts, key=cv2.contourArea)
            ((x, y), radius) = cv2.minEnclosingCircle(c)
            M = cv2.moments(c)
            center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
            if radius > 15:
                # draw the circle and centroid on the frame,
                # then update the list of tracked points
                cv2.circle(image, (int(x), int(y)), int(radius),
                    (0, 255, 255), 2)
                cv2.circle(image, center, 5, (0, 0, 255), -1)
                handle_movement(drone, x, radius)
    
            else:
                manage_altitude(drone)
        else:
            manage_altitude(drone)
    
        cv2.imshow('frame', image)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            out = cv2.imwrite('capture.jpg', frame)
            break
    
    cap.release()
    cv2.destroyAllWindows()
    drone.halt()

if __name__ == '__main__':
    main()
