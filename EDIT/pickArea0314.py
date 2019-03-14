import cv2;
import colorsys;
import numpy as np;
import roi_merge as roi_;
import PIL.Image as Image;
import datetime;
import os;
import utils;
import request;
import math;

class Picker:
	def __init__(self):
		print("****** Start CV Part ******");
		img = utils.readImage(str(input("Please Input the ImgPath: ")));
		img_ = img.copy(); # back-up;
		img = utils.shift_demo(img, 10, 50);
		img = self.colorFilter(img, img_);
		img = utils.threshold(img);

		img1 = img_.copy();
		region = self.roi_solve(img);
		for i in range(len(region)):
			rect2 = region[i]
			w1,w2 = rect2[0],rect2[0]+rect2[2]
			h1,h2 = rect2[1],rect2[1]+rect2[3]
			box = [[w1,h2],[w1,h1],[w2,h1],[w2,h2]]
			cv2.drawContours(img1, np.array([box]), 0, (0, 0, 255), 1)
			# self.saveImage(img_, box, i)
		utils.showImage(img1, "Result");

	# Filters;
	def colorFilter(self, img, img_):
		# 转PIL_image,获取颜色统计;
		tmp = img.copy();
		PILImg = Image.fromarray(cv2.cvtColor(tmp,cv2.COLOR_BGR2RGB));
		_, colorDic = self.get_dominant_color(PILImg);

		# 去除红色，带补全;
		HSV = cv2.cvtColor(img.copy(), cv2.COLOR_BGR2HSV);
		H, S, V = cv2.split(HSV);
		H = np.array(H).flatten()
		S = np.array(S).flatten()
		V = np.array(V).flatten()
		mask_R = utils.color_(img_.copy(), 1);
		img_R = cv2.bitwise_and(img, img, mask=mask_R);
		img_R = cv2.bitwise_not(img_R);
		img -= img_R;
		# utils.showImage(img, "red")

		# 取蓝色;
		HSV = cv2.cvtColor(img.copy(), cv2.COLOR_BGR2HSV);
		H, S, V = cv2.split(HSV);
		rangeColor = 20
		for item in colorDic:
			color = item[1]
			Hue = colorsys.rgb_to_hsv(color[0]/255.0, color[1]/255.0, color[2]/255.0)[0]*180
			if (abs(Hue - 112) < rangeColor):
				break;
		LowerBlue = np.array([Hue - rangeColor,43,46]);
		UpperBlue = np.array([Hue + rangeColor,255,255]);
		mask_B = cv2.inRange(HSV, LowerBlue, UpperBlue);
		img_B = cv2.bitwise_and(img, img, mask=mask_B);
		utils.showImage(img_B, "with blue")
		img = img_B;
		return img;

	# create Single img with given RGB;
	def create_image(self, r, g, b):
	    img = np.zeros((512,512,3), np.uint8) 
	    img[:,:,0]=r
	    img[:,:,1]=g
	    img[:,:,2]=b
	    # cv2.imshow("image", img)
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

	# 颜色统计
	def get_dominant_color(self, image):
	    max_score = 0.0001
	    dominant_color = None
	    colorDic = {};
	    for count,(r,g,b) in image.getcolors(image.size[0]*image.size[1]):
	        # 转为HSV标准
	        saturation = colorsys.rgb_to_hsv(r/255.0, g/255.0, b/255.0)[1]
	        y = min(abs(r*2104+g*4130+b*802+4096+131072)>>13,235)
	        y = (y-16.0)/(235-16)
	        #忽略高亮色
	        if y > 0.9:
	            continue
	        score = (saturation+0.1)*count
	        colorDic[score] = (r,g,b);
	        if score > max_score:
	            max_score = score
	            dominant_color = (r,g,b)
	    colorDic = sorted(colorDic.items(), key=lambda item:item[0], reverse=True);
	    self.create_seq(colorDic);
	    return dominant_color, colorDic;

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
		lt = []

		# 出现次数最多的>10的宽度mostHeight 取[mH/2,mH*2]之间的矩形，可整段注释
		region_ = []
		for rect in region:
			if(rect[3]>10):
				lt.append(rect[3])
		mostHeight = max(lt, key=lt.count)
		rangeHeight = 20
		for rect in region:
			if abs( math.log( float(rect[3]) / mostHeight, 2)) < 1 :
				region_.append(rect)
		return region_;

		return region;

	# Output;
	def saveImage(self, img_, box, index):
		current_path = os.path.abspath(__file__)
		# 获取当前文件的父目录
		path = os.path.abspath(os.path.dirname(current_path) + os.path.sep + ".") + "\\result"
		if not os.path.exists(path):
			os.makedirs(path)
		savepath = path + "\\" + str(datetime.datetime.now().strftime("%Y%m%d%H%M%S")) + "-" +str(index)+ ".png"
		Xs = [i[0] for i in box]
		Ys = [i[1] for i in box]
		x1 = min(Xs)
		x2 = max(Xs)
		y1 = min(Ys)
		y2 = max(Ys)
		hight = y2 - y1
		width = x2 - x1
		img_ = utils.shift_demo(img_, 10, 50);
		img_ =utils.threshold(img_)
		crop_img = img_[y1:y1+hight, x1:x1+width];
		crop_img = 255 - crop_img;
		cv2.imwrite(savepath, crop_img);
		request.callApi(savepath)
		request.ocr(crop_img, "test1");



if __name__ == "__main__":
	P = Picker();

