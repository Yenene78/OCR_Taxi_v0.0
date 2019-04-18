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
import tempfile;
from pdf2image import convert_from_path;
 

# Gen Excel && Trans to pdf;
class genTables:
	fieldList = ["Change Request ID", "Description", "Material", "Material Type"];
	fieldDic = {"Change Request ID":[1,2,3,4,5], "Description":["test","LOL","hehe"], "Material":["MM1", "MM2"], "Material Type":["Type1", "Type2"]};

	def __init__(self):
		# generate as template;
		for i in range(int(input("Please input how many to generate? "))):
			self.readTem("tem.xlsx", str(i), "tem.txt");

	# Windows: excel -> other format;
	def exceltopdf(self, doc):
	    excel = client.DispatchEx("Excel.Application")
	    excel.Visible = 1

	    wb = excel.Workbooks.Open(doc)
	    ws = wb.Worksheets[0]
	    pdfPath = doc.strip("html");
	    # pdfPath = doc.strip("xls") + "html"; # FileFormat = 44
	    try:
	        wb.SaveAs(pdfPath, FileFormat=57);
	        return pdfPath + ".pdf";
	    except Exception as e:
	        print("Failed to convert");
	        print(e);
	    finally:
	        wb.Close()
	        excel.Quit()

	# generate simple tables;
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
				counter += 1;

		for i in range(3):
			row += 1;
			counter = 0;
			for x in self.fieldDic:
				if(x in use):
					fieldNum = random.randint(0, len(self.fieldDic[x])-1);
					sheet.write_merge(row, row, counter, counter+2, self.fieldDic[x][fieldNum]);
					counter += 1;
		book.save(fileName);
		html_list, html_file = ReportImage.excel_html(fileName, "tmp/")
		workpath = os.getcwd();
		pdfName = self.exceltopdf(str(workpath)+ "/" + html_file);
		self.pdfToPng(pdfName);

	def pdfToPng(self, fileName):
		with tempfile.TemporaryDirectory() as path:
			images = convert_from_path(fileName);
			for i, img in enumerate(images):
				img.save(fileName.strip("pdf") + "png");

	# generate tables by templates;
	def readTem(self, temPath, fileName, temDic = fieldDic):
		# input;
		book = xlrd.open_workbook(temPath);
		sheet = book.sheet_by_index(0);
		style = xlwt.XFStyle();
		# set Borders:
		borders = xlwt.Borders();
		borders.left = xlwt.Borders.THIN;
		borders.right = 1;
		borders.top = 1;
		borders.bottom = 1;
		borders.bottom_colour=0x3A;
		style.borders = borders;
		# set Wrap:
		alignment = xlwt.Alignment();
		alignment.wrap = xlwt.Alignment.WRAP_AT_RIGHT;
		style.alignment = alignment;
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

		# fulfil;
		merge = {};
		for x in sheet.merged_cells:
			merge[str(x[0])+","+str(x[2])] = [x[1], x[3]];
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
							val = random.randint(10, 99);
					else:
						val = "None";
				elif(val == "#"):
					key = str(self.searchField(sheet.col_values(j)[:i][::-1]));
					if(key in temDic):
						coin = random.randint(0, len(temDic[key])-1);
						val = temDic[key][coin];
						if(val == "#"):
							val = random.randint(10, 99);
					else:
						val = "None";
				if(pos in merge):
					sheet1.write_merge(i,w-1,j,h-1, str(val), style);
				else:
					for x in sheet.merged_cells:
						if(i in range(x[0], x[1])) and (j in range(x[2], x[3])):
							continue;
						else:
							sheet1.write(i,j,val, style)
		book1.save(fileName + ".xls");
		workpath = os.getcwd();
		pdfName = self.exceltopdf(str(workpath)+ "\\" + fileName);
		self.pdfToPng(pdfName);


	# find Field of current block;
	def searchField(self, tar):
		for x in tar:
			if(x != "") and (x not in ["#","*"]):
				return x;
		return -1;


if(__name__ == "__main__"):
	genTables();

