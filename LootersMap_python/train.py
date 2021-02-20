from PIL import Image
import os
import numpy as np
import insightface

path_for_imgs = '/home/user/Desktop/Face_Recognition/data/faces/'
encod_path = './data_encod.npy'
ids_path = './data_ids.npy'

model = insightface.app.FaceAnalysis()
model.prepare(ctx_id = -1, nms=0.4)

print("\n Reading images ...")
encods = []
ids = []
listDirectory = os.listdir(path_for_imgs)
image_paths = [os.path.join(path_for_imgs, f) for f in listDirectory]
for imagePath in image_paths:
	filename = imagePath[len(path_for_imgs):]
	byf = np.array(Image.open(imagePath),'uint8')
	faces_from_model = model.get( byf )
	if len(faces_from_model):
		index = filename.find('_')
		if index != -1:
			encods.append(faces_from_model[0].normed_embedding)
			ids.append(int(filename[:index]))
print(" Reading images ... DONE\n")

print(" Saving ...")
np.save(encod_path, encods)
np.save(ids_path, ids)
print(" Saving ... DONE\n")
