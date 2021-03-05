import requests, json, base64, io, os
from PIL import Image

train_data_path = "./train_data/"

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
url = "http://localhost:8000/php/loadTrainImgs.php"
request = requests.get(url, {'login': login, 'pass': password})
print("request code = ", request)
#print(request.content)
#print(request.text)

general_counter = 0
content = json.loads(request.content)
print(content['staff_id'])
if(content['answer'] == 'done'):
	for i in range(0, len(content['arr'])):
		image = Image.open(io.BytesIO(base64.b64decode(content['arr'][i])))
		image.save(train_data_path + "f" + str(general_counter) + "_" + content['staff_id'][i] + ".png", "PNG")
		general_counter += 1
	
	#os.system('python3 train.py &')
else:
	print(" --- HTTP error ---")