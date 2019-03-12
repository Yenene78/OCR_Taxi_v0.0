import pytesseract;
import requests;
import urllib3;
import json;
import jsonpath;

# call our Api;
def callApi(path):
	url = "https://sandbox.api.sap.com/ml/ocr/ocr";
	headers = {"APIKey":"9YDYKKcLitizMCzPlWiO0WsMHazVOU0j", "content-type":"multipart/form-data", "boundary":"---011000010111000001101001"};
	data = {};
	data['files']= ('1.jpeg', open(path, 'rb').read());
	encode_data = urllib3.encode_multipart_formdata(data);
	data = encode_data[0];
	headers['Content-Type'] = encode_data[1];
	r = requests.post(url, headers=headers, data=data);
	text = r.text;
	print(text);

# Tesseract;
def ocr(img, lang):
	text = pytesseract.image_to_string(img, lang=lang);
	if(text == ""):
		return;
	print("[TES]: " + text);