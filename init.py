import cv2
import numpy as np
import matplotlib.pyplot as plt
import os
#== Parameters =======================================================================
BLUR = 9
CANNY_THRESH_1 = 10
CANNY_THRESH_2 = 200
MASK_DILATE_ITER = 10
MASK_ERODE_ITER = 10
MASK_COLOR = (0.0,0.0,0.0) # In BGR format


def webcam():
    cam = cv2.VideoCapture(0)
    cv2.namedWindow("UPR")
    img_counter = 0
    
    while True:
        ret, frame = cam.read()
        cv2.imshow("UPR", frame)
        if not ret:
            break
        k = cv2.waitKey(1)
        
        if k % 256 == 27:
            # ESC pressed
            print("Close")
            break
        elif k % 256 == 32:
                    # SPACE pressed
            img_name = "UPR_{}.png".format(img_counter)
            cv2.imwrite(img_name, frame)
                
            print("{} written!".format(img_name))
            img_counter += 1

    cam.release()

    cv2.destroyAllWindows()

def function():
    webcam()
    filename = '/Users/bonha/realtimefirebase_easypath/UPR_0.png'

    print(filename)
    img = cv2.imread(filename) #only png file!!
    gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    #-- Edge detection -------------------------------------------------------------------
    edges = cv2.Canny(gray, CANNY_THRESH_1, CANNY_THRESH_2)
    edges = cv2.dilate(edges, None)
    edges = cv2.erode(edges, None)

    #-- Find contours in edges, sort by area ---------------------------------------------
    contour_info = []
    #_, contours, _ = cv2.findContours(edges, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)
    # Previously, for a previous version of cv2, this line was:
    contours, _ = cv2.findContours(edges, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)
    # Thanks to notes from commenters, I've updated the code but left this note
    for c in contours:
        contour_info.append((
                             c,
                             cv2.isContourConvex(c),
                             cv2.contourArea(c),
                             ))
    contour_info = sorted(contour_info, key=lambda c: c[2], reverse=True)
    max_contour = contour_info[0]

    #-- Create empty mask, draw filled polygon on it corresponding to largest contour ----
    # Mask is black, polygon is white
    mask = np.zeros(edges.shape)
    cv2.fillConvexPoly(mask, max_contour[0], (255))

    #-- Smooth mask, then blur it --------------------------------------------------------
    mask = cv2.dilate(mask, None, iterations=MASK_DILATE_ITER)
    mask = cv2.erode(mask, None, iterations=MASK_ERODE_ITER)
    mask = cv2.GaussianBlur(mask, (BLUR, BLUR), 0)
    mask_stack = np.dstack([mask]*3)    # Create 3-channel alpha mask

    #-- Blend masked img into MASK_COLOR background --------------------------------------
    mask_stack  = mask_stack.astype('float32') / 255.0          # Use float matrices,
    img         = img.astype('float32') / 255.0                 #  for easy blending

    masked = (mask_stack * img) + ((1-mask_stack) * MASK_COLOR) # Blend
    masked = (masked * 255).astype('uint8')                     # Convert back to 8-bit


#    cv2.imshow('img', masked)                                   # Display
#    #cv2.waitKey()
    cv2.imwrite('/Users/bonha/realtimefirebase_easypath/image/0.png', masked)

