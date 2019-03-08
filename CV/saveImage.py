import cv2
import os.path
import datetime as d

class SaveImage():
	def __init__(self, img_):
		path = str(input("Please Input the SavePath: "))
		if not (os.path.exists(path)):
			os.makedirs(dirs)		
		imgName = "\\result_"+str(d.datetime.now().strftime("%Y%m%d%H%M%S"))+".png"
		self.saveImage(img_, path + imgName)
	
	# Save Image;
	def saveImage(self, img, savepath):
		print(savepath)
		cv2.imwrite(savepath, img)