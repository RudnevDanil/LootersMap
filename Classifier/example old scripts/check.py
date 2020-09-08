import cv2, os, shutil
import numpy as np
from PIL import Image

# Путь к фотографиям
path = '../data/faces_6/'

# Получаем лица и соответствующие им номера
names = ['1_Omelchenko','2_Victoria','3_Rudnev','4_Oleg','5_Irina','6_Alexandr','7_Lena','8_Somebody','9_Roiby','10_Priimakov', '11_OlegDmitr','12_Vital','13_Ponkratov','14_Edik','15_Vova','16_Stud','17_Sveta','18_&&&','19_Max','20_Petrovich']
path_for_data_encod = './data_encod_150.npy'
path_for_data_names = './data_names_150.npy'

print(" Load a trained data...")
known_face_encodings = np.load(path_for_data_encod)
known_face_names = np.load(path_for_data_names)
print(" Using dataset on %d images" % len(known_face_encodings))

def cleanDirectory(path):
	#need import os, shutil
	for the_file in os.listdir(path):
		file_path = os.path.join(path, the_file)
		try:
			if os.path.isfile(file_path):
				os.unlink(file_path)
			# if we want clean subdirrictories - uncoment
			elif os.path.isdir(file_path): shutil.rmtree(file_path)
		except Exception as e:
			print(e)

def getImagesAndLabels(path):
	faces = []
	labels = []
	for i in range(1,len(names)+1):
		listDirectory = os.listdir(path+str(i))
		listDirectory.sort()
		image_paths = [os.path.join(path+str(i), f) for f in listDirectory]
		for imagePath in image_paths:
			image = Image.open(imagePath)
			image = np.array(image,'uint8')
			faces.append(image)
			labels.append(i)
	return faces, labels

# Load faces
print ("\n [INFO] Loading faces ...")
faces, labels = getImagesAndLabels(path)

# Print info
print("\n [INFO] {0} faces all.".format(len(labels)))
print("\n [INFO] {0} different people.".format(len(np.unique(labels))))

# Cleaning report directories
print('\nCleaning report directories.')
cleanDirectory('report/right/')
cleanDirectory('report/wrong/')
cleanDirectory('report/unknown/')

# Recognition
print('\nRecognition.')
right_answers = 0
wrong_answers = 0
unknown_detection = 0
for i in range(0, len(labels)):
	small_frame = cv2.resize(faces[i], (0, 0), fx=0.25, fy=0.25)
	rgb_small_frame = small_frame[:, :, ::-1]
	face_locations = face_recognition.face_locations(rgb_small_frame, number_of_times_to_upsample=3, model="hog")
	face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

	for face_encoding in face_encodings:
		# less tolerance will be more strict. Value 0.6 is default.
		matches = face_recognition.compare_faces(known_face_encodings, face_encoding, tolerance=0.6)
		face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
		best_match_index = np.argmin(face_distances)
		if matches[best_match_index]:
			if labels[i] == best_match_index:
				right_answers += 1
				cv2.imwrite("report/right/%d_"  % i + names[best_match_index] + '.jpg', labels[i])
			else:
				wrong_answers += 1
				cv2.imwrite("report/wrong/%d_"  % i + names[best_match_index] + '.jpg', labels[i])
		else:
			unknown_detection += 1
			cv2.imwrite("report/unknown/%d_"  % i + names[best_match_index] + '.jpg', labels[i])


print(' *** *** *** right   answers: ', str(right_answers), '/', str(len(labels)), '  ', str(right_answers/len(labels)*100), '%')
print(' *** *** *** wrong   answers: ', str(wrong_answers), '/', str(len(labels)), '  ', str(wrong_answers/len(labels)*100), '%')
print(' *** *** *** unknown answers: ', str(unknown_detection), '/', str(len(labels)), '  ', str(unknown_detection/len(labels)*100), '%')

