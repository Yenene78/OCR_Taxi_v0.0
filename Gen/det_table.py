import cv2
import numpy as np 
import matplotlib.pyplot as plt

class detTable:
    def __init__(self):
        pass;
        
    def get(self, imgPath):
        img = cv2.imread(imgPath)
        # img = cv2.resize(img, (int(img.shape[1]*0.75), int(img.shape[0]*0.75)), interpolation=cv2.INTER_CUBIC) 
        bboxes = self.genBBoxes(img)
        print(bboxes);
        return bboxes;

    def make_similar_same(self, pts, idx):
        ps = pts[:,idx]
        pts_keys = np.unique(ps)
        i=0
        while i <len(pts_keys):
            key = pts_keys[i]
            a = key-2<ps
            b = key+2>ps
            c = a*b
            ps[c] = key
            pts_keys = np.unique(ps)
            i+=1
        pts[:,idx] = ps
        return pts

    def merge_pts(self, pts):
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
        x1,y1 = pt1
        x2,y2 = pt2
        line = lines[x1:x2+1,y1:y2+1]
        line = line.squeeze()
        assert len(line.shape)==1
        return ((line==255).sum()/line.shape[0])>0.95

    def org_pts_by_x(self, pts):
        keys = np.unique(pts[:,0])
        pts_ = {}
        for key in keys:
            vals = pts[pts[:,0]==key,1]
            pts_[key] = np.array(sorted(vals))
        return pts_

    def org_pts_by_y(self, pts):
        keys = np.unique(pts[:,1])
        pts_ = {}
        for key in keys:
            vals = pts[pts[:,1]==key,0]
            pts_[key] = np.array(sorted(vals))
        return pts_

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
            j,k=0,0
            j = int(np.where(pts_same_rows==y)[0])
            k = int(np.where(pts_same_cols==x)[0])
            row=j+1
            col=k+1
            flag = False    
            for j in range(row,len(pts_same_rows)):
                y1 = pts_same_rows[j]
                if not self.is_line((x,y),(x,y1),merge):
                    break
                for k in range(col,len(pts_same_cols)):                
                    x1 = pts_same_cols[k]
                    if not self.is_line((x,y),(x1,y),merge):
                        flag = True
                        break
                    if self.is_line((x1,y),(x1,y1),merge) and self.is_line((x,y1),(x1,y1),merge):
                        flag = True
                        # count+=1
                        bbox.append((x,y,x1,y1))
                        break
                if flag:
                    break               
        return bbox
            
    def imshow(self, img,info):
        # pass
        cv2.namedWindow(info,0);
        cv2.resizeWindow(info, 640, 480);
        cv2.imshow(info,img)       
        cv2.waitKey(0)

    def is_same_pt(self,pt1,pt2):
        #threshold depending on linewidth and size of minimum cell
        return abs(pt1[0]-pt2[0])< 3 and abs(pt1[1]-pt2[1]) < 3


    def genBBoxes(self, img):
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        binary = cv2.adaptiveThreshold(~gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 15, -10)
        # cv2.imshow("cell", binary) 
        # cv2.waitKey(0)
        h,w =binary.shape
        scale = 20 
        #maximum number of cells in different directions
        kernel  = cv2.getStructuringElement(cv2.MORPH_RECT,(w//scale,1))
        #w//scale = minimum horizonal line length
        eroded = cv2.erode(binary,kernel,iterations = 1)
        dilatedcol = cv2.dilate(eroded,kernel,iterations = 1)
        #imshow(dilatedcol,"horizonal lines")
        kernel  = cv2.getStructuringElement(cv2.MORPH_RECT,(1,h//scale))
        #h//scale = minimum vertical line length
        eroded = cv2.erode(binary,kernel,iterations = 1)
        dilatedrow = cv2.dilate(eroded,kernel,iterations = 1)
        #imshow(dilatedrow,"vertical lines")

        #标识交点
        bitwiseAnd = cv2.bitwise_and(dilatedcol,dilatedrow)    
        self.imshow(bitwiseAnd,'cross point')
        #标识表格
        merge = cv2.add(dilatedcol,dilatedrow)
        self.imshow(merge,'table')
        
        x,y = np.where(bitwiseAnd==255)
        pts = np.array([x,y]).T
        pts = self.merge_pts(pts)
        bboxes = self.pts_to_box(pts,merge)
        img_ = np.zeros_like(bitwiseAnd)
        for bbox in bboxes:
            x1,y1,x2,y2 = bbox
            img_[x1:x2+1,y1] = 255
            img_[x1:x2+1,y2] = 255
            img_[x1,y1:y2+1] = 255
            img_[x2,y1:y2+1] = 255
        self.imshow(img_,'my result')

        
        return bboxes

if(__name__ == "__main__"):
    d = detTable();
    d.get("0.png");

