# function of rotation is ready, working good, but I'm not sure, that we need that functionality

from PIL import Image
import os, cv2
import numpy as np
import insightface

import math
from numpy import matrix
from numpy import linalg

path = '../data/faces_6/'

model = insightface.app.FaceAnalysis()
model.prepare(ctx_id = -1, nms=0.4)



def rotate(imN,l_eye, r_eye):
	def rot_x(angle,ptx,pty):
	    return math.cos(angle)*ptx + math.sin(angle)*pty
	def rot_y(angle,ptx,pty):
	    return -math.sin(angle)*ptx + math.cos(angle)*pty
	im = Image.fromarray(imN)
	angle = -math.atan(math.fabs(l_eye[1]-r_eye[1])/math.fabs(l_eye[0]-r_eye[0]))
	(x,y) = im.size
	xextremes = [rot_x(angle,0,0),rot_x(angle,0,y-1),rot_x(angle,x-1,0),rot_x(angle,x-1,y-1)]
	yextremes = [rot_y(angle,0,0),rot_y(angle,0,y-1),rot_y(angle,x-1,0),rot_y(angle,x-1,y-1)]
	mnx = min(xextremes)
	mxx = max(xextremes)
	mny = min(yextremes)
	mxy = max(yextremes)
	T = matrix([[math.cos(angle),math.sin(angle),-mnx],[-math.sin(angle),math.cos(angle),-mny],[0,0,1]])
	Tinv = linalg.inv(T)
	Tinvtuple = (Tinv[0,0],Tinv[0,1], Tinv[0,2], Tinv[1,0],Tinv[1,1],Tinv[1,2])
	new_im = im.transform((int(round(mxx-mnx)),int(round((mxy-mny)))),Image.AFFINE,Tinvtuple,resample=Image.BILINEAR)
	return np.array(new_im,'uint8')

frame = []
is_read = True
face_counter = 0

for i in range(1,21):
	listDirectory = os.listdir(path+str(i))
	image_paths = [os.path.join(path+str(i), f) for f in listDirectory]
	counter = 0
	for imagePath in image_paths:
		if is_read:		
			frame = np.array(Image.open(imagePath),'uint8')
			is_read = not is_read
		else:
			frame = rotate(frame,left_eye_coord,right_eye_coord)
			is_read = not is_read
	
		faces_from_model = model.get( frame )
		if len(faces_from_model):
			result = faces_from_model[0]
			left_eye_coord = (result.landmark[0][0],result.landmark[0][1])
			right_eye_coord = (result.landmark[1][0],result.landmark[1][1])
			
			color = (0,155,255)
			cv2.circle(frame,left_eye_coord, 2, color, 2)
			cv2.circle(frame,right_eye_coord, 2, color, 2)
			cv2.rectangle(frame, ((int)(result.bbox[0]), (int)(result.bbox[1])), ((int)(result.bbox[2]), (int)(result.bbox[3])), color, 2)
			
		cv2.imshow('Video', frame)
		cv2.imwrite("report/byf/%d.jpg"  % face_counter, frame)		
		face_counter += 1
		'''
		while True:
			if cv2.waitKey(1) & 0xFF == ord('n'):
				break
		'''
			
			
			
			




