from PIL import Image
import os, requests, json

train_data_path = "./train_data/"

# loading user login and password
with open("./auth.json") as json_file:
	data = json.load(json_file)
	login = data['login']
	password = data['pass']
	print('Login    : ' + data['login'])
	print('Password : ' + data['pass'])
	
faces_dir = './faces/'
url = "http://localhost:8000/php/saveClassficationResult.php"

print("\n loading to server ...")
#while True:
listDirectory = os.listdir(faces_dir)
image_paths = [os.path.join(faces_dir, f) for f in listDirectory]
for imagePath in image_paths:
	filename = imagePath[len(faces_dir):]
	print("\n"+filename)
	
	index1 = filename.find('_')
	index2 = filename.find('.png')
	if index1 == -1 or index2 == -1:
		print(" --- filename error ---")
		quit()		
	
	staff_id = int(filename[index1 + 1:index2])
	files = {'img': open(imagePath, 'rb')}
	request = requests.post(url, {'login': login, 'pass': password, 'staff_id': staff_id}, files=files)
	print("request code = ", request)
	if request.status_code != 200:
		print(" --- request error --- response code = " + str(request.status_code))
		quit()	
	print(request.content)
	#print(request.text)
	

	# delete loaded img
	#os.remove(imagePath])