import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

import time, requests, insightface
import numpy as np
from PIL import Image, ImageDraw
from scipy.spatial.distance import cosine
from mtcnn import MTCNN
import cv2

detector = MTCNN()
model = insightface.app.FaceAnalysis()
model.prepare(ctx_id = -1, nms=0.4)

encod_path = './data_encod.npy'
ids__path = './data_ids.npy'

print(" Load a trained data...")
known_face_encodings = np.load(encod_path)
known_face_ids = np.load(ids__path)
print(" Using dataset on %d images" % len(known_face_encodings))

names = ['','','','','','','6-Walter','7-Hank','8-Jessey','9-DEA_Agent','10-Skyler','11-Junior','12-Narco_1','13-Mary','14-Car_Washer','15-Narco_2','16-Doctor']
check_file = "./isClassify"
imgs_dir = './demo/'
faces_dir = './demo_result/'
delete_img_after_classificcation = True
general_face_counter = 0
#print_bool = True

files = os.listdir(imgs_dir)
if len(files) == 0:
	#print("waiting imgs" + (" / " if print_bool else " \ "), end='\r')
	print(" . ", end='', flush=True)			
	#print_bool = not print_bool
	time.sleep(0.5)
	
for filename in files:
	timer_start = time.time()
	boxes = []
		
	byfImg = Image.open(imgs_dir + filename)
	cvImg = cv2.imread(imgs_dir + filename)
	
	frame = np.array(byfImg,'uint8')
	image = frame
	
	
	
	#print(" --- img size is ", frame.shape)

	result = detector.detect_faces(image)
	print(" --- mtcnn found " , len(result), " boxes ...")
	for cur_result in result:
		box_i = len(boxes)
		bounding_box = cur_result['box']
		left = bounding_box[0]
		top = bounding_box[1]
		right = bounding_box[0]+bounding_box[2]
		bottom = bounding_box[1] + bounding_box[3]
		
		cv2.rectangle(cvImg,(left,top),(right,bottom),(255,0,0),2)
		print(" --- --- box l=", left, "t=", top, "r=", right, "b=", bottom)
		
		border_h = (int)((bottom - top)*0.40) # 0.4 because mtcnn gives box cutted on top eyebrow and mounth.
		border_w = (int)((right - left)*0.40) # That border will be added to box.
		if (top - border_h >= 0) and (bottom + border_h < frame.shape[0]) and (left - border_w >= 0) and (right + border_w < frame.shape[1]):			
			faces = model.get(frame[top-border_h:bottom+border_h,left-border_w:right+border_w])
			
			#print(" --- founded " + str(len(faces)) + " faces")
			for face in faces:				
							
				min_ind, min_val = -1 , 1.1
				tolerance = 0.6
				for i in range(0,len(known_face_encodings)):
					byf = cosine(face.normed_embedding, known_face_encodings[i])
					if byf < min_val:
						min_val = byf
						min_ind = i
				
				answer = known_face_ids[min_ind] if (min_ind != -1) and (min_val < tolerance) else -1
				cv2.rectangle(cvImg,(left-border_w,top-border_h),(right+border_w,bottom+border_h),(0,0,255) if answer == -1 else (0,255,0),2)
				if(answer != -1):
					cv2.putText(cvImg, names[answer], (left-border_w,bottom+border_h + 15), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)
				boxes.append([])
				boxes[box_i].append(left-border_w)
				boxes[box_i].append(top-border_h)
				boxes[box_i].append(right+border_w)
				boxes[box_i].append(bottom+border_h)
				boxes[box_i].append(answer)
				print(boxes[box_i])
				box_i = len(boxes)
				
	timer_end = time.time()
	print(" DONE \t time is ", round(timer_end - timer_start,2), "\t founded ", len(boxes) , "faces ", "+"*len(boxes))
	
	#cv2.imshow("WindowNameHere", cvImg)
	#cv2.waitKey(0)
	cv2.imwrite(faces_dir+filename,cvImg)

