# Importing the Tello Drone Library
from djitellopy import Tello
# Importing OpenCV library
import cv2
import numpy as np
# Importing time package
import time
# Importing OS module
import asyncio
from threading import Thread


# Possible solutions could be a global boolean VAR for detected cyl then flight goes to it
# Maybe put camera in the background thread and flight in the main function


#w, h = 360, 480
w, h = 1280, 720


def telloGetFrame(theDrone, w=360, h=240):
    myFrame = theDrone.get_frame_read()
    myFrame = myFrame.frame
    img = cv2.resize(myFrame, (w, h))
    return img


def flight_controller(drone:Tello):
    async def main(): #this is a function declared inside of another function
        try:
            await drone.takeoff()
            await drone.move_forward(10)
            await drone.turn_clockwise(360)
            await drone.move_left(20)
            await drone.land()
        finally:
            await drone.stop_video()
            await drone.disconnect()

    asyncio.run(main())

def run_robot(drone):
    count = 0
    while True:
        # Step 1
        img = telloGetFrame(drone, w, h)

        hsv_frame = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        cx = int(w / 2)
        cy = int(h / 2)

        pixel_center = hsv_frame[cy, cx]
        hue_value = pixel_center[0]

        color = "undefined"
        if hue_value < 5:
            color = "RED"
        elif hue_value < 22:
            color = "ORANGE"
        elif hue_value < 33:
            color = "YELLOW"
        elif hue_value < 78:
            color = "GREEN"
        elif hue_value < 131:
            color = "BLUE"
        elif hue_value < 170:
            color = "VIOLET"
        else:
            color = "RED"

        pixel_center_bgr = img[cy, cx]
        b, g, r = int(pixel_center_bgr[0]), int(pixel_center_bgr[1]), int(pixel_center_bgr[2])

        cv2.putText(img, color, (10, 70), 0, 1.5, (b, g, r), 2)
        cv2.circle(img, (cx, cy), 5, (25, 25, 25), 3)

        # 40 for hsv = green cyl
        # 30-40rg, 208/209, 147-150 for bgr

        cv2.imshow('Image', img)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            drone.streamoff()
            drone.land()
            break


def main():
    # Instantiating the Tello module
    drone = Tello()
    # Connecting the drone to the python script after connecting to the Drone's WiFi
    drone.connect()
    drone.streamon()
    time.sleep(2)
    fly_thread = Thread(target=flight_controller, daemon=True, kwargs={"drone":drone})
    fly_thread.start()
    run_robot(drone)
    cv2.destroyAllWindows()


if __name__ == '__main__':
    main()