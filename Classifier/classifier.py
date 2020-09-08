import face_recognition
import cv2, os
import numpy as np
from PIL import Image
from mtcnn import MTCNN
import insightface
from scipy import spatial
import xml.etree.ElementTree as xml
import time

color_green = (0,255,0)
color_red = (0,0,255)

detector = MTCNN()
model = insightface.app.FaceAnalysis()
model.prepare(ctx_id = -1, nms=0.4)

path_for_data_encod = './data_encod.npy'
path_for_data_names = './data_names.npy'
names = ['1_Omelchenko','2_Victoria','3_Rudnev','4_Oleg','5_Irina','6_Alexandr','7_Lena','8_Somebody','9_Roiby','10_Priimakov', '11_OlegDmitr','12_Vital','13_Ponkratov','14_Edik','15_Vova','16_Stud','17_Sveta','18_&&&','19_Max','20_Petrovich']
font = cv2.FONT_HERSHEY_DUPLEX

print(" Load a trained data...")
known_face_encodings = np.load(path_for_data_encod)
known_face_names = np.load(path_for_data_names)
print(" Using dataset on %d images" % len(known_face_encodings))

'''
imgs_dir = './imgs/'
ans_dir = './answers/'
rec_faces_dir = "./recognized_faces/"
unk_faces_dir = "./unknown_faces/"
'''
imgs_dir = '../LootersMap_cpp/LootersMap_cpp_linux/build/saved_imgs/'
ans_dir = '../LootersMap_cpp/LootersMap_cpp_linux/build/answers/'
rec_faces_dir = "../LootersMap_cpp/LootersMap_cpp_linux/build/recognized_faces/"
unk_faces_dir = "../LootersMap_cpp/LootersMap_cpp_linux/build/unknown_faces/"
save_recognized_faces = True
save_unknown_faces = True
delete_img_after_classificcation = True

# clear answer directory
files = os.listdir(ans_dir)
for filename in files:
	os.remove(ans_dir + filename)

# clear rec_faces_dir
files = os.listdir(rec_faces_dir)
for filename in files:
	os.remove(rec_faces_dir + filename)

# clear unk_faces_dir
files = os.listdir(unk_faces_dir)
for filename in files:
	os.remove(unk_faces_dir + filename)

while(True):
	#print("----------- new while iteration -----------")
	files = os.listdir(imgs_dir)
	#print(" --- Founded " + str(len(files)) + " files")
	#print(".", end = '')
	for filename in files:
		timer_start = time.time()
		print("\n --- working with file named " + filename + " ...")
		boxes = []
		
		frame = cv2.imread(imgs_dir + filename)
		frame = cv2.resize(frame, (frame.shape[0]//4, frame.shape[1]//4), interpolation = cv2.INTER_AREA)
		#print("f_sh = " + str(frame.shape))
		#frame_draw = frame.copy() # debug
		image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

		result = detector.detect_faces(image)	
		#print(" --- founded " + str(len(result)) + " boxes")	
		for cur_result in result:
			box_i = len(boxes)
			bounding_box = cur_result['box']
			left = bounding_box[0]
			top = bounding_box[1]
			right = bounding_box[0]+bounding_box[2]
			bottom = bounding_box[1] + bounding_box[3]

			color = (0,155,255)
			#cv2.rectangle(frame_draw, (left, top), (right, bottom), color, 2) # debug
			
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
					name = "Unknown"
					color = color_red
					if (min_ind != -1) and (min_val < tolerance):
						name = known_face_names[min_ind]
						color = color_green
					
					gender = 'Male'
					if face.gender==0:
						gender = 'Female'
					
					'''
					print("\tgender:%s"%(gender))
					print("\tembedding shape:%s"%face.embedding.shape)
					print("\tbbox:%s"%(face.bbox.astype(np.int).flatten())) # coordinates of face
					print("\tlandmark:%s"%(face.landmark.astype(np.int).flatten())) # coordinates of 5 points (eyes and nose)
					print("")
					'''
					#cv2.putText(frame_draw, name, (left, bottom + 40), font, 1.5, color, 2) # debug
					#cv2.putText(frame_draw, "Gender %s" % (gender), (left, bottom + 80), font, 1.5, color, 2) # debug
				
					boxes.append([])
					boxes[box_i].append(left-border_w)
					boxes[box_i].append(top-border_h)
					boxes[box_i].append(right+border_w)
					boxes[box_i].append(bottom+border_h)
					boxes[box_i].append(gender)
					boxes[box_i].append(name)

		# record answer to special file. create and record .xml answer
		root = xml.Element("boxes")
		for i in range(len(boxes)):
			xml_box = xml.Element("box_" + str(i)) # не должно название повторяться !
			root.append(xml_box)
			xml.SubElement(xml_box, "left").text = str(boxes[i][0])
			xml.SubElement(xml_box, "top").text = str(boxes[i][1])
			xml.SubElement(xml_box, "right").text = str(boxes[i][2])
			xml.SubElement(xml_box, "bottom").text = str(boxes[i][3])
			xml.SubElement(xml_box, "gender").text = str(boxes[i][4])
			xml.SubElement(xml_box, "name").text = str(boxes[i][5])			

		xml.ElementTree(root).write(ans_dir + filename[:-4] + ".xml")
		
		# record rec and unknown face if neccesarry (by settings for rec and for unknown)
		for i in range(len(boxes)):
			if save_recognized_faces and (boxes[i][5] != "Unknown"):
				for i in range(len(boxes)):			
					cv2.imwrite(rec_faces_dir + "face_" + str(i) + "_" + filename[:-4] + "_" + boxes[i][5] + ".png", frame[boxes[i][1]:boxes[i][3],boxes[i][0]:boxes[i][2]])
			
			if save_unknown_faces and (boxes[i][5] == "Unknown"):
				for i in range(len(boxes)):			
					cv2.imwrite(unk_faces_dir + "face_" + str(i) + "_" + filename[:-4] + ".png", frame[boxes[i][1]:boxes[i][3],boxes[i][0]:boxes[i][2]])
		
		# delete this file
		if delete_img_after_classificcation:
			os.remove(imgs_dir + filename)
		
		# show result on the screen
		#cv2.imshow("frame", frame_draw) # debug
		#cv2.waitKey(0) # debug
	
		timer_end = time.time()
		print("elapsed time is " + str(timer_end - timer_start))



























