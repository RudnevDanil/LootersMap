# calling this script 
# python3 save_faces.py byf 0
# where 
#	'...' faces will be here
#	'...' strart index for faces

import cv2, os
import numpy as np
import sys # for taking argument of console
from mtcnn import MTCNN
import insightface

model = insightface.app.FaceAnalysis()
model.prepare(ctx_id = -1, nms=0.4)

pathForFaces = "faces/" + sys.argv[1] + "/"

print(" Try to take video...")
video_capture = cv2.VideoCapture('rtsp://admin:admin@192.168.144.200:554/snl/live/1/1')
success, frame = video_capture.read()
if success: 
	print(" Stream founded successfully.")
else: 
	print(" Stream NOT founded.")

# Initialize some variables
detector = MTCNN()
color = (0,155,255)
iterations_counter = 0
face_counter = 0 + int(sys.argv[2])

print(" While cycle strated...")
while True:
	ret, frame = video_capture.read()
	
	if iterations_counter == 10:				
		image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
		result = detector.detect_faces(image)
		if len(result) > 0 :
			bounding_box = result[0]['box']
			keypoints = result[0]['keypoints']
			left = bounding_box[0]
			top = bounding_box[1]
			right = bounding_box[0]+bounding_box[2]
			bottom = bounding_box[1] + bounding_box[3]
			
			border_h = (int)((bottom - top)*0.40)
			border_w = (int)((right - left)*0.40)
			if (top - border_h >=0) and (bottom + border_h < 960) and (left - border_w >= 0) and (right + border_w < 1280):
				faces = model.get(frame[top-border_h:bottom+border_h,left-border_w:right+border_w])
				if len(faces):	
					cv2.imwrite(pathForFaces + "%d.jpg"  % face_counter, frame[top-border_h:bottom+border_h,left-border_w:right+border_w])			
					face_counter += 1
					cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
					cv2.circle(frame,(keypoints['left_eye']), 2, color, 2)
					cv2.circle(frame,(keypoints['right_eye']), 2, color, 2)
					cv2.circle(frame,(keypoints['nose']), 2, color, 2)
					cv2.circle(frame,(keypoints['mouth_left']), 2, color, 2)
					cv2.circle(frame,(keypoints['mouth_right']), 2, color, 2)	

		iterations_counter = 0
		cv2.imshow('Video', frame)
	else:
		iterations_counter += 1

	if cv2.waitKey(1) & 0xFF == ord('q'):
		break

video_capture.release()
cv2.destroyAllWindows()
