from PIL import Image
import face_recognition
import os
import numpy as np

path_for_imgs = '../data/faces_old/'
path_for_data_encod = './data_encod.npy'
path_for_data_names = './data_names.npy'

# 150 --- 7
# 500 --- 30
# ### --- all 2500

names = ['1_Omelchenko','2_Victoria','3_Rudnev','4_Oleg','5_Irina','6_Alexandr','7_Lena','8_Somebody','9_Roiby','10_Priimakov', '11_OlegDmitr','12_Vital','13_Ponkratov','14_Edik','15_Vova','16_Stud','17_Sveta','18_&&&','19_Max','20_Petrovich']

def getImagesAndLabelsWithoutCheck(path):
	faces = []
	labels = []
	for i in range(1,len(names)+1):
		listDirectory = os.listdir(path+str(i))
		#listDirectory.sort()
		image_paths = [os.path.join(path+str(i), f) for f in listDirectory]
		counter = 0
		for imagePath in image_paths:
			image = face_recognition.load_image_file(imagePath)			
			faces.append(image)
			labels.append(i)
			'''			
			counter += 1
			if counter > 30:
				break
			'''
	return faces, labels

print(" Reading images ...\n")
images, labels = getImagesAndLabelsWithoutCheck(path_for_imgs)
print(" Will be used %d images.\n" % len(images))

print(" Process encodings ...\n")
known_face_encodings = []
known_face_names = []
for i in range(0,len(images)):
	encoding = face_recognition.face_encodings(images[i])
	if len(encoding):
		known_face_encodings.append(face_recognition.face_encodings(images[i])[0])
		known_face_names.append(names[labels[i]-1])

np.save(path_for_data_encod,known_face_encodings)
np.save(path_for_data_names,known_face_names)


