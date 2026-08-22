import cv2

print(
    "\n".join(
        line
        for line in cv2.getBuildInformation().splitlines()
        if "GStreamer" in line
    )
)

pipeline = (
    "v4l2src device=/dev/video0 ! "
    "image/jpeg,width=1920,height=1080,framerate=30/1 ! "
    "jpegdec ! "
    "videoconvert ! "
    "video/x-raw,format=BGR ! "
    "appsink drop=true max-buffers=1 sync=false"
)

cap = cv2.VideoCapture(
    pipeline,
    cv2.CAP_GSTREAMER,
)

print("opened:", cap.isOpened())

for i in range(10):
    ret, frame = cap.read()

    print(
        i,
        ret,
        None if frame is None else frame.shape,
    )

cap.release()