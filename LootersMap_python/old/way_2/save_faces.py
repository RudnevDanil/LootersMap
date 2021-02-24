# calling this script 
# python3 save_faces.py byf 0
# where 
#	'...' faces will be here
#	'...' strart index for faces

import face_recognition
import cv2, os
import numpy as np
import sys # for taking argument of console
from PIL import Image

pathForFaces = "faces/" + sys.argv[1] + "/"

print(" Try to take video...")
video_capture = cv2.VideoCapture('rtsp://admin:admin@192.168.144.200:554/snl/live/1/1')
success, frame = video_capture.read()
if success: 
	print(" Stream founded successfully.")
else: 
	print(" Stream NOT founded.")

# Initialize some variables
face_locations = []
face_encodings = []
process_this_frame = True
color = (0,155,255)
face_locations = []

iterations_counter = 0
face_counter = 0 + int(sys.argv[2])
print(" While cycle strated...")
while True:
	ret, frame = video_capture.read()
	
	if iterations_counter == 5:
		small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
		rgb_small_frame = small_frame[:, :, ::-1]
		
		face_locations = face_recognition.face_locations(rgb_small_frame, number_of_times_to_upsample=3, model="hog")
		face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

		for (top, right, bottom, left) in face_locations:
			print("FACE FOUNDED >>> top: ",top, "bottom: ",bottom, "left: ",left,"right: ",right)
			if (top*4 - 30 >=0) and (bottom*4 + 30 < 960) and (left*4 - 30 >= 0) and (right*4 + 30 < 1280):
				cv2.imwrite(pathForFaces + "%d.jpg"  % face_counter, frame[ top*4 - 30: bottom*4 + 30, left*4 - 30: right*4 + 30])
				face_counter += 1
		
		border = 30
		for (top, right, bottom, left) in face_locations:
			top *= 4
			right *= 4
			bottom *= 4
			left *= 4

			cv2.rectangle(frame, (left-border, top-border), (right+border, bottom+border), color, 2)
			cv2.rectangle(frame, (left-border, bottom - 35 + border), (right+border, bottom+border), color, cv2.FILLED)
			
		iterations_counter = 0
	else:
		iterations_counter += 1

	
	cv2.imshow('Video', frame)

	if cv2.waitKey(1) & 0xFF == ord('q'):
		break

video_capture.release()
cv2.destroyAllWindows()
