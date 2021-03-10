import requests, json, base64, io, os
from PIL import Image

xmlDoc = "./xml/settings.xml"

# loading user login and password
with open("./auth.json") as json_file:
	data = json.load(json_file)
	login = data['login']
	password = data['pass']
	#print('Login    : ' + data['login'])
	#print('Password : ' + data['pass'])
	
# loading data
url = "http://localhost:8000/php/loadSettingsData.php"
request = requests.get(url, {'login': login, 'pass': password})
if(request.status_code != 200):
	print("request code = ", request)
#print(request.content)
#print(request.text)

general_counter = 0
content = json.loads(request.content)
if(content['answer'] == 'done'):
	#print(content)
	data = "<?xml version='1.0' encoding='UTF-8'?>\n<data>\n";
	data += "\t<number_active_streams>" + str(len(content['arr'])) + "</number_active_streams>\n"
	for i in range(0, len(content['arr'])):		
		data += "\t<stream_" + str(i+1) + ">\n"
		data += "\t<path_to_cam>" + content['arr'][i][1] + "</path_to_cam>\n"
		data += "\t<fps>" + content['arr'][i][4] + "</fps>\n"
		data += "\t<skip_frames_saving>" + content['arr'][i][2] + "</skip_frames_saving>\n"
		data += "\t<skip_frames_classify>" + content['arr'][i][3] + "</skip_frames_classify>\n"
		data += "\t<is_show_on_screen>true</is_show_on_screen>\n"
		data += "\t<frames_in_one_avi_file>" + content['arr'][i][5] + "</frames_in_one_avi_file>\n"
		data += "\t<scaling>" + content['arr'][i][6] + "</scaling>\n"
		data += "\t</stream_" + str(i+1) + ">\n"
	data += "</data>\n";
	#print(data)
	
	f = open(xmlDoc, 'w')
	f.write(data)
	f.close()
	
else:
	print(" --- HTTP error ---")
