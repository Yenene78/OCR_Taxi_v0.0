# #边缘保留滤波（EPF）  高斯双边、均值迁移
# import cv2 as cv
# import numpy as np
# import roi_merge as roi_;
 
# def bi_demo(image):   #双边滤波
#     dst = cv.bilateralFilter(image, 0, 100, 15)
#     # cv.namedWindow("bi_demo", cv.WINDOW_NORMAL)
#     cv.imshow("bi_demo", dst)
 
# def shift_demo(image):   #均值迁移
#     dst = cv.pyrMeanShiftFiltering(image, 10, 50)
#     # cv.namedWindow("shift_demo", cv.WINDOW_NORMAL)
#     cv.imshow("shift_demo", dst)
 
# # src = cv.imread('taxi/5.png')
# # # cv.namedWindow('input_image', cv.WINDOW_NORMAL)
# # cv.imshow('input_image', src)
 
# # bi_demo(src)
# # shift_demo(src)
 
# # cv.waitKey(0)
# # cv.destroyAllWindows()

# path = "taxi/1.png"

# def detection(img):
#     gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
#     #ret, dst = cv.threshold(gray, 200, 255, cv.THRESH_OTSU)
#     ret, dst = cv.threshold(gray, 188, 255, cv.THRESH_BINARY_INV)
#     return dst

# image = cv.imread(path)

# img = cv.pyrMeanShiftFiltering(src = image, sp = 5, sr = 40)

# dst = detection(img)
# contours, hierarchy = cv.findContours(dst, cv.RETR_TREE, cv.CHAIN_APPROX_NONE)
# cv.drawContours(image, contours, -1, (0, 0, 255), 2)
# cv.imshow('img', image)
# cv.waitKey(0)

import colorsys
import numpy as np
import cv2 as cv
import PIL.Image as Image

def create_image(r,g,b):
    img = np.zeros((512,512,3), np.uint8) 
    img[:,:,0]=r
    img[:,:,1]=g
    img[:,:,2]=b
    cv.imshow("iamge", img)
    cv.waitKey(0)
 
def create_seq(colorDic):
	img = np.zeros((512,512,3), np.uint8);
	i0 = 0;
	i1 = 0;
	size = 32;
	for i in range(len(colorDic)):
		if(i1 >= 512//size):
			print(i0,i1)
			i0 += 1;
			i1 = 0;
		curR = colorDic[i][0][0];
		curG = colorDic[i][0][1];
		curB = colorDic[i][0][2];
		img[i0*size:(i0+1)*size,i1*size:(i1+1)*size,0] = curR;
		img[i0*size:(i0+1)*size,i1*size:(i1+1)*size,1] = curG;
		img[i0*size:(i0+1)*size,i1*size:(i1+1)*size,2] = curB;
		i1 += 1;
		
		cv.imshow("image", img)
		cv.waitKey(0)
	cv.imshow("image", img)
	cv.waitKey(0)

def get_dominant_color(image):
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
    create_seq(colorDic);
    # for i in range(3):
    # 	cur = colorDic[i];
    # 	cur = cur[0];
    # 	create_image(cur[0],cur[1],cur[2])
    return dominant_color
 
 
if __name__ == '__main__':
    image = Image.open('taxi/5.png')
    img = cv.imread('taxi/5.png')
    cv.imshow("1",img);
    cv.waitKey(0)
    image = image.convert('RGB')
    
    print(get_dominant_color(image))