# --- get from db img and send it python
import requests 
import json
import base64
from PIL import Image
import io

url = "http://localhost:8000/php/test2.php"
request = requests.get(url, {'id': 6})
print("request code = ", request)
#print(request.content)
#print(request.text)
content = json.loads(request.content)

aaa = base64.b64decode(content["el"])

image = Image.open(io.BytesIO(aaa))
image.show()