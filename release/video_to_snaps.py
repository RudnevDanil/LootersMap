import cv2, os, shutil, time
import numpy as np

video_dir = './video_for_classification/'
imgs_dir = './saved_imgs/'
done_video_dir = video_dir + 'done/'

if not os.path.exists(done_video_dir):
	os.mkdir(done_video_dir)

while(True):
	counetr_files = 0
	files = os.listdir(video_dir)
	
	for filename in files:
		if not os.path.isdir(video_dir + filename):
			print(" --- working with file named " + video_dir + filename)
			counetr_files += 1
			
			cap = cv2.VideoCapture(video_dir + filename)
			
			if not cap.isOpened(): 
				print(" --- ERROR --- could not open :" + fn)
				break
				
			success, image = cap.read()
			fr_counter = 0
			saving_counter = 0
			while success:
				if(fr_counter % 25 == 0): # how much frames to skip
					cv2.imwrite(imgs_dir + "video_" + filename + "__frame_%d.jpg" % saving_counter, image)  
					saving_counter += 1
					print(' + ', end='') if success else  print(' - ', end='')
					if(saving_counter % 25 == 0): # just for printing
						print(' / %d min. %d sec.done' % (saving_counter // 60 , saving_counter % 60))
				success, image = cap.read()
				fr_counter += 1
			
			shutil.move(video_dir + filename, done_video_dir)
			
	if counetr_files == 0:
		print(" . ", end='', flush=True)
		time.sleep(0.5)
