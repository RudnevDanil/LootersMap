import os, time, requests, insightface
import numpy as np
from PIL import Image
from mtcnn import MTCNN
from scipy.spatial.distance import cosine

detector = MTCNN()
model = insightface.app.FaceAnalysis()
model.prepare(ctx_id = -1, nms=0.4)

encod_path = './data_encod.npy'
ids__path = './data_ids.npy'

print(" Load a trained data...")
known_face_encodings = np.load(encod_path)
known_face_ids = np.load(ids__path)
print(" Using dataset on %d images" % len(known_face_encodings))

imgs_dir = '../LootersMap_cpp/LootersMap_cpp_linux/build/saved_imgs/'
faces_dir = './faces/'
delete_img_after_classificcation = True
general_face_counter = 0
while(True):
	files = os.listdir(imgs_dir)
	for filename in files:
		timer_start = time.time()
		print(" --- working with file named " + filename + " ...")
		boxes = []	

		frame = np.array(Image.open(imgs_dir + filename),'uint8')
		image = frame

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
						byf = cosine(face.normed_embedding, known_face_encodings[i])
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
			img = Image.fromarray(np.uint8(frame[boxes[i][1]:boxes[i][3],boxes[i][0]:boxes[i][2]])).convert('RGB')
			img.save(faces_dir + "f" + str(general_face_counter) + "_" + str(boxes[i][4]) + ".png", "PNG")
			general_face_counter += 1
			
		# delete this file
		if delete_img_after_classificcation:
			os.remove(imgs_dir + filename)
	
		timer_end = time.time()
		print("elapsed time is " + str(timer_end - timer_start) + "\n")