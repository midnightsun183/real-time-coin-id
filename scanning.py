import numpy as np
import serial
import threading
import time

import cv2
import cv2.cv as cv


def get_work_data():
    return 'data'


def read_from_cameras(top_camera, bottom_camera):
    ret, top = top_camera.read()
    ret, bottom = bottom_camera.read()
    if top == None:
        raise ValueError('A frame from the top camera came up None')
    if bottom == None:
        raise ValueError('A frame from the bottom camera came up None')
    return top, bottom

def deskew(src, pixel_shift):
    src_tri = np.zeros((3, 2), dtype=np.float32)
    dst_tri = np.zeros((3, 2), dtype=np.float32)

    rows = src.shape[0]
    cols = src.shape[1]


    # Set your 3 points to calculate the  Affine Transform
    src_tri[1] = [cols - 1, 0]
    src_tri[2] = [0, rows - 1]
    # dstTri is the same except the bottom is moved over shiftpixels:
    dst_tri[1] = src_tri[1]
    dst_tri[2] = [pixel_shift, rows - 1]

    # Get the Affine Transform
    warp_mat = cv2.getAffineTransform(src_tri, dst_tri)

    ## Apply the Affine Transform just found to the src image
    cv2.warpAffine(src, warp_mat, (cols, rows), src, cv2.INTER_CUBIC)
    return src


def scan(top_camera, bottom_camera, ser):
    top_captures = []
    bottom_captures = []

    for count in range(0, 62):
        # print count,
        top, bottom = read_from_cameras(top_camera, bottom_camera)

        if count > 4:
            top_captures.append(top)
            bottom_captures.append(bottom)

        led = count / 2
        if led < 29:
            # print "led", led
            ser.write(str(led) + "\n")
            cv.WaitKey(1)
    return top_captures, bottom_captures


def save(captures, coin_id):
    count = 0
    for frame in captures:
        ratio = .7
        frame_width = int(1920 * ratio)
        frame_height = int(1080 * ratio)
        # print '3 In %s seconds' % (time.time() - start_time,)
        frame = cv2.resize(frame, (frame_width, frame_height), interpolation=cv2.INTER_AREA)
        if count == 54:
            cv2.imwrite('/home/pkrush/cents-test/' + str(coin_id).zfill(5) + str(count).zfill(2) + '.png', frame)
        count += 1
        #
        # cv2.imshow('frame', frame)
        #cv.WaitKey(30)

    #     # cv2.imwrite('/home/pkrush/cents-hd/' + str(coin_count).zfill(5) + str(count).zfill(2) + '.png', frame)
    #     # bottom camera:
    #     # coin_size_adjustment_factor = 1.06
    #
    #     # top_camera:
    #     coin_size_adjustment_factor = .405
    #
    #     # frame = deskew(frame,-9)  #100 rpm
    #     # frame = deskew(frame, -30)
    #     # print '5 In %s seconds' % (time.time() - start_time,)
    #     gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    #     # circles = cv2.HoughCircles(gray, cv.CV_HOUGH_GRADIENT, 1, 300, param1=50, param2=30, minRadius=448, maxRadius=450)
    #
    #     # good for scanning:
    #     # circles = cv2.HoughCircles(gray, cv.CV_HOUGH_GRADIENT, 1, 300, param1=40, param2=20, minRadius=222, maxRadius=226)
    #     # print '6 In %s seconds' % (time.time() - start_time,)
    #
    #     # Bottom Camera
    #     circles = cv2.HoughCircles(gray, cv.CV_HOUGH_GRADIENT, 1, 300, param1=40, param2=20, minRadius=222, maxRadius=224)
    #
    #     # Top Camera:
    #     # circles = cv2.HoughCircles(gray, cv.CV_HOUGH_GRADIENT, 1, 300, param1=40, param2=20, minRadius=290, maxRadius=295)
    #
    #     # print '7 In %s seconds' % (time.time() - start_time,)
    #
    #     if circles is None:
    #         # continue
    #         pass
    #
    #     circles = np.uint16(np.around(circles))
    #
    #     print 'circles:', len(circles)
    #
    #     for i in circles[0, :]:
    #         center_x = i[0]
    #         center_y = i[1]
    #         crop_radius = i[2]
    #         # cv2.circle(frame, (center_x, center_y), 2, (0, 0, 255), 1)
    #         # cv2.circle(frame, (center_x, center_y), crop_radius, (0, 0, 255), 1)
    #         # print circles
    #         cv2.imshow('detected circles', frame)
    #
    #         # The coin is move from right to left so the center_x is going down.
    #         center_stop_x = 530
    #         center_go_x = 350
    #         print center_x, "   ", center_y, "     ", crop_radius
    #         if center_go_x < center_x < center_stop_x:
    #             print center_x
    #             if found_coin == False:
    #                 found_coin = True
    #                 print "Conveyor Stop"
    #                 # ser.write(str(103) + "\n")
    #                 cv.WaitKey(2)
    #                 continue
    #             print count
    #             led = count / 2
    #             if led < 29:
    #                 print "led", led
    #                 # ser.write(str(led) + "\n")
    #                 cv.WaitKey(2)
    #
    #             center_list.append([center_x, center_y, crop_radius])
    #
    #             sample_size = 20
    #
    #             total_center_x = 0
    #             total_center_y = 0
    #             total_radius = 0
    #
    #             for past_x, past_y, past_radius in center_list[len(center_list) - sample_size:len(center_list)]:
    #                 total_center_x += past_x
    #                 total_center_y += past_y
    #                 total_radius += past_radius
    #
    #             average_center_x = float(total_center_x) / sample_size
    #             average_center_y = float(total_center_y) / sample_size
    #             average_radius = float(total_radius) / sample_size
    #
    #             print average_center_x, center_x, "   ", average_center_y, center_y, "     ", average_radius, crop_radius
    #             print center_x, "   ", center_y, "     ", crop_radius
    #
    #             font = cv2.FONT_HERSHEY_SIMPLEX
    #             cv2.circle(frame, (int(average_center_x), int(average_center_y)), int(average_radius), (0, 255, 0), 1)
    #             # cv2.circle(frame, (center_x, center_y), crop_radius, (0, 255, 0), 1)
    #
    #             # crop = frame[center_y - 224:center_y + 224, center_x - 224:center_x + 224]
    #             # cv2.putText(crop, str(crop_radius)[0:5], (10, 90), font, .7, (0, 255, 0), 2)
    #             if len(center_list) > 20:
    #                 crop = frame[average_center_y - 224:average_center_y + 224,
    #                        average_center_x - 224:average_center_x + 224]
    #                 cv2.putText(crop, str(average_radius)[0:5], (10, 90), font, .7, (0, 255, 0), 2)
    #
    #                 cv2.imshow('crop', crop)
    #                 if count > 4 and count < 62:
    #                     image_id = count - 5
    #                     filename = '/home/pkrush/cents-test/' + str(coin_count) + str(image_id).zfill(2) + '.png'
    #                     cv2.imwrite(filename, frame)
    #                 if count == 62:
    #                     # ser.write(str(102) + "\n")
    #                     cv.WaitKey(2)
    #                 if count == 80:
    #                     # ser.write(str(100) + "\n")
    #                     # cv.WaitKey(100)
    #                     # ser.write(str(101) + "\n")
    #                     count = 0
    #                     found_coin = False
    #                     coin_count += 1
    #
    #                 if found_coin == True:
    #                     count += 1
    #
    #     # red = frame[:, :, 2]
    #     # green = frame[:, :, 1]
    #     # blue = frame[:, :, 0]
    #
    # if cv2.waitKey(1) & 0xFF == ord('q'):
    #     return
    return

def get_moving_center_x(frame, ratio, deskew_pixels, frame_name):
    frame_width = int(1920 * ratio)
    frame_height = int(1080 * ratio)
    # print '3 In %s seconds' % (time.time() - start_time,)
    frame = cv2.resize(frame, (frame_width, frame_height), interpolation=cv2.INTER_AREA)
    # print '4 In %s seconds' % (time.time() - start_time,)

    height_expansion_amount = 40
    blank_image = np.zeros((frame_height + height_expansion_amount, frame_width, 3), np.uint8)
    blank_image[height_expansion_amount / 2:frame_height + height_expansion_amount / 2, 0:frame_width] = frame
    frame = blank_image
    # frame = frame[460:,40:1040]
    deskewed = deskew(frame, deskew_pixels)
    gray = cv2.cvtColor(deskewed, cv2.COLOR_BGR2GRAY)

    # circles = cv2.HoughCircles(gray, cv.CV_HOUGH_GRADIENT, 1, 300, param1=50, param2=30, minRadius=448, maxRadius=450)
    # good for scanning:
    # circles = cv2.HoughCircles(gray, cv.CV_HOUGH_GRADIENT, 1, 300, param1=40, param2=20, minRadius=222, maxRadius=226)
    # print '6 In %s seconds' % (time.time() - start_time,)
    # Bottom Camera
    circles = cv2.HoughCircles(gray, cv.CV_HOUGH_GRADIENT, 1, 300, param1=40, param2=20, minRadius=52, maxRadius=58)
    if circles is None:
        cv2.imshow(frame_name, frame)
        return 0
    circles = np.uint16(np.around(circles))

    for i in circles[0, :]:
        center_x = i[0]
        center_y = i[1]
        crop_radius = i[2]
        cv2.circle(frame, (center_x, center_y), 2, (0, 0, 255), 1)
        cv2.circle(frame, (center_x, center_y), crop_radius, (0, 0, 255), 1)
        # print circles
        cv2.imshow(frame_name, frame)
    return center_x * (1 / ratio)


ser = serial.Serial(port='/dev/ttyUSB1', baudrate=115200)
ser.write(str(102) + "\n")
cv.WaitKey(2)
ser.write(str(104) + "\n")
cv.WaitKey(2)
cameras = []
top_camera = None
bottom_camera = None

for camera_id in range(0, 3):
    cap = cv2.VideoCapture(camera_id)
    cap.set(3, 1920)
    cap.set(4, 1080)

    if cap.get(3) == 1920:
        if top_camera is None:
            top_camera = cap
        else:
            bottom_camera = cap

            # if cap.get(3) == 1920:
            #     if bottom_camera is None:
            #         bottom_camera = cap
            #     else:
            #         top_camera = cap
frame_count = 0
last_scan_frame_count = -100
coin_count = 0
center_list = []
found_coin = False

top_status = 2
bottom_status = 2
print top_status, bottom_status
#first_top_scanned = False

# 0 is ready to scan
# 1 is move to center
# 2 is moving away from center

while (True):
    status = ''
    # Capture frame-by-frame
    cv.WaitKey(2)
    start_time = time.time()

    # Wait at least 15 frames before looking again:
    if frame_count - last_scan_frame_count < 15:
        frame_count += 1
        continue

    top, bottom = read_from_cameras(top_camera, bottom_camera)

    if top_status in (1, 2):
        center_x = get_moving_center_x(top, .1, 8, 'Top')
        if center_x != 0:
            status += 'top' + ' ' + str(center_x) + '-'
            if top_status == 2 and center_x > 1600:
                top_status = 1
                status += str(top_status) + ' ' + str(bottom_status) + '-'
            else:
                if top_status == 1 and center_x < 1600:
                    # if first_top_scanned == True:
                    top_status = 0
                    status += str(top_status) + ' ' + str(bottom_status) + '-'
                    ser.write(str(105) + "\n")
                    cv.WaitKey(2)
                    status += 'Top belt off'
                    # else:
                    # first_top_scanned = True
                    #top_status = 2

    if bottom_status in (1, 2):
        center_x = get_moving_center_x(bottom, .11, -8, 'Bottom')
        if center_x != 0:
            status += 'bottom' + ' ' + str(center_x) + '-'
            if bottom_status == 2 and center_x < 500:
                bottom_status = 1
                status += str(top_status) + ' ' + str(bottom_status) + '-'
            else:
                if bottom_status == 1 and center_x > 300:
                    bottom_status = 0
                    status += str(top_status) + ' ' + str(bottom_status) + '-'
                    ser.write(str(103) + "\n")
                    status += 'Bottom belt off'

    if top_status == 0 and bottom_status == 0:
        # if first_top_scanned == True:
        top_captures, bottom_captures = scan(top_camera, bottom_camera, ser)

        t = threading.Thread(target=save, args=(top_captures, coin_count))
        t.start()
        t = threading.Thread(target=save, args=(bottom_captures, coin_count + 1))
        t.start()
        coin_count += 2
        status += 'Cycle In %s seconds' % (time.time() - start_time,)
        start_time = time.time()
        status += 'Scanning with the LED lights.'
        cv.WaitKey(10)
        ser.write(str(102) + "\n")
        cv.WaitKey(2)
        ser.write(str(104) + "\n")
        cv.WaitKey(2)
        status += 'Both belts on'
        top_status = 2
        bottom_status = 2
        status += str(top_status) + ' ' + str(bottom_status) + '-'
    if top_status == 2 and bottom_status == 2:
        ser.write(str(102) + "\n")
        cv.WaitKey(2)
        ser.write(str(104) + "\n")
        cv.WaitKey(2)
    if status != '':
        print frame_count, status
    frame_count +=1

#ser.write(str(102) + "\n")
# cv.WaitKey(3500)
cv.WaitKey(35)
#ser.write(str(100) + "\n")
cv.WaitKey(100)
#ser.write(str(101) + "\n")

cap.release()
cv2.destroyAllWindows()
