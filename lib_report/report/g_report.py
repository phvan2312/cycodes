# /use/bin/env python
# -*- coding: utf-8 -*-
"""
Input: [
    {
        'file_name': 'name of file',
        'key_name': 'key, field name, ...',
        '...',
    }
]
"""
from .base.report import BaseReport
from .tool.verify import Verification
import datetime


class GReport(BaseReport):
    global_index = 0
    output_dir = None
    output_path = None
    workbook = None
    worksheet = None
    freeze_panel_row = 1
    freeze_panel_col = 1
    is_verification = 0
    header_format = {
        'bold': 1,
        'border': 1,
        'align': 'center',
        'valign': 'vcenter',
        'fg_color': '#366092',
        'color': '#ffffff'
    }
    leftside_format = {
        'bold': 1,
        'border': 1,
        'align': 'center',
        'valign': 'vcenter',
        'fg_color': '#538DD5',
        'color': '#ffffff'
    }
    data_format = {
        'file_name': {'header': 'File Name', 'size': 30, 'index': 0, 'type': 'str'},
        'key_name': {'header': 'Item ID', 'size': 20, 'index': 1, 'type': 'str'},
        'data_type': {'header': 'Type', 'size': 10, 'index': 2, 'type': 'str'},
        'ocr': {'header': 'AI OCR', 'size': 30, 'index': 3, 'type': 'str'},
        'label': {'header': 'Correct Answer', 'size': 30, 'index': 4, 'type': 'str'},
        'img_path': {'header': 'Line Cut', 'size': 50, 'index': 5, 'type': 'img'},
    }
    default_col_height = 50

    def __init__(self, output_dir=None, is_appending_date=True, is_appending_img=True):
        super().__init__()
        if output_dir is not None:
            self.output_dir = output_dir

        self.cur_datetime = ''
        if is_appending_date is True:
            self.cur_datetime = datetime.datetime.now().strftime("%Y%m%d")
        self.is_appending_img = is_appending_img

    def add_worksheet(self, workbook, sheet_name="report"):
        worksheet = None
        if workbook is not None:
            if sheet_name is not None:
                worksheet = workbook.add_worksheet(name=sheet_name)
            else:
                cur_datetime = datetime.datetime.now().strftime("%Y%m%d")
                worksheet = workbook.add_worksheet(name="Worksheet_" + cur_datetime)
        return worksheet

    def append_header(self, workbook=None, worksheet=None):
        # Freeze table
        worksheet.freeze_panes(self.freeze_panel_row, self.freeze_panel_col)
        general_format = workbook.add_format()
        general_format.set_text_wrap(True)
        worksheet.set_default_row(self.default_col_height)
        cell_format = workbook.add_format(self.header_format)

        for key, item in self.data_format.items():
            worksheet.set_column(item['index'], item['index'], item['size'])
            worksheet.write(0, item['index'], item['header'], cell_format)

    def append_data(self, workbook=None, worksheet=None, data=[]):
        """
        :param workbook to write data on
        :param json_data: json data to write
        :return:
        """

        if worksheet is not None:
            self.append_header(workbook, worksheet)
            # Set data to row
            for index, item in enumerate(data):
                for key_name in item.keys():
                    if key_name in self.data_format.keys():
                        if self.data_format[key_name].get('type', 'str') in ['img', 'image']:
                            check_resize = self.resize_img(item[key_name], self.default_col_height)
                            if check_resize:
                                worksheet.insert_image(
                                    row=index + 1, col=self.data_format[key_name]['index'],
                                    filename=check_resize,
                                    options={
                                        'x_offset': 3,
                                        'y_offset': 3,
                                        'x_scale': 1,
                                        'y_scale': 1
                                    })
                        else:
                            if self.data_format[key_name]['index'] in [0]:
                                cell_format = workbook.add_format(self.leftside_format)
                            else:
                                cell_format = None

                            worksheet.write_string(index + 1, self.data_format[key_name]['index'],
                                                   item[key_name], cell_format)

        else:
            print('Worksheet is invalid')

    def verify(self, excel_file, measures=('L', 'F'), attributes=('File Name', 'Item ID', 'Type'),
               correct_dict=None, is_strip=False, is_normalize=False):
        verification = Verification()
        output_file = excel_file.replace('.xlsx', '_out.xlsx')
        verification.run(excel_file, output_file, measures=measures, attributes=attributes, correct_dict=correct_dict,
                         strip=is_strip, normalize=is_normalize)

    def save(self, data, file_name):
        file_name += self.cur_datetime
        excel_file = super().save(data, file_name)
        if self.is_verification:
            self.verify(excel_file)
        return excel_file
