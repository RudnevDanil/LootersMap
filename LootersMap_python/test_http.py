# --- get from python img and put it to db example
import requests 

url = "http://localhost:8000/php/test.php"
files = {'img': open('./test_img.png', 'rb')}
request = requests.post(url, files=files)
print("request code = ", request)
print(request.content)
print(request.text)