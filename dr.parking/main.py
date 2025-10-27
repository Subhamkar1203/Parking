import cv2
import pickle
import cvzone
import numpy as np
import time

width, height = 105, 40  # Width and height of a single parking space

# Load video feed
cap = cv2.VideoCapture('carPark.mp4')

# Load parking positions
with open('CarParkPos', 'rb') as f:
    posList = pickle.load(f)

def checkParkingSpace(img, imgPro):
    free_count = 0
    occupied_count = 0

    for i, pos in enumerate(posList):
        x, y = pos
        imgCrop = imgPro[y:y + height, x:x + width]
        count = cv2.countNonZero(imgCrop)

        if count < 900:
            color = (0, 255, 0)  # Green for free
            free_count += 1
        else:
            color = (255, 0, 0)  # Red for occupied
            occupied_count += 1

        cv2.rectangle(img, pos, (pos[0] + width, pos[1] + height), color, 2)
        cvzone.putTextRect(img, f"Spot {i+1}", (x + 15, y + 30),
                           scale=0.8, thickness=1, colorT=(255, 255, 255), colorR=color)

    # Display counts in boxes at the top
    total_spots = len(posList)
    cvzone.putTextRect(img, f"FREE: {free_count}", (40, 40),
                       scale=1.8, thickness=2, offset=10, colorR=(0, 255, 0), colorT=(0, 0, 0))
    cvzone.putTextRect(img, f"OCCUPIED: {occupied_count}", (300, 40),
                       scale=1.8, thickness=2, offset=10, colorR=(0, 0, 255), colorT=(255, 255, 255))
    cvzone.putTextRect(img, f"TOTAL: {total_spots}", (620, 40),
                       scale=1.8, thickness=2, offset=10, colorR=(200, 200, 200), colorT=(0, 0, 0))

while True:
    if cap.get(cv2.CAP_PROP_POS_FRAMES) == cap.get(cv2.CAP_PROP_FRAME_COUNT):
        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)

    success, img = cap.read()
    if not success:
        break

    # Image preprocessing
    imgGray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    imgBlur = cv2.GaussianBlur(imgGray, (3, 3), 1)
    imgThreshold = cv2.adaptiveThreshold(
        imgBlur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY_INV, 25, 16)
    imgMedian = cv2.medianBlur(imgThreshold, 5)
    kernel = np.ones((3, 3), np.uint8)
    imgDilate = cv2.dilate(imgMedian, kernel, iterations=1)

    # Check spaces and display
    checkParkingSpace(img, imgDilate)

    # Show window
    cv2.imshow("Smart Parking Monitor", img)

    if cv2.waitKey(15) & 0xFF == ord('q'):
        break

    time.sleep(0.02)

cap.release()
cv2.destroyAllWindows()
