#encoding: utf-8
import cv2
import numpy as np
 
class Roi_solve:
	def __init__(self,rect): 
		self.rect = rect  #所有矩形框
		self.cursor = -1 #初始化游标位置  
		self.rect_num = len(rect) #记录rect的实时数量
	def next(self):  
		#将游标的位置前移一步，并返回所在检索位的矩形框
		self.cursor = self.cursor+1  
		return self.rect[self.cursor]
	def hasNext(self):  
		#判断是否已经检查完了所有矩形框 
		return self.rect_num > self.cursor + 1
	def remove(self,flag = -1):  
		#将非优解从数据集删除
		if flag == -1:
			del self.rect[self.cursor]
			#删除当前游标位置，游标回退一步  
			self.cursor = self.cursor-1  
		else:
			#删除后面位置的rect，游标不动
			del self.rect[flag]
		#rect数量，减1  
		self.rect_num = self.rect_num - 1
	def add(self,add_rect):
		self.rect.append(add_rect)
		self.rect_num = self.rect_num + 1
	def get_u_d_l_r(self,rect_):
		#获取rect的上下左右边界值
		upper_,down_ = rect_[1],rect_[1] + rect_[3]
		left_,right_ = rect_[0],rect_[0] + rect_[2]
		return upper_,down_,left_,right_
	def is_intersect(self,y01, y02 , x01, x02, y11, y12 , x11, x12):  
		# 判断两个矩形是否相交    
		lx = abs((x01 + x02) / 2 - (x11 + x12) / 2)  
		ly = abs((y01 + y02) / 2 - (y11 + y12) / 2)  
		sax = abs(x01 - x02)  
		sbx = abs(x11 - x12)  
		say = abs(y01 - y02)  
		sby = abs(y11 - y12)  
		if lx <= (sax + sbx) / 2 and ly <= (say + sby) / 2:  
			return True
		else:  
			return False
	def intersect_area(self,y01, y02 , x01, x02, y11, y12 , x11, x12): 
		#返回两个rect的交叉面积 
		col=min(x02,x12)-max(x01,x11)  
		row=min(y02,y12)-max(y01,y11)  
		return col*row  
	def intersect_height(self,y01, y02, y11, y12): 
		#height轴方向交叉，返回height交叉段占比
		row=float(min(y02,y12)-max(y01,y11))   
		return max(row/float(y02-y01),row/float(y12-y11))

	#remove_inside：如果“本rect”被“其他rect”包围了，则删除
	def remove_inside(self,rect_curr):
		#获取当前rect的上下左右边界信息  
		u_curr,d_curr,l_curr,r_curr = self.get_u_d_l_r(rect_curr)
		#判断当前rect是否在内部
		for rect_ in self.rect:
			u_,d_,l_,r_ = self.get_u_d_l_r(rect_)		
			if u_curr>u_ and d_curr<d_ and l_curr>l_ and r_curr<r_:  
				self.remove()
				break
	#remove_overlop：如果“本rect”和“其他rect”相交区域达到了95%以上，则删除
	def remove_overlop(self,rect_curr):
		#获取当前rect的上下左右边界信息  
		u_curr,d_curr,l_curr,r_curr = self.get_u_d_l_r(rect_curr)
		area_curr = rect_curr[2] * rect_curr[3]
		#判断当前rect是否在内部
		for rect_ in self.rect:
			u_,d_,l_,r_ = self.get_u_d_l_r(rect_)	
			if self.is_intersect(u_curr,d_curr,l_curr,r_curr,u_,d_,l_,r_): 
				if rect_ == rect_curr:
					continue
				else :
					area_ = self.intersect_area(u_curr,d_curr,l_curr,r_curr,u_,d_,l_,r_)
				if float(area_)/float(area_curr) >0.95:
					self.remove()
					break
	#如果“两个rect”在同一水平面上，横向坐标
	def merge(self,rect_curr):
		#获取当前rect的上下左右边界信息  
		u_curr,d_curr,l_curr,r_curr = self.get_u_d_l_r(rect_curr)
		#判断当前rect是否在内部
		for i in range(self.cursor+1,len(self.rect)):
			# printi,self.cursor+1,len(self.rect)
			rect_ = self.rect[i]
			u_,d_,l_,r_ = self.get_u_d_l_r(rect_)	
			#判断是否相交	
			if self.is_intersect(u_curr,d_curr,l_curr,r_curr,u_,d_,l_,r_): 
				if self.intersect_height(u_curr,d_curr,u_,d_) > 0.6:
					if rect_curr[2] > rect_[2]:
						new_rect = np.array(rect_curr)
					else:
						new_rect = np.array(rect_)
					new_l = min(l_curr,l_)
					new_r = max(r_curr,r_)
					new_rect[0] = new_l
					new_rect[2] = new_r-new_l
					self.remove(i)
					self.remove()
					self.add(new_rect)
					break
	def rm_inside(self): 
		self.cursor = -1 
		while(self.hasNext()):  
			rect_curr = self.next()  
			self.remove_inside(rect_curr)
		return self.rect
	def rm_overlop(self):
		self.cursor = -1
		while(self.hasNext()):  
			rect_curr = self.next()  
			self.remove_overlop(rect_curr)
		return self.rect
	def merge_roi(self):
		self.cursor = -1
		while(self.hasNext()):  
			rect_curr = self.next()  
			self.merge(rect_curr)
		return self.rect