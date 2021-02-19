import face_recognition
import cv2, os
import numpy as np
from PIL import Image

path_for_data_encod = './data_encod_150.npy'
path_for_data_names = './data_names_150.npy'
names = ['1_Omelchenko','2_Victoria','3_Rudnev','4_Oleg','5_Irina','6_Alexandr','7_Lena','8_Somebody','9_Roiby','10_Priimakov', '11_OlegDmitr','12_Vital','13_Ponkratov','14_Edik','15_Vova','16_Stud','17_Sveta','18_&&&','19_Max','20_Petrovich']

print(" Load a trained data...")
known_face_encodings = np.load(path_for_data_encod)
known_face_names = np.load(path_for_data_names)
print(" Using dataset on %d images" % len(known_face_encodings))

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
face_names = []
process_this_frame = True
color_green = (0,255,0)
color_red = (0,0,255)
face_locations = []
face_names = []

iterations_counter = 0
print(" While cycle strated...")
while True:
	# Grab a single frame of video
	ret, frame = video_capture.read()
	
	if iterations_counter == 10:
		# Resize frame of video to 1/4 size for faster face recognition processing
		small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)

		# Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
		rgb_small_frame = small_frame[:, :, ::-1]

		# Only process every other frame of video to save time
		if process_this_frame:
			# Find all the faces and face encodings in the current frame of video
			'''
			*** DESCRIPTION *** face_locations
			    img – An image (as a numpy array)
			    number_of_times_to_upsample – How many times to upsample the image looking for faces. 
				Higher numbers find smaller faces.
			    model – Which face detection model to use. 
				“hog” is less accurate but faster on CPUs.
				“cnn” is a more accurate deep-learning model which is GPU/CUDA accelerated (if available). The default is “hog”.
			'''
			
			# when using gpu try to use face_recognition.batch_face_locations
			face_locations = face_recognition.face_locations(rgb_small_frame, number_of_times_to_upsample=3, model="hog")
			face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

			#face_names = []
			for face_encoding in face_encodings:
				# less tolerance will be more strict. Value 0.6 is default.
				matches = face_recognition.compare_faces(known_face_encodings, face_encoding, tolerance=0.6)
				name = "Unknown"
				color = color_red

				# ... If a match was found in known_face_encodings, just use the first one.
				# if True in matches:
				#     first_match_index = matches.index(True)
				#     name = known_face_names[first_match_index]

				# ... Or instead, use the known face with the smallest distance to the new face
				face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
				best_match_index = np.argmin(face_distances)
				if matches[best_match_index]:
					name = known_face_names[best_match_index]
					color = color_green

				face_names.append(name)

		process_this_frame = not process_this_frame

		iterations_counter = 0
	else:
		iterations_counter += 1

	# Display the results
	border = 30
	for (top, right, bottom, left), name in zip(face_locations, face_names):
		# Scale back up face locations since the frame we detected in was scaled to 1/4 size
		top *= 4
		right *= 4
		bottom *= 4
		left *= 4

		# Draw a box around the face
		cv2.rectangle(frame, (left-border, top-border), (right+border, bottom+border), color, 2)

		# Draw a label with a name below the face
		cv2.rectangle(frame, (left-border, bottom - 35 + border), (right+border, bottom+border), color, cv2.FILLED)
		font = cv2.FONT_HERSHEY_DUPLEX
		cv2.putText(frame, name, (left + 6 -border, bottom - 6 + border), font, 1.0, (0, 0, 0), 1)

	
	# Display the resulting image
	cv2.imshow('Video', frame)

	# Hit 'q' on the keyboard to quit!
	if cv2.waitKey(1) & 0xFF == ord('q'):
		break

# Release handle to the webcam
video_capture.release()
cv2.destroyAllWindows()
