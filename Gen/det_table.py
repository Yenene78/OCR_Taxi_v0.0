import cv2
import numpy as np 
import matplotlib.pyplot as plt

class detTable:
    def __init__(self):
        pass
        
    def get(self, imgPath):
        img = cv2.imread(imgPath)
        bboxes = self.gen_bboxes(img)
        return bboxes

    def make_similar_same(self, pts, idx):
        '''merge the points into the uniform coords'''
        ps = pts[:,idx]
        pts_keys = np.unique(ps)
        i=0
        while i <len(pts_keys):
            key = pts_keys[i]
            ids = (key<=ps)*(key+3>=ps)
            vs = ps[ids]
            key = int(np.median(vs))
            ps[ids] = key
            pts_keys = np.unique(ps)
            i+=1
        pts[:,idx] = ps
        return pts

    def merge_pts(self, pts):
        '''merge the same crosspoints'''
        pts=self.make_similar_same(pts,0)
        pts=self.make_similar_same(pts,1)
        new_pts = []
        for pt in pts:
            for key in new_pts:
                if self.is_same_pt(pt,key):
                    break
            else:
                new_pts.append(pt)
        return np.array(new_pts)
    def is_line(self,pt1,pt2,lines):
        '''if the points is a line in th pics'''
        #threshold tbd
        cols,rows = lines
        x1,y1 = pt1
        x2,y2 = pt2
        if x1==x2:
            line = cols[x1-3:x2+3,y1-2:y2+2].max(0)
        elif y1==y2:
            line = rows[x1-2:x2+2,y1-3:y2+3].max(1)     
        line = line.squeeze()
        assert len(line.shape)==1
        return ((line==255).sum()/line.shape[0])>=0.5

    def org_pts_by_x(self, pts):
        '''orgnize points according to their x coords''' 
        keys = np.unique(pts[:,0])
        pts_dict = {}
        for key in keys:
            vals = pts[pts[:,0]==key,1]
            pts_dict[key] = np.array(sorted(vals))
        return pts_dict

    def org_pts_by_y(self, pts):
        '''orgnize points according to their y coords''' 
        keys = np.unique(pts[:,1])
        pts_dict = {}
        for key in keys:
            vals = pts[pts[:,1]==key,0]
            pts_dict[key] = np.array(sorted(vals))
        return pts_dict

    def pts_to_box(self, pts,merge):
        pts_x = self.org_pts_by_x(pts)
        pts_y = self.org_pts_by_y(pts)
        bbox = []
        length = pts.shape[0]
        for i in range(length):
            x,y = pts[i]        
            pts_same_rows = pts_x[x]
            pts_same_cols = pts_y[y]
            if y == pts_same_rows.max():
                #on the border
                continue
            elif x == pts_same_cols.max():
                #on the border
                continue
            row_start = int(np.where(pts_same_rows==y)[0])+1
            col_start = int(np.where(pts_same_cols==x)[0])+1
            flag = False    
            for row in range(row_start,len(pts_same_rows)):
                y1 = pts_same_rows[row]
                if not self.is_line((x,y),(x,y1),merge):
                    break
                for col in range(col_start,len(pts_same_cols)):                
                    x1 = pts_same_cols[col]
                    if not self.is_line((x,y),(x1,y),merge):
                        flag = True
                        break
                    if self.is_line((x1,y),(x1,y1),merge) and self.is_line((x,y1),(x1,y1),merge):
                        flag = True
                        bbox.append((x,y,x1,y1))
                        break
                if flag:
                    break               
        return bbox

    def is_same_pt(self,pt1,pt2):
        ''' if the pts representing the same crosspoint'''
        #threshold depending on linewidth and size of minimum cell
        return abs(pt1[0]-pt2[0])< 3 and abs(pt1[1]-pt2[1]) < 3


    def gen_bboxes(self, img):
        '''generate bounding boxes'''
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        binary = cv2.adaptiveThreshold(~gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 15, -10)
        h,w =binary.shape
        scale = 30 
        #maximum number of cells in different directions
        kernel  = cv2.getStructuringElement(cv2.MORPH_RECT,(w//scale,1))
        #w//scale = minimum horizonal line length
        eroded = cv2.erode(binary,kernel,iterations = 1)
        dilatedcol = cv2.dilate(eroded,kernel,iterations = 1)
        kernel  = cv2.getStructuringElement(cv2.MORPH_RECT,(1,h//scale))
        #h//scale = minimum vertical line length
        eroded = cv2.erode(binary,kernel,iterations = 1)
        dilatedrow = cv2.dilate(eroded,kernel,iterations = 1)

        #标识交点
        bitwiseAnd = cv2.bitwise_and(dilatedcol,dilatedrow)    
        #标识表格
        merge = cv2.add(dilatedcol,dilatedrow)
        
        x,y = np.where(bitwiseAnd==255)
        pts = np.array([x,y]).T
        pts = self.merge_pts(pts)
        bboxes = self.pts_to_box(pts,[dilatedcol,dilatedrow])    
        return bboxes
    def is_adjant(self,box1,box2):
        '''if the boxes are adjant'''
        flag1,flag2 = False,False
        if box1[0] >= box2[0] and box1[0] <= box2[2]:
            flag1 = True
        if box1[1] >= box2[1] and box1[1] <= box2[3]:
            flag2 = True
        if box1[2] >= box2[0] and box1[2] <= box2[2]:
            flag1 = True
        if box1[3] >= box2[1] and box1[3] <= box2[3]:
            flag2 = True
        return flag1 and flag2
    def in_bbox(self,box1,box2):
        '''if box2 in box1'''
        x1,y1,x2,y2 = box1
        xmin,ymin,xmax,ymax = box2
        return x1>=xmin and y1>=ymin and x2<=xmax and y2<=ymax
    def divide_bboxes_into_groups(self,bboxes):
        '''divide boxes of different tables into groups'''
        tables = {}
        for bbox in bboxes:
            match = []
            x1,y1,x2,y2 = bbox
            for key in tables.keys():
                if self.is_adjant(bbox,key):
                    match.append(key)
            if len(match)==0:
                tables[tuple(bbox)] = [bbox]
            else:
                key = match[0]
                new_key = (min(x1,key[0]),min(y1,key[1]),max(x2,key[2]),max(y2,key[3]))
                new_boxes = tables[key].copy()
                new_boxes.append(bbox)
                del(tables[key])
                for key in match[1:]:
                    x1,y1,x2,y2 = new_key
                    new_key = (min(x1,key[0]),min(y1,key[1]),max(x2,key[2]),max(y2,key[3]))
                    new_boxes += tables[key].copy()
                    del(tables[key])
                tables[new_key] = new_boxes
        return tables


if(__name__ == "__main__"):
    d = detTable()
    bboxes = d.get("0.png")
    print(len(bboxes))
    tables = d.divide_bboxes_into_groups(bboxes)
    print(list(tables.keys()))

    

