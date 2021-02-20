import requests 
import json
import numpy as np
import cv2
from wand.image import Image 
from io import StringIO #from io import StringIO.
import PIL.Image

#print(requests.get('http://learn.python.ru'))

'''
request = requests.get('http://localhost:8000/')
print("request code = ", request)
print("request content = ", request.content)
'''

url = "http://localhost:8000/php/test.php"
request = requests.post(url, {'a': 123})
print("request code = ", request)
if request.status_code == 200:
	content = json.loads(request.content)
	print("request content = ", content["answer"])
	if(content["answer"] == "done"):
		arr = content["arr"]
		print("request len(arr) = ", len(arr))
		'''
		nparr = np.frombuffer(arr[0][0].encode(), np.uint8)  
		print(nparr)
		#img_np = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
		img_np = cv2.imdecode(nparr, 1)
		print(img_np)
		'''
		
		data = arr[0][0]
		dataS = arr[0][0][22:]
		dataE = data.encode()
		dataSE = dataS.encode()
		
		'''
		with open("./1.png", 'wb') as file:
			file.write(dataSE)
		'''	
		
		file_like= StringIO(dataS)
		img=PIL.Image.open(file_like)
		img.show()
		
		#cv2.imshow("frame", nparr)
		#cv2.waitKey(0)
		
	
	
'''

Convert Image to String

import base64
 
with open("t.png", "rb") as imageFile:
    str = base64.b64encode(imageFile.read())
    print str



Convert String to Image

fh = open("imageToSave.png", "wb")
fh.write(str.decode('base64'))
fh.close()

'''