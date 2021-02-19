from PIL import Image
import os
import numpy as np
import insightface

path_for_imgs = '/home/user/Desktop/Face_Recognition/data/faces_6/'
path_for_data_encod = './data_encod.npy'
path_for_data_names = './data_names.npy'

model = insightface.app.FaceAnalysis()
model.prepare(ctx_id = -1, nms=0.4)

names = ['1_Omelchenko','2_Victoria','3_Rudnev','4_Oleg','5_Irina','6_Alexandr','7_Lena','8_Somebody','9_Roiby','10_Priimakov', '11_OlegDmitr','12_Vital','13_Ponkratov','14_Edik','15_Vova','16_Stud','17_Sveta','18_&&&','19_Max','20_Petrovich']

def getImagesAndLabelsWithoutCheck(path):
	faces = []
	labels = []
	for i in range(1,len(names)+1):
		listDirectory = os.listdir(path+str(i))
		image_paths = [os.path.join(path+str(i), f) for f in listDirectory]
		counter = 0
		for imagePath in image_paths:
			byf = np.array(Image.open(imagePath),'uint8')
			faces_from_model = model.get( byf )
			if len(faces_from_model):
				face = faces_from_model[0]			
				faces.append(face.normed_embedding)
				labels.append(i)
	return faces, labels

print(" Reading images ...\n")
known_face_encodings = []
known_face_encodings, labels = getImagesAndLabelsWithoutCheck(path_for_imgs)
print(" Will be used %d images.\n" % len(labels))

print(" Process encodings ...\n")

known_face_names = []
for i in range(0,len(labels)):
	known_face_names.append(names[labels[i]-1])

np.save(path_for_data_encod,known_face_encodings)
np.save(path_for_data_names,known_face_names)


