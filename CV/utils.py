import cv2;
import numpy as np;

# 双边滤波
def bi_demo(img, p1, p2):   
    dst = cv2.bilateralFilter(img, 0, p1, p2) # 100, 15
    cv2.imshow("bi_demo", dst)
    return dst;

# Provide several color masks;
def color_(img, flag):
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

# Input;
def readImage(path):
	img = cv2.imread(path, cv2.IMREAD_UNCHANGED);
	showImage(img, "Original");
	return img;
# Display Image;
def showImage(img, info):
	cv2.imshow(info, img);
	cv2.waitKey(0);

# 均值滤波
def shift_demo(img, p1, p2):
    dst = cv2.pyrMeanShiftFiltering(img, p1, p2) # 10, 50
    cv2.imshow("shift_demo", dst)
    return dst;

# 自适应threshold && 反色；
def threshold(img):
	img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
	img = cv2.adaptiveThreshold(img, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 11, 5)
	img = 255 - img;
	showImage(img, "Threshold");
	return img;