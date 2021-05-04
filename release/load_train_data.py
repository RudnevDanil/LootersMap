import requests, json, base64, io, os
from PIL import Image
import numpy as np

train_data_path = "./train_data/"
train_img_ids_file = "./train_image_ids"

print(" ---------- load_train_data.py .... ----------")

# loading user login and password
with open("./auth.json") as json_file:
	data = json.load(json_file)
	login = data['login']
	password = data['pass']
	print('Login    : ' + data['login'])
	print('Password : ' + data['pass'])
	
# clar directory
files = os.listdir(train_data_path)
for filename in files:
	os.remove(train_data_path + filename)
	
# loading images
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
#url = "http://localhost:8000/php/loadTrainImgs.php"
url = "http://h96046yr.beget.tech/lm/php/loadTrainImgs.php"

request = requests.get(url, {'login': login, 'pass': password, headers=headers})
if(request.status_code != 200):
	print("request code = ", request)
#print(request.content)
#print(request.text)

general_counter = 0
content = json.loads(request.content)
if(content['answer'] == 'done'):
	train_img_ids = np.array([])
	for i in range(0, len(content['arr'])):
		image = Image.open(io.BytesIO(base64.b64decode(content['arr'][i])))
		image.save(train_data_path + "f" + str(general_counter) + "_" + content['staff_id'][i] + ".png", "PNG")
		#train_img_ids = np.append(train_img_ids, content['ids'][i])
		general_counter += 1
	#np.save(train_img_ids_file, train_img_ids)
	print(" ---------- load_train_data.py DONE ----------")
	os.system('python3 train.py')
else:
	print(" --- HTTP error ---")


