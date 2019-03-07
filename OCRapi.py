import requests;
import urllib3;
import json;
import jsonpath;

url = "https://sandbox.api.sap.com/ml/ocr/ocr";
headers = {"APIKey":"9YDYKKcLitizMCzPlWiO0WsMHazVOU0j", "content-type":"multipart/form-data", "boundary":"---011000010111000001101001"};
data = {};
data['files']= ('1.jpg', open('C:\\Users\\i355926\\Desktop\\invoice\\taxi\\1.png', 'rb').read());
encode_data = urllib3.encode_multipart_formdata(data);
data = encode_data[0];
headers['Content-Type'] = encode_data[1];

r = requests.post(url, headers=headers, data=data);
text = r.text;
r = json.loads(r.text)
r = jsonpath.jsonpath(r, "$..predictions");
print(r);