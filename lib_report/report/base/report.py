# /usr/bin/env python
# -*- coding: utf-8 -*-
import os
import xlsxwriter
import traceback
from PIL import Image


class BaseReport(object):
    output_dir = ''

    def __init__(self, output_dir=''):
        self.output_dir = output_dir

    def add_worksheet(self, *args, **kwargs):
        pass

    def format_header(self, *args, **kwargs):
        pass

    def append_header(self, *args, **kwargs):
        pass

    def append_data(self,  *args, **kwargs):
        pass

    def save(self, data, file_name):
        output_path = os.path.join(self.output_dir, file_name + ".xlsx")
        workbook = xlsxwriter.Workbook(output_path)
        worksheet = self.add_worksheet(workbook=workbook)
        self.append_data(data=data, workbook=workbook, worksheet=worksheet)
        workbook.close()

        print("***********SUCCESSFULLY EXPORT SINGLE FILE REPORT*************")
        return output_path

    @staticmethod
    def resize_img(img_path, max_height=50):
        try:
            im = Image.open(img_path)
            if im.size[1] > max_height:
                wpercent = int(float(im.size[0]) * 20 / 100)
                hpercent = int(float(im.size[1]) * 20 / 100)
                im = im.resize((wpercent, hpercent), Image.ANTIALIAS)
                _, ext = os.path.splitext(img_path)
                resize_img_path = _ + '_resized.' + ext
                im.save(resize_img_path)
                return resize_img_path
        except IOError:
            traceback.print_exc()
            return False
