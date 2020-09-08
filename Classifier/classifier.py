import face_recognition
import cv2, os
import numpy as np
from PIL import Image
from mtcnn import MTCNN
import insightface
from scipy import spatial
import xml.etree.ElementTree as xml

color_green = (0,255,0)
color_red = (0,0,255)

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

imgs_dir = './imgs/'
ans_dir = './answers/'
rec_faces_dir = "./recognized_faces/"
unk_faces_dir = "./unknown_faces/"
while(True):
	print("----------- new while iteration -----------")
	files = os.listdir(imgs_dir)
	print(" --- Founded " + str(len(files)) + " files")
	for filename in files:
		print("\n --- working with file named " + filename + " ...")
		boxes = []
		
		frame = cv2.imread(imgs_dir + filename)
		image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

		result = detector.detect_faces(image)	
		print(" --- founded " + str(len(result)) + " boxes")	
		for cur_result in result:
			box_i = len(boxes)
			bounding_box = cur_result['box']
			keypoints = cur_result['keypoints']
			left = bounding_box[0]
			top = bounding_box[1]
			right = bounding_box[0]+bounding_box[2]
			bottom = bounding_box[1] + bounding_box[3]

			color = (0,155,255)
			cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
			
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
					
					print("\tgender:%s"%(gender))
					print("\tembedding shape:%s"%face.embedding.shape)
					print("\tbbox:%s"%(face.bbox.astype(np.int).flatten())) # coordinates of face
					print("\tlandmark:%s"%(face.landmark.astype(np.int).flatten())) # coordinates of 5 points (eyes and nose)
					print("")
					cv2.putText(frame, name, (left, bottom + 40), font, 1.5, color, 2)
					cv2.putText(frame, "Gender %s" % (gender), (left, bottom + 80), font, 1.5, color, 2)
				
					boxes.append([])
					boxes[box_i].append(left)
					boxes[box_i].append(top)
					boxes[box_i].append(right)
					boxes[box_i].append(bottom)
					boxes[box_i].append(gender)
					boxes[box_i].append(name)

					


		# record answer to special file
		# ---
		print(boxes)
		# create and record .xml answer
		root = xml.Element("boxes")
		for box in boxes:
			xml_box = xml.Element("box")
			root.append(xml_box)
			b = xml.SubElement(xml_box, "left")
			b.text = str(box[0])

		tree = xml.ElementTree(root)
		with open(ans_dir + filename[:-4] + ".xml", 'w') as fh:
			tree.write(fh) # FAIL !!! 

		# record rec and unknown face if neccesarry (by settings for rec and for unknown)
		# ---
		
		# delete this file
		# ---

		# show result on the screen
		cv2.imshow("frame", frame) # debug
		cv2.waitKey(0) # debug





























