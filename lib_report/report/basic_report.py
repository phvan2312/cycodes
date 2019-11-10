# /usr/bin/env python
# -*- coding: utf-8 -*-
from .base.report import BaseReport

BASIC_HEADER_FORMAT = {
    'bold': 1,
    'border': 1,
    'align': 'center',
    'valign': 'vcenter',
    'fg_color': '#366092',
    'color': '#ffffff'
}


class BasicReport(BaseReport):
    global_index = 0
    output_dir = None
    output_path = None
    workbook = None
    worksheet = None
    default_col_height = 30
    freeze_panel_row = 1
    freeze_panel_col = 1

    data_format = {
        'data_key_A': {'header': 'COLUMN_A', 'size': 30, 'index': 0, 'type': 'str'},
        'data_key_B': {}
    }
    is_data_format_set = 0

    def __init__(self, output_dir=None):
        super().__init__()
        if output_dir is not None:
            self.output_dir = output_dir
        else:
            print('Warning: you not set output dir so report will be on current folder!')

        print('You are creating new Report instance, '
              'you may want to set its data format with .set_data_format(data_format)')
        print('Example data format: \n {}'.format(self.data_format))

    def add_worksheet(self, workbook, sheet_name='Sheet 1'):
        self.workbook = workbook
        self.worksheet = self.workbook.add_worksheet(name=sheet_name)

    def format_header(self, header_format=BASIC_HEADER_FORMAT):
        self.workbook.add_format().set_text_wrap(True)
        self.worksheet.freeze_panes(self.freeze_panel_row, self.freeze_panel_col)
        self.worksheet.set_default_row(self.default_col_height)
        cell_format = self.workbook.add_format(header_format)

        for i, (key, item) in enumerate(self.data_format.items()):
            self.worksheet.set_column(item.get('index', i), item.get('index', i), item.get('size', 30))
            self.worksheet.write(0, item.get('index', i), item.get('header', key), cell_format)

    def set_data_format(self, data_format):
        self.data_format = data_format
        self.is_data_format_set = 1
        print('Current data format: \n {}'.format(data_format))

    def check_keys_with_data_format(self, keys):
        if not self.is_data_format_set:
            print("You haven't set the data format for report, so it will automatically make a simple format:")
            data_format = {
                key: {'index': i, 'header': key} for i, key in enumerate(keys)
            }
            self.set_data_format(data_format)
            print("If result is not as you expected, please try to set data format with .set_data_format(your_format)")

        data_format_keys = list(self.data_format.keys())
        setting_keys = []
        for key in keys:
            if key not in data_format_keys:
                print('Warning: Key `{}` is not set in the report data format, its will not show in report!')
            else:
                setting_keys.append(keys)

        if len(setting_keys) < 3:
            raise ValueError('Too less data keys ({}) is set on data format, please re-check'.format(setting_keys))

        self.format_header()

    def get_col_index(self, key_name):
        if key_name in self.data_format and 'index' in self.data_format[key_name]:
            return self.data_format[key_name]['index']
        elif key_name in self.data_format:
            return list(self.data_format.keys()).index(key_name)
        else:
            raise ValueError('Try to work on key not in data format!')

    def append_data(self, data=(), *args, **kwargs):
        if len(data) == 0:
            return
        # check data:
        keys = list(data[0].keys())
        self.check_keys_with_data_format(keys)
        for i, row in enumerate(data):
            for col in row.keys():
                if col in self.data_format.keys():
                    if self.data_format[col].get('type', 'str') in ['img', 'image']:
                        check_resize = self.resize_img(row[col], self.default_col_height)
                        if check_resize:
                            self.worksheet.insert_image(
                                row=i + 1,
                                col=self.get_col_index(col),
                                filename=check_resize,
                                options={
                                    'x_offset': 3,
                                    'y_offset': 3,
                                    'x_scale': 1,
                                    'y_scale': 1
                                })
                    else:
                        if isinstance(row[col], list):
                            for j, _ in enumerate(row[col]):
                                self.worksheet.write_string(i + 1, self.get_col_index(col) + j, _)
                        else:
                            self.worksheet.write_string(i + 1, self.get_col_index(col), row[col])

    def save(self, data, file_name):
        return super().save(data, file_name)