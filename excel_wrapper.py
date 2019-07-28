import xlsxwriter
import string

import numpy as np
from PIL import Image

def insert_image_worksheet(worksheet, img_path, index, col_index, scale=3, positioning=2):
    img = np.array(Image.open(img_path))
    height = img.shape[0]
    worksheet.insert_image(scale * index - scale + 1, col_index, img_path, {
        'x_offset': 2, 'y_offset': 20,
        # 'x_scale': 20.0/height, 'y_scale': 20.0/height,
        'x_scale': scale * 18.0 / height, 'y_scale': scale * 18.0 / height,
        'positioning': positioning
    })

class ExcelWrapper:
    def __init__(self, excel_out_fn, fixed_row_height=50):
        self.workbook = xlsxwriter.Workbook(excel_out_fn)
        self.fixed_row_height = fixed_row_height
        self.dct_worksheets = {}

    def close(self):
        self.workbook.close()

    def add_work_sheet(self, sheet_name):
        worksheet = self.workbook.add_worksheet()
        self.dct_worksheets[sheet_name] = worksheet

    def add_column(self, index_column, sheet_name, datas, title_name, column_width = 40, is_image=False):
        """
        :param index_column: index 0 ->
        :param sheet_name:
        :param datas:
        :return:
        """

        upper_cases = list(string.ascii_uppercase)
        index_character = upper_cases[index_column]

        worksheet = self.dct_worksheets[sheet_name]
        worksheet.set_column('%s:%s' % (index_character, index_character), column_width)

        # write title
        worksheet.write(0, index_column, title_name)

        index = 1
        scale = 1
        for data in datas:
            worksheet.set_row(index, 50)

            if not is_image:
                worksheet.write("%s%d" % (index_character, index + 1), data)
            else:
                insert_image_worksheet(worksheet, data, index, col_index=index_column, scale=scale)

            index += 1



