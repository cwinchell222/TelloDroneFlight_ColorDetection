from djitellopy import Tello
import cv2
import numpy as np
import time
import asyncio
from threading import Thread

width, height = 360, 240

# lower_range = np.array([30, 150, 100])  # green on HSV when dark
# upper_range = np.array([45, 255, 255])

lower_range = np.array([30, 200, 100])  # green on HSV when bright
upper_range = np.array([45, 255, 255])

# lower_range = np.array([30, 150, 50])  # green on HSV
# upper_range = np.array([50, 255, 255])


def main():
    landed = False
    count = 0
    no_obj_count = 0
    tello = Tello()
    tello.connect()
    print(tello.get_battery())
    tello.streamon()
    time.sleep(2)
    tello.takeoff()
    while True:
        img = get_frame(tello, width, height)

        img, center_x_y, area = find_color(img)

        cv2.imshow('image', img)
        cv2.waitKey(1000)
        cv2.waitKey(1)
        cv2.destroyAllWindows()
        cv2.waitKey(1)

        hor_error = (center_x_y[0] - (width // 2))
        vert_error = (center_x_y[1] - (height // 2))

        print(f'horizontal error is {hor_error}. and vertical error is {vert_error}')
        if count == 0:
            locate_thread = Thread(target=locate, daemon=True, kwargs={"tello": tello})
            locate_thread.start()
            locate_thread.join()
        if center_x_y[0] == 0:
            no_obj_count += 1
            print(f'no object detected {no_obj_count} times')
        if no_obj_count > 12:
            count = 0
            no_obj_count = 0
        if center_x_y[0] != 0:
            count += 1
            no_obj_count = 0
            print(f"center x is {center_x_y[0]}. center y is {center_x_y[1]}. and the area is {area}")
            if hor_error < -30:
                print('error is less than -30')
                left_thread = Thread(target=left_turn, daemon=True, kwargs={"tello": tello})
                left_thread.start()
                left_thread.join()
            elif hor_error > 30:
                print('horizontal error is greater than 30')
                right_thread = Thread(target=right_turn, daemon=True, kwargs={"tello": tello})
                right_thread.start()
                right_thread.join()
            elif vert_error > 30:
                down_thread = Thread(target=down, daemon=True, kwargs={"tello": tello})
                down_thread.start()
                down_thread.join()
            elif vert_error < -30:
                up_thread = Thread(target=up, daemon=True, kwargs={"tello": tello})
                up_thread.start()
                up_thread.join()
            elif area > 250 and area < 3800:
                print(f'area is greater than 250, and less than 3800: {area}')
                forward_thread = Thread(target=forward, daemon=True, kwargs={"tello": tello})
                forward_thread.start()
                forward_thread.join()
            elif area > 3800:
                print('tello move forward and then land')
                forward_land_thread = Thread(target=forward_land, daemon=True, kwargs={"tello": tello})
                forward_land_thread.start()
                forward_land_thread.join()
        if cv2.waitKey(1) & 0xFF == ord('q'):
            tello.land()
            break


def get_frame(tello, w, h):
    my_frame = tello.get_frame_read()
    my_frame = my_frame.frame
    img = cv2.resize(my_frame, (w, h))
    return img


def find_color(img):
    img_hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(img_hsv, lower_range, upper_range)  # makes mask for color green
    cv2.imshow('mask', mask)
    contours, hierarchy = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if len(contours) != 0:
        for contour in contours:
            contour_area = cv2.contourArea(contour)
            if contour_area > 250:  # if object larger than 500 pixels
                x, y, w, h = cv2.boundingRect(contour)
                cv2.rectangle(img, (x, y), (x + w, y + h), (0, 0, 255, 3))
                center_x = x + w // 2
                center_y = y + h // 2
                return img, [center_x, center_y], contour_area
            else:
                return img, [0, 0], 0
    else:
        return img, [0, 0], 0


def left_turn(tello):
    async def main():
        tello.rotate_counter_clockwise(5)
        print('turned left 5 degrees')

    asyncio.run(main())


def right_turn(tello):
    async def main():
        tello.rotate_clockwise(5)
        print('turned right 5 degrees')

    asyncio.run(main())


def forward(tello):
    async def main():
        tello.move_forward(20)
        print('went forward 30cm')

    asyncio.run(main())


def up(tello):
    async def main():
        tello.move_up(20)
        print('went up 30cm')

    asyncio.run(main())


def down(tello):
    async def main():
        tello.move_down(20)
        print('went down 20cm')

    asyncio.run(main())


def forward_land(tello):
    async def main():
        tello.move_forward(110)
        tello.land()
        print('went forward 110cm and landed')

    asyncio.run(main())


def locate(tello):
    async def main():
        tello.rotate_clockwise(10)
        print('turned right 10 degrees')

    asyncio.run(main())


if __name__ == '__main__':
    main()