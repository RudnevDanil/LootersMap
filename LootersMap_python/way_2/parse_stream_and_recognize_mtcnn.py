import face_recognition
import cv2, os
import numpy as np
from PIL import Image
from mtcnn import MTCNN
import insightface
from scipy import spatial

detector = MTCNN()
model = insightface.app.FaceAnalysis()
model.prepare(ctx_id = -1, nms=0.4)

path_for_data_encod = './data_mtcnn_encod.npy'
path_for_data_names = './data_mtcnn_names.npy'
names = ['1_Omelchenko','2_Victoria','3_Rudnev','4_Oleg','5_Irina','6_Alexandr','7_Lena','8_Somebody','9_Roiby','10_Priimakov', '11_OlegDmitr','12_Vital','13_Ponkratov','14_Edik','15_Vova','16_Stud','17_Sveta','18_&&&','19_Max','20_Petrovich']
font = cv2.FONT_HERSHEY_DUPLEX

print(" Load a trained data...")
known_face_encodings = np.load(path_for_data_encod)
known_face_names = np.load(path_for_data_names)
print(" Using dataset on %d images" % len(known_face_encodings))

'''
# cosine similarity example
a = known_face_encodings[0]
b = known_face_encodings[1]
c = known_face_encodings[2]
d = known_face_encodings[3]
e = known_face_encodings[4]

an = known_face_names[0]
bn = known_face_names[1]
cn = known_face_names[2]
dn = known_face_names[3]
en = known_face_names[4] 

print(an,"   ", bn,"   ",spatial.distance.cosine(a, b))
print(bn,"   ", an,"   ",spatial.distance.cosine(b, a))
print(bn,"   ", cn,"   ",spatial.distance.cosine(b, c))
print(dn,"   ", en,"   ",spatial.distance.cosine(d, e))
print(en,"   ", an,"   ",spatial.distance.cosine(e, a))
print(an,"   ", an,"   ",spatial.distance.cosine(a, a))

exit(0)
#
'''

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
		image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
		result = detector.detect_faces(image)
		#print(result)
		if len(result) > 0 :
			bounding_box = result[0]['box']
			keypoints = result[0]['keypoints']
			left = bounding_box[0]
			top = bounding_box[1]
			right = bounding_box[0]+bounding_box[2]
			bottom = bounding_box[1] + bounding_box[3]
			
			color = (0,155,255)
			cv2.rectangle(frame, (left, top), (right, bottom), color, 2)

			cv2.circle(frame,(keypoints['left_eye']), 2, color, 2)
			cv2.circle(frame,(keypoints['right_eye']), 2, color, 2)
			cv2.circle(frame,(keypoints['nose']), 2, color, 2)
			cv2.circle(frame,(keypoints['mouth_left']), 2, color, 2)
			cv2.circle(frame,(keypoints['mouth_right']), 2, color, 2)
			
			border_h = (int)((bottom - top)*0.40)
			border_w = (int)((right - left)*0.40)
			if (top - border_h >=0) and (bottom + border_h < 960) and (left - border_w >= 0) and (right + border_w < 1280):			
				faces = model.get(frame[top-border_h:bottom+border_h,left-border_w:right+border_w])
				if len(faces):
					face = faces[0]
					
					# recognition 
					min_ind, min_val = -1 , 1.1
					tolerance = 0.6
					for i in range(0,len(known_face_encodings)):
						byf = spatial.distance.cosine(face.normed_embedding, known_face_encodings[i])
						if byf < min_val:
							min_val = byf
							min_ind = i
					name = "Unknown"
					color = color_red
					if (min_ind != -1) and (min_val < tolerance):
						name = known_face_names[min_ind]
						color = color_green
					
					#print("\tage:%d"%(face.age))
					gender = 'Male'
					if face.gender==0:
						gender = 'Female'
					print("\tgender:%s"%(gender))
					print("\tembedding shape:%s"%face.embedding.shape)
					print("\tbbox:%s"%(face.bbox.astype(np.int).flatten())) # coordinates of face
					print("\tlandmark:%s"%(face.landmark.astype(np.int).flatten())) # coordinates of 5 points (eyes and nose)
					print("")
					cv2.putText(frame, name, (left, bottom + 40), font, 1.5, color, 2)
					cv2.putText(frame, "Gender %s" % (gender), (left, bottom + 80), font, 1.5, color, 2)
					#cv2.putText(frame, "Years %d" % (face.age), (left, bottom + 120), font, 1.5, color, 2)
					
		cv2.imshow('Video', frame)

		iterations_counter = 0
	else:
		iterations_counter += 1

	if cv2.waitKey(1) & 0xFF == ord('q'):
		break

# Release handle to the webcam
video_capture.release()
cv2.destroyAllWindows()
