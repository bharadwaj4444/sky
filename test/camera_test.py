import cv2

cap = cv2.VideoCapture(
    "/dev/videoX",
    cv2.CAP_V4L2,
)

cap.set(
    cv2.CAP_PROP_FOURCC,
    cv2.VideoWriter_fourcc(*"MJPG"),
)

cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
cap.set(cv2.CAP_PROP_FPS, 30)

print("opened:", cap.isOpened())

for i in range(10):
    ret, frame = cap.read()

    print(
        i,
        ret,
        None if frame is None else frame.shape,
    )

cap.release()