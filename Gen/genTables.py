# -*- coding: utf-8 -*-
import xlwt;
import xlrd;
import random;
import time;
import pandas as pd;
import codecs;
import os;
from win32com import client;
import win32api;
 
#__author__ = 'YangXin'
# ReportImage -> report convert include multiple sheets into pictures
class ReportImage:
    def __init__(self):
        pass;

    @staticmethod
    def excel_html(excel_file, html_path):
        html_list = []
        excel_obj = pd.ExcelFile(excel_file)
        sheet_list = excel_obj.sheet_names
        index = 0
        for i in sheet_list:
            html_file = html_path + excel_file.strip("xls") + "html"
            excel_data = excel_obj.parse(excel_obj.sheet_names[index])
            with codecs.open(html_file, 'w', 'utf-8') as html:
                html.write(excel_data.to_html(header=True, index=True))
            html_list.append(html_file)
            index += 1;
        return html_list, html_file

# Gen Excel && Trans to pdf;
class genTables:
	fieldList = ["Change Request ID", "Description", "Material", "Material Type"];
	fieldDic = {"Change Request ID":[1,2,3,4,5], "Description":["test","LOL","hehe"], "Material":["MM1", "MM2"], "Material Type":["Type1", "Type2"]};

	def __init__(self):
		self.readTem("tem.xlsx", "tem.txt");
		# for i in range(10):
		# 	self.genSimExcel(str(i)+".xls");

	def exceltopdf(self, doc):
	    excel = client.DispatchEx("Excel.Application")
	    excel.Visible = 0

	    wb = excel.Workbooks.Open(doc)
	    ws = wb.Worksheets[0]
	    pdfPath = doc.strip("html") + 'pdf';
	    try:
	        wb.SaveAs(pdfPath, FileFormat=57)
	    except Exception as e:
	        print("Failed to convert");
	        print(e);
	    finally:
	        wb.Close()
	        excel.Quit()

	def genSimExcel(self, fileName):
		counter = 0;
		row = 0;
		use = [];
		book = xlwt.Workbook(encoding="utf-8", style_compression=0);
		sheet = book.add_sheet("test", cell_overwrite_ok=True);
		for x in self.fieldList:
			fieldNum = random.randint(0, 1);
			if(fieldNum == 1):
				sheet.write_merge(row, row, counter, counter+2, x);
				use.append(x);
				print(x);
				counter += 1;

		for i in range(3):
			row += 1;
			counter = 0;
			for x in self.fieldDic:
				if(x in use):
					fieldNum = random.randint(0, len(self.fieldDic[x])-1);
					sheet.write_merge(row, row, counter, counter+2, self.fieldDic[x][fieldNum]);
					# sheet.write(row, counter, fieldDic[x][fieldNum]);
					counter += 1;
		print(fileName);
		book.save(fileName);
		html_list, html_file = ReportImage.excel_html(fileName, "tmp/")
		workpath = os.getcwd();
		self.exceltopdf(str(workpath)+ "/" + html_file);

	def readTem(self, temPath, temDic = fieldDic):
		# input;
		book = xlrd.open_workbook(temPath);
		sheet = book.sheet_by_index(0);
		# output;
		book1 = xlwt.Workbook(encoding="utf-8", style_compression=0);
		sheet1 = book1.add_sheet("test", cell_overwrite_ok=True);
		if(temDic != self.fieldDic):
			f = open(temDic);
			line = f.readline();
			dic = {};
			while line:
				line = line.replace("\n", "");
				line = line.split(":");
				dic[line[0]] = line[1].split(" ");
				line = f.readline();
			f.close;
		temDic = dic;

		print(sheet.merged_cells)
		merge = {};
		for x in sheet.merged_cells:
			merge[str(x[0])+","+str(x[2])] = [x[1], x[3]];
		print(merge)

		for i in range(0, sheet.nrows):
			rowValues= sheet.row_values(i);
			for j in range(len(rowValues)):
				pos = str(i)+","+str(j);
				val = "-1";
				if(pos in merge):
					w = merge[pos][0];
					h = merge[pos][1];
					
					for i1 in range(i, w):
						for j1 in range(j, h):
							if(sheet.cell_value(i1,j1)):
								val = sheet.cell_value(i1,j1);
								break;
				else:
					val = sheet.cell_value(i,j);
				if(val == "*"):
					key = str(self.searchField(sheet.row_values(i)[:j][::-1]));
					if(key in temDic):
						coin = random.randint(0, len(temDic[key])-1);
						val = temDic[key][coin];
						if(val == "#"):
							val = random.randint(0, 100);
					else:
						val = "None";
				elif(val == "#"):
					key = str(self.searchField(sheet.col_values(j)[:i][::-1]));
					if(key in temDic):
						coin = random.randint(0, len(temDic[key])-1);
						val = temDic[key][coin];
						if(val == "#"):
							val = random.randint(0, 100);
					else:
						val = "None";

				if(pos in merge):
					sheet1.write_merge(i,w-1,j,h-1, val);
				else:
					sheet1.write(i,j,val)
		print(temDic);
		book1.save("test.xls");

	def searchField(self, tar):
		for x in tar:
			if(x != "") and (x not in ["#","*"]):
				return x;
		return -1;


if(__name__ == "__main__"):
	genTables();

