import requests, json, base64, io, os, time
from PIL import Image
import numpy as np

print(" ---------- reTrainChecker.py ----------")

# loading user login and password
with open("./auth.json") as json_file:
	data = json.load(json_file)
	login = data['login']
	password = data['pass']
	print('Login    : ' + data['login'])
	print('Password : ' + data['pass'])


check_file = "./isClassify"
if(os.path.exists(check_file)):
	os.remove(check_file)

os.system('python3 classifier.py &')

train_img_ids_file = "./train_image_ids"
train_img_ids = np.array([])
train_img_ids = np.load(train_img_ids_file + ".npy")


url = "http://localhost:8000/php/loadTrainImgs.php"
while(True):
	request = requests.get(url, {'login': login, 'pass': password, 'idsOnly': 'true'})
	if(request.status_code != 200):
		print("request code = ", request)	
	content = json.loads(request.content)
	
	if(content['answer'] == 'done'):
		train_img_ids_loaded = np.array([])
		for i in range(0, len(content['ids'])):
			train_img_ids_loaded = np.append(train_img_ids_loaded, content['ids'][i])
		
		if train_img_ids_loaded.size != train_img_ids.size or (train_img_ids_loaded.size == train_img_ids.size and all( train_img_ids_loaded == train_img_ids) == False ):
			np.save(train_img_ids_file, train_img_ids_loaded)
			train_img_ids = train_img_ids_loaded.copy()
			if(os.path.exists(check_file)):
				os.remove(check_file)
			os.system('python3 load_train_data.py')
		else:
			#print(" --- No changes ---")
			if(not os.path.exists(check_file)):
				open(check_file, 'w').close()
	else:
		print(" --- HTTP error ---")
	
	time.sleep(1)
