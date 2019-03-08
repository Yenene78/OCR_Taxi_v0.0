import cv2;
import colorsys;
import numpy as np;
import roi_merge as roi_;
import PIL.Image as Image;
import saveImage as si;

class Picker:
	def __init__(self):
		print("****** Start CV Part ******");
		img = self.readImage(str(input("Please Input the ImgPath: ")));
		img_ = img.copy(); # back-up;
		img = self.shift_demo(img);
		img = self.colorFilter(img, img_);
		img = self.threshold(img);
		region = self.roi_solve(img);
		for i in range(len(region)):
			rect2 = region[i]
			w1,w2 = rect2[0],rect2[0]+rect2[2]
			h1,h2 = rect2[1],rect2[1]+rect2[3]
			box = [[w1,h2],[w1,h1],[w2,h1],[w2,h2]]
			cv2.drawContours(img_, np.array([box]), 0, (0, 0, 255), 1)
			# ocr(img[h1:h2,w1:w2]);
			# showImage(img[h1:h2,w1:w2],"block")
		self.showImage(img_, "Result");
		si.SaveImage(img_)
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
		PILImg = Image.fromarray(cv2.cvtColor(img.copy(),cv2.COLOR_BGR2RGB));
		count= PILImg.getcolors(PILImg.size[0]*PILImg.size[1]);
		count = sorted(count, reverse = True); # (count, (r,g,b));
		self.create_seq(count);

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

		# 取蓝色;
		HSV = cv2.cvtColor(img.copy(), cv2.COLOR_BGR2HSV);
		H, S, V = cv2.split(HSV);
		LowerBlue = np.array([80,43,46]);
		UpperBlue = np.array([160,255,255]);
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
	    cv2.imshow("iamge", img)
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
	        colorDic[(r,g,b)] = score;
	        if score > max_score:
	            max_score = score
	            dominant_color = (r,g,b)
	    colorDic = sorted(colorDic.items(), key=lambda item:item[1], reverse=True);
	    self.create_seq(colorDic);
	    # self.create_image(120,22,120)
	    return dominant_color
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
	# #均值迁移
	def shift_demo(self, img):
	    dst = cv2.pyrMeanShiftFiltering(img, 10, 50)
	    cv2.imshow("shift_demo", dst)
	    return dst;

if __name__ == "__main__":
	P = Picker();

