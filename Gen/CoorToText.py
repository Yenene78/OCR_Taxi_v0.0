import pytesseract
from PIL import Image
import xlrd
import json
import os

def coor_record(img,coor,filepath):
	'''
	Convert Coordinates to records

	coor : a list of coordinates;
		<e.g.> coor = [(92, 244, 115, 432), (92, 432, 115, 620),...]

	records : a one-dim list to record all recognized rectangles' values;
		<e.g.> records = [rec1,rec2...] 

	'''
	api.send('output',("Start Coor -> Record"))
	image = Image.fromarray(img)
	records=[];
	respath = os.path.join(filepath,'results')
	if not os.path.exists(respath):
		os.mkdir(respath)
	for num, pos in enumerate(coor) :
		# crop [(left, up, right, bottom),...]
		cropped_image = image.crop((pos[1]+3,pos[0]+3,pos[3],pos[2]))
		cropped_image.save(os.path.join(respath,str(num)+".jpg"))
		record = pytesseract.image_to_string(cropped_image).replace("\n\n", " ").replace("\n", " ")
		# need to fix
		# Can't recognize single digit
		if(len(record)==0):
			record = "<BLANK>";
		api.send('output',("Rect " + str(num + 1) + " finished. The result is " + record))
		records.append(record)
	return records

def record_dict(filepath,field,records):
	'''
	
	Convert records to dict, save as json (dic.txt)

	field : it is a list of field name;
		<e.g.> field = ['Plant', 'Date', 'No.'...]

	records : it is a one-dim list to record all recognized rectangles' values;
		<e.g.> records = [rec1,rec2...] 

	dic : it is a dictionary of restructural data;
		<e.g.> dic = {"Plant": "35","Date": "None","Item1": {"No.": "64","MatrialDescription": "41",...},"Item2": {"No.": "68","MatrialDescription": "20",...}...}

	'''
	api.send('output',("Start Record -> Dict"))
	filepath = os.path.join(filepath, "output/dic.txt");
	dic = {}
	temp_dic = {}
	col_field = []
	field_status = 0
	col = 0
	item_num = 0
	for num, val in enumerate(records):
		if (field_status == -1):
			field_status = 0
			continue
		if (num == len(records) - 1):
			temp_dic[col_field[col]] = val
			col = col + 1
			if(col == len(col_field)):
				item_num = item_num + 1
				dic["Item"+str(item_num)] = temp_dic;
				temp_dic = {}
				col = 0;
				if(next_val in field):
					col_field = []
			continue;
		next_val = records[num + 1]
		if ((val in field) and (next_val in field)):
			if (field_status == 1) :
				col_field.append(next_val);
			else :
				col_field.append(val);
				col_field.append(next_val);
				field_status = 1
		elif ((val in field) and (next_val not in field)):
			if(field_status == 0):
				dic[val] = next_val
				field_status = -1
			else:
				field_status = 0
		else:
			temp_dic[col_field[col]] = val
			col = col + 1
			if(col == len(col_field)):
				item_num = item_num + 1
				dic["Item"+str(item_num)] = temp_dic;
				temp_dic = {}
				col = 0;
				if(next_val in field):
					col_field = []
	api.send('output',(str(dic)))
	file = open(filepath, "w")
	file.write(json.dumps(dic,indent=4))
	file.close()
	return dic

def get_content(coor,img,message,field):
	'''

	'''
	filepath = message.body
	filepath = os.path.split(filepath)[0]
	api.send('output',filepath)
	img = img.copy()
	records = coor_record(img,coor,filepath)
	field = field.split(",")
	dic = record_dict(os.path.split(os.path.split(filepath)[0])[0],field,records)
	api.send('terminate', "EOF");

api.set_port_callback(["input","imgin","pathin","field"], get_content)
