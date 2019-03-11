import cv2;
import colorsys;
import numpy as np;
import roi_merge as roi_;
import PIL.Image as Image;
import datetime;
import os;

import requests;
import urllib3;
import json;
import jsonpath;


class Picker:
	def __init__(self):
		print("****** Start CV Part ******");
		img = self.readImage(str(input("Please Input the ImgPath: ")));
		img_ = img.copy(); # back-up;
		img = self.shift_demo(img, 10, 50);
		# img = self.bi_demo(img, 100, 15);
		img = self.colorFilter(img, img_);
		img = self.threshold(img);
		img1 = img_.copy();
		region = self.roi_solve(img);
		for i in range(len(region)):
			rect2 = region[i]
			w1,w2 = rect2[0],rect2[0]+rect2[2]
			h1,h2 = rect2[1],rect2[1]+rect2[3]
			box = [[w1,h2],[w1,h1],[w2,h1],[w2,h2]]
			cv2.drawContours(img1, np.array([box]), 0, (0, 0, 255), 1)
			self.saveImage(img_, box, i)
		self.showImage(img1, "Result");
	# 双边滤波
	def bi_demo(self, image, p1, p2):   
	    dst = cv2.bilateralFilter(image, 0, p1, p2) # 100, 15
	    cv2.imshow("bi_demo", dst)
	    return dst;
	# call Api to recognize;
	def callApi(self, path):
		url = "https://sandbox.api.sap.com/ml/ocr/ocr";
		headers = {"APIKey":"9YDYKKcLitizMCzPlWiO0WsMHazVOU0j", "content-type":"multipart/form-data", "boundary":"---011000010111000001101001"};
		data = {};
		data['files']= ('1.jpg', open(path, 'rb').read());
		encode_data = urllib3.encode_multipart_formdata(data);
		data = encode_data[0];
		headers['Content-Type'] = encode_data[1];
		r = requests.post(url, headers=headers, data=data);
		text = r.text;
		# print(text);
		r = json.loads(r.text)
		r = jsonpath.jsonpath(r, "$..predictions");
		print(r);
	# [Cited] Provide several color masks;
	def color_(self, img, flag):
		HSV = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
		#LowerBlue从左到右分别表示"black","red","red","blue"的hsv值
		LowerBlue = [np.array([0,0,0]),np.array([0,43,46]),np.array([156,43,46]),np.array([100,43,46])]
		UpperBlue = [np.array([180,255,180]),np.array([10,255,255]),np.array([180,255,255]),np.array([124,255,255])]
		if flag == 0:
			mask_ = cv2.inRange(HSV.copy(),LowerBlue[3],UpperBlue[3])
		if flag == 1:
			mask_ = cv2.inRange(HSV.copy(),LowerBlue[1],UpperBlue[1]) + cv2.inRange(HSV.copy(),LowerBlue[2],UpperBlue[2])
		if flag == 2:
			mask_ = cv2.inRange(HSV.copy(),LowerBlue[0],UpperBlue[0])
		return mask_
	# Filters;
	def colorFilter(self, img, img_):
		# 转PIL_image,获取颜色统计;
		tmp = img.copy();
		# tmp = self.shift_demo(tmp, 10, 100);
		PILImg = Image.fromarray(cv2.cvtColor(tmp,cv2.COLOR_BGR2RGB));
		_, colorDic, img = self.get_dominant_color(PILImg, img);

		# 去除红色，带补全;
		HSV = cv2.cvtColor(img.copy(), cv2.COLOR_BGR2HSV);
		H, S, V = cv2.split(HSV);
		H = np.array(H).flatten()
		S = np.array(S).flatten()
		V = np.array(V).flatten()
		mask_R = self.color_(img_.copy(), 1);
		img_R = cv2.bitwise_and(img, img, mask=mask_R);
		img_R = cv2.bitwise_not(img_R);
		img -= img_R;
		self.showImage(img, "red")

		# LowerRed = np.array([0,43,46]);
		# UpperRed = np.array([10,255,255]);
		# mask_R = cv2.inRange(HSV, LowerRed, UpperRed);

		# img_R = cv2.bitwise_and(img, img, mask=mask_R);
		# img_R = cv2.bitwise_not(img_R);
		# img -= img_R;

		# LowerRed = np.array([156,43,46]);
		# UpperRed = np.array([180,255,255]);
		# mask_R = cv2.inRange(HSV, LowerRed, UpperRed);

		# img_R = cv2.bitwise_and(img, img, mask=mask_R);
		# img_R = cv2.bitwise_not(img_R);
		# img -= img_R;

		# LowerGreen = np.array([35,43,46]);
		# UpperGreen = np.array([77,255,255]);
		# mask_G = cv2.inRange(HSV, LowerGreen, UpperGreen);

		# img_G = cv2.bitwise_and(img, img, mask=mask_G);
		# img_G = cv2.bitwise_not(img_G);
		# img -= img_G;

		# 取蓝色;
		HSV = cv2.cvtColor(img.copy(), cv2.COLOR_BGR2HSV);
		H, S, V = cv2.split(HSV);

		for item in colorDic:
			color = item[1]
			Hue = colorsys.rgb_to_hsv(color[0]/255.0, color[1]/255.0, color[2]/255.0)[0]*180
			if (abs(Hue -112) < 12):
				break;
		rangeColor = 24
		LowerBlue = np.array([Hue - rangeColor,43,46]);
		UpperBlue = np.array([Hue + rangeColor,255,255]);
		mask_B = cv2.inRange(HSV, LowerBlue, UpperBlue);
		img_B = cv2.bitwise_and(img, img, mask=mask_B);
		self.showImage(img_B, "with blue")
		img = img_B;
		return img;
	# create Single img with given RGB;
	def create_image(self, r, g, b):
	    img = np.zeros((512,512,3), np.uint8) 
	    img[:,:,0]=r
	    img[:,:,1]=g
	    img[:,:,2]=b
	    cv2.imshow("image", img)
	    cv2.waitKey(0)
 	# create Multiple img with given colorDic(RGB);
	def create_seq(self, colorDic):
		img = np.zeros((512,512,3), np.uint8);
		i0 = 0;
		i1 = 0;
		size = 32; # dicide size of each Block;
		for i in range(len(colorDic)):
			if(i1 >= 512//size):
				i0 += 1;
				i1 = 0;
			curR = colorDic[i][1][0];
			curG = colorDic[i][1][1];
			curB = colorDic[i][1][2];
			img[i0*size:(i0+1)*size,i1*size:(i1+1)*size,0] = curR;
			img[i0*size:(i0+1)*size,i1*size:(i1+1)*size,1] = curG;
			img[i0*size:(i0+1)*size,i1*size:(i1+1)*size,2] = curB;
			i1 += 1;
		cv2.imshow("Sort Result", img)
		cv2.waitKey(0)
	def change_background(self, img, offset):
		print(offset)
		self.showImage(img, 'a')
		img = cv2.cvtColor(np.asarray(img), cv2.COLOR_RGB2BGR);
		(B,G,R) = cv2.split(img);
		for i in range(len(R)):
			for j in range(len(R[0])):
				R[i][j] = min(255,R[i][j]/offset[0]*255);
				G[i][j] = min(255,G[i][j]/offset[1]*255);
				B[i][j] = min(255,B[i][j]/offset[2]*255);
				# R[i][j] = min(R[i][j],R[i][j]+255-offset[0]);
				# G[i][j] = min(G[i][j],G[i][j]+255-offset[1]);
				# B[i][j] = min(B[i][j],B[i][j]+255-offset[2]);
		img = cv2.merge([R,G,B]);
		self.showImage(img, "2")
		return img

	# 颜色统计
	def get_dominant_color(self, image, img):
	    max_score = 0.0001
	    dominant_color = None
	    colorDic = {};
	    meanWhite = [255,255,255];
	    ctrWhite = 0;

	    for count,(r,g,b) in image.getcolors(image.size[0]*image.size[1]):
	        # 转为HSV标准
	        saturation = colorsys.rgb_to_hsv(r/255.0, g/255.0, b/255.0)[1]
	        y = min(abs(r*2104+g*4130+b*802+4096+131072)>>13,235)
	        y = (y-16.0)/(235-16)
	 		
	        #忽略高亮色
	        if y > 0.9:
	        	for i1 in range(len([r,g,b])):
	        		meanWhite[i1] = (meanWhite[i1] * ctrWhite + [r,g,b][i1])/(ctrWhite + 1);
	        	ctrWhite += 1;

	    img = self.change_background(img, meanWhite);
	    image = Image.fromarray(cv2.cvtColor(img,cv2.COLOR_BGR2RGB));


	    for count,(r,g,b) in image.getcolors(image.size[0]*image.size[1]):
	        # 转为HSV标准
	        saturation = colorsys.rgb_to_hsv(r/255.0, g/255.0, b/255.0)[1]
	        y = min(abs(r*2104+g*4130+b*802+4096+131072)>>13,235)
	        y = (y-16.0)/(235-16)
	 		
	        #忽略高亮色
	        # if y > 0.9:
	        # 	for i1 in range(len([r,g,b])):
	        # 		meanWhite[i1] = (meanWhite[i1] * ctrWhite + [r,g,b][i1])/(ctrWhite + 1);
	        # 	ctrWhite += 1;
	        	# print(ctrWhite, meanWhite)
	        	# continue;
	        	#self.create_image(255,255,255)
	        	#exit()
	        score = (saturation+0.1)*count
	        # colorDic[(r,g,b)] = score;
	        colorDic[score] = (r,g,b);
	        if score > max_score:
	            max_score = score
	            dominant_color = (r,g,b)

	    colorDic = sorted(colorDic.items(), key=lambda item:item[0], reverse=True);
	    self.create_seq(colorDic);
	    return dominant_color, colorDic, img;
	# 画框
	def find_region(self, img):
		#图像的宽带和高度
		h_img,w_img = img.shape
		# 查找轮廓
		contours,hierarchy = cv2.findContours(img, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
		# 获取矩形框
		rect_list = []
		for i in range(len(contours)):
			cont_ = contours[i]
			# 找到boundingRect
			rect = cv2.boundingRect(cont_)
			rect_list.append(rect)
		#筛选矩形框
		region = []
		for rect in rect_list:
			region.append(rect)
		return region
	# Merge ROI;
	def roi_solve(self, img):
		region = self.find_region(img);
		roi_solve = roi_.Roi_solve(region)
		roi_solve.rm_inside() 
		roi_solve.rm_overlop()
		region = roi_solve.merge_roi();
		return region
		lt = []
		region_ = []
		for rect in region:
			if(rect[3]>10):
				lt.append(rect[3])
		mostHeight = max(lt, key=lt.count)
		rangeHeight = 5
		for rect in region:
			if abs( rect[3] - mostHeight ) < rangeHeight :
				region_.append(rect)
		return region_;
	# 自适应threshold && 反色；
	def threshold(self, img):
		img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
		img = cv2.adaptiveThreshold(img, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 11, 5)
		img = 255 - img;
		self.showImage(img, "Threshold");
		return img;
	# Input;
	def readImage(self, path):
		img = cv2.imread(path, cv2.IMREAD_UNCHANGED);
		self.showImage(img, "Original");
		return img;
	# Display Image;
	def showImage(self, img, info):
		cv2.imshow(info, img);
		cv2.waitKey(0);
	# Output;
	def saveImage(self, img_, box, index):
		current_path = os.path.abspath(__file__)
		# 获取当前文件的父目录
		path = os.path.abspath(os.path.dirname(current_path) + os.path.sep + ".") + "\\result"
		if not os.path.exists(path):
			os.makedirs(path)
		curTime = str(datetime.datetime.now().strftime("%Y%m%d%H%M%S"));
		savepath = path + "\\" + curTime + "-" +str(index)+ ".png"
		#print(savepath)
		Xs = [i[0] for i in box]
		Ys = [i[1] for i in box]
		x1 = min(Xs)
		x2 = max(Xs)
		y1 = min(Ys)
		y2 = max(Ys)
		hight = y2 - y1
		width = x2 - x1
		img_ =self.threshold(img_)
		crop_img = img_[y1:y1+hight, x1:x1+width]
		cv2.imwrite(savepath, crop_img); 
		self.callApi(savepath);
	# #均值迁移
	def shift_demo(self, img, p1, p2):
	    dst = cv2.pyrMeanShiftFiltering(img, p1, p2) # 10, 50
	    cv2.imshow("shift_demo", dst)
	    return dst;

if __name__ == "__main__":
	P = Picker();

