from PIL import Image
import os, requests, json

def intTryParse(value):
    try:
        return int(value), True
    except ValueError:
        return value, False
        
# loading user login and password
with open("./auth.json") as json_file:
	data = json.load(json_file)
	login = data['login']
	password = data['pass']
	#print('Login    : ' + data['login'])
	#print('Password : ' + data['pass'])
	
faces_dir = './faces/'

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
#url = "http://localhost:8000/php/saveClassficationResult.php"
url = "http://h96046yr.beget.tech/lm/php/saveClassficationResult.php"

while True:
	listDirectory = os.listdir(faces_dir)
	image_paths = [os.path.join(faces_dir, f) for f in listDirectory]
	for imagePath in image_paths:
		filename = imagePath[len(faces_dir):]
		#print("\n"+filename)

		index1 = filename.find('_')
		index2 = filename.find('_', index1 + 1)
		index3 = filename.find('.png')
		if index1 == -1 or index2 == -1 or index3 == -1:
			print(" --- filename error ---")
			quit()		
		
		staff_id = int(filename[index1 + 1:index2]) if intTryParse(filename[index1 + 1:index2])[1] else -1
		camCode = int(filename[index2 + 1:index3])  if intTryParse(filename[index2 + 1:index3])[1] else -1

		files = {'img': open(imagePath, 'rb')}
		request = requests.post(url, {'login': login, 'pass': password, 'staff_id': staff_id, 'camCode': camCode}, files=files, headers=headers)
		#print("request code = ", request)
		if request.status_code != 200:
			print(" --- request error --- response code = " + str(request.status_code))
			quit()	
		#print(request.content)
		#print(request.text)


		# delete loaded img
		os.remove(imagePath)
