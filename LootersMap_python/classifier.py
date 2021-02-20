import face_recognition
import cv2, os
import numpy as np
from PIL import Image
from mtcnn import MTCNN
import insightface
from scipy import spatial
import xml.etree.ElementTree as xml
import time
import requests 

detector = MTCNN()
model = insightface.app.FaceAnalysis()
model.prepare(ctx_id = -1, nms=0.4)

encod_path = './data_encod.npy'
ids__path = './data_ids.npy'
request_url = "http://localhost:8000/php/test.php"
font = cv2.FONT_HERSHEY_DUPLEX

print(" Load a trained data...")
known_face_encodings = np.load(encod_path)
known_face_ids = np.load(ids__path)
print(" Using dataset on %d images" % len(known_face_encodings))

imgs_dir = '../LootersMap_cpp/LootersMap_cpp_linux/build/saved_imgs/'
delete_img_after_classificcation = True

while(True):
	files = os.listdir(imgs_dir)
	for filename in files:
		timer_start = time.time()
		print("\n --- working with file named " + filename + " ...")
		boxes = []	

		frame = cv2.imread(imgs_dir + filename)
		image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

		result = detector.detect_faces(image)	
		for cur_result in result:
			box_i = len(boxes)
			bounding_box = cur_result['box']
			left = bounding_box[0]
			top = bounding_box[1]
			right = bounding_box[0]+bounding_box[2]
			bottom = bounding_box[1] + bounding_box[3]

			color = (0,155,255)
			
			border_h = (int)((bottom - top)*0.40)
			border_w = (int)((right - left)*0.40)
			if (top - border_h >=0) and (bottom + border_h < 960) and (left - border_w >= 0) and (right + border_w < 1280):			
				faces = model.get(frame[top-border_h:bottom+border_h,left-border_w:right+border_w])
				print(" --- founded " + str(len(faces)) + " faces")
				for face in faces:	
									
					min_ind, min_val = -1 , 1.1
					tolerance = 0.6
					for i in range(0,len(known_face_encodings)):
						byf = spatial.distance.cosine(face.normed_embedding, known_face_encodings[i])
						if byf < min_val:
							min_val = byf
							min_ind = i
					
					answer = known_face_ids[min_ind] if (min_ind != -1) and (min_val < tolerance) else -1

					boxes.append([])
					boxes[box_i].append(left-border_w)
					boxes[box_i].append(top-border_h)
					boxes[box_i].append(right+border_w)
					boxes[box_i].append(bottom+border_h)
					boxes[box_i].append(answer)

		for i in range(len(boxes)):
			print(boxes[i][4])
			#cv2.imshow("frame", frame[boxes[i][1]:boxes[i][3],boxes[i][0]:boxes[i][2]]) # debug
			#cv2.waitKey(0) # debug
			print(frame[boxes[i][1]:boxes[i][3],boxes[i][0]:boxes[i][2]])
			request = requests.post(request_url, {'answerId': boxes[i][4], 'img': frame[boxes[i][1]:boxes[i][3],boxes[i][0]:boxes[i][2]]})
			if request.status_code != 200:
				print("Error posting. Request status code is ", request.status_code)
			else:
				print(request.content) # debug

		# delete this file
		if delete_img_after_classificcation:
			os.remove(imgs_dir + filename)
	
		timer_end = time.time()
		print("elapsed time is " + str(timer_end - timer_start))