import cv2
# Get exposure time range
cap = cv2.VideoCapture(0)
import subprocess
subprocess.check_call("v4l2-ctl -d /dev/video0 -c exposure_absolute=40",shell=True)
print(cap.get(cv2.CAP_PROP_EXPOSURE))
cap.release()