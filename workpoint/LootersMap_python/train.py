from PIL import Image
import os
import numpy as np
import insightface

path_for_imgs = '/home/user/Desktop/Face_Recognition/data/faces/'
path_for_data_encod = './data_encod.npy'
path_for_data_names = './data_names.npy'

model = insightface.app.FaceAnalysis()
model.prepare(ctx_id = -1, nms=0.4)

names = []
f = open(path_for_imgs + 'annotation.txt', 'r')
for line in f:
	index = line.find('_')
	if index != -1:
		names.append(line[index+1:len(line)-1])
f.close()
print("\n Names:")
print(names)

print("\n Reading images ...")
known_face_encodings = []
known_face_names = []
labels = []

listDirectory = os.listdir(path_for_imgs)
image_paths = [os.path.join(path_for_imgs, f) for f in listDirectory]
for imagePath in image_paths:
	filename = imagePath[len(path_for_imgs):]
	if(filename != "annotation.txt"):
		byf = np.array(Image.open(imagePath),'uint8')
		faces_from_model = model.get( byf )
		if len(faces_from_model):
			index = filename.find('_')
			if index != -1:	
				known_face_encodings.append(faces_from_model[0].normed_embedding)				
				known_face_names.append(names[int(filename[:index])-1])
print(" Reading images ... DONE\n")

print("\n Saving ...")
np.save(path_for_data_encod,known_face_encodings)
np.save(path_for_data_names,known_face_names)
print(" Saving ... DONE\n")
