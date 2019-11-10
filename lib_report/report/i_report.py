# /use/bin/env python
# -*- coding: utf-8 -*-
"""
Input: [
    {
        'file_name': 'name of file',
        '...',
        'fields': [
            {...}
        ]
    }
]
"""
from .base.report import BaseReport
import datetime


class IReport(BaseReport):
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
    normal_col_format = {
        'bold': 1,
        'border': 1,
        'align': 'center',
        'valign': 'vcenter',
    }
    error_col_format = {
        'bold': 1,
        'border': 1,
        'align': 'center',
        'valign': 'vcenter',
        'fg_color': 'red'
    }
    default_col_height = 25
    freeze_panel_row = 2
    freeze_panel_col = 2

    def __init__(self, output_dir=None, is_appending_date=True, is_appending_img=True):
        super().__init__(output_dir)
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

    def append_header(self, workbook=None, worksheet=None, data_format={}):
        # Freeze table by row and col
        worksheet.freeze_panes(self.freeze_panel_row, self.freeze_panel_col)
        # Set default height of row
        worksheet.set_default_row(self.default_col_height)

        fields = data_format.get('fields')
        merge_format = workbook.add_format(self.header_format)
        for index, name in enumerate(data_format.keys()):
            if name != 'fields':
                worksheet.merge_range(0, index, 1, index, name, merge_format)
            else:
                for idx, key_name in enumerate(fields.keys()):
                    last_col = len(fields[key_name])
                    sub_fields = fields[key_name].keys()
                    worksheet.merge_range(0, (idx * last_col) + index,
                                          0, (idx * last_col) + index + last_col - 1,
                                          key_name, merge_format)
                    for sub_idx, sub_key_name in enumerate(sub_fields):
                        worksheet.write_string(1, (idx * last_col) + index + sub_idx,
                                               sub_key_name, merge_format)

    def append_data(self, workbook=None, worksheet=None, data=[]):
        data_format = self.get_largest(data)
        if worksheet is not None:
            self.append_header(workbook, worksheet, data_format)
            # Set data to row
            for index, item in enumerate(data):
                for idx, name in enumerate(item.keys()):
                    val = item[name]
                    if name != 'fields':
                        val, col_format = self.get_value(val)
                        if idx in [0]:
                            col_format = self.leftside_format

                        worksheet.write(index + 2, idx, val, workbook.add_format(col_format))
                    else:
                        for sub_idx, key_name in enumerate(val.keys()):
                            last_col = len(val[key_name])
                            sub_fields = val[key_name]
                            for sub_sub_idx, sub_key_name in enumerate(sub_fields.keys()):
                                value, col_format = self.get_value(sub_fields[sub_key_name])
                                worksheet.write(index + 2,
                                                (sub_idx * last_col) + idx + sub_sub_idx,
                                                value, workbook.add_format(col_format))

        else:
            print('Worksheet is invalid')

    @staticmethod
    def get_largest(x):
        """
        GET a dict largest of data to use in header of excel file
        """
        max = x[0] if len(x) > 0 else {}
        for index, k in enumerate(x):
            if 'fields' in k:
                if len(max.get('fields').keys()) < len(k.get('fields').keys()):
                    max = k

        return max

    def get_value(self, val):
        col_format = self.normal_col_format
        return val, col_format

    def save(self, data, file_name):
        file_name += self.cur_datetime
        super().save(data, file_name)
