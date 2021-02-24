from PIL import Image
import os
import requests 

faces_dir = './faces/'
url = "http://localhost:8000/php/saveClassficationResult.php"

print("\n loading to server ...")
#while True:
listDirectory = os.listdir(faces_dir)
image_paths = [os.path.join(faces_dir, f) for f in listDirectory]
for imagePath in image_paths:
	filename = imagePath[len(faces_dir):]
	print(filename)
	
	index1 = filename.find('_')
	index2 = filename.find('.png')
	if index1 == -1 or index2 == -1:
		print(" --- filename error ---")
		quit()		
	
	staff_id = int(filename[index1 + 1:index2])
	files = {'img': open(imagePath, 'rb')}
	request = requests.post(url, files=files)
	if request.status_code != 200:
		print(" --- request error --- response code = " + str(request.status_code))
		quit()	
	
	# delete loaded img
	#os.remove(imagePath])