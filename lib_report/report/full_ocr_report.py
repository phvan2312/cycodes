import xlsxwriter
import os
import json
import collections
from PIL import Image
from .tool.matching import check_overlap
from .tool.accuracy import calculate_accuracy_by_char2
from .tool.merge_cell import get_lines, merge_cell
from .basic_report import BasicReport


def report_line(predicted_json, report_file):
    data = []
    for file in predicted_json:
        predicted_pages = get_lines(predicted_json[file])
        for page in predicted_pages:
            page_result = predicted_pages[page]
            for line in page_result:
                data.append({
                    'FILE': file,
                    'PAGE': page,
                    'LINE': line,
                    'OCR': [item['text'] for item in page_result[line]]
                })
    return BasicReport(os.path.dirname(report_file)).save(data, os.path.basename(report_file))


def make_report_no_image(predicted_json, report_file):
    """Run all image paths and calculate accuracy by field"""
    count = 0
    workbook = xlsxwriter.Workbook(report_file)
    worksheet = workbook.add_worksheet(name='OCR')

    for image_id in predicted_json:
        predicted = get_lines(predicted_json[image_id])
        max_col = 0
        page_max_row = {}
        for page in predicted:
            page_max_row[page] = 0
            for line in predicted[page]:
                worksheet.write_string(count, max_col, image_id)
                worksheet.write_string(count, max_col + 1, page)
                worksheet.write_string(count, max_col + 2, line)
                col = max_col + 2
                for item in predicted[page][line]:
                    col += 1
                    worksheet.write_string(count, col, item['text'])
                count += 1
                page_max_row[page] += 1
    workbook.close()
    return report_file


def make_report_attach_image(predicted_json, image_paths, report_file):
    """Run all image paths and calculate accuracy by field"""
    count = 0
    workbook = xlsxwriter.Workbook(report_file)
    worksheet = workbook.add_worksheet(name='OCR')

    for image_id in predicted_json:
        predicted = get_lines(predicted_json[image_id])
        max_row = 45
        max_col = 10
        page_max_row = {}
        for page in predicted:
            page_max_row[page] = 0
            for line in predicted[page]:
                worksheet.write_string(count, max_col, image_id)
                worksheet.write_string(count, max_col + 1, page)
                worksheet.write_string(count, max_col + 2, line)
                col = max_col + 2
                for item in predicted[page][line]:
                    col += 1
                    worksheet.write_string(count, col, item['text'])
                count += 1
                page_max_row[page] += 1
            count = max(count, count - page_max_row[page] + max_row)
        row = 0
        for page in predicted:
            img = Image.open(image_paths[image_id][page])
            width, height = img.size

            cell_width = worksheet.default_col_pixels
            cell_height = worksheet.default_row_pixels
            # cell_width = worksheet.col_sizes[0]
            # cell_height = worksheet.row_sizes[0]
            x_scale = cell_width * max_col / width #/ 45
            y_scale = cell_height * max_row / height #/ 15

            worksheet.insert_image(
                row=row,
                col=0,
                filename=image_paths[image_id][page],
                options={
                    'x_offset': 0,
                    'y_offset': 0,
                    'x_scale': x_scale,
                    'y_scale': y_scale
                })
            row += max(page_max_row[page], max_row)

    workbook.close()
    return report_file


def write_line_acc(count_line, dict_text, sheet, image_name, page_idx):
    avg_acc = 0
    for idx in dict_text:
        # print('Gt is {}, Pred is {}'.format(dict_text[idx][0], dict_text[idx][1]))
        acc = calculate_accuracy_by_char2(dict_text[idx][1], dict_text[idx][0])
        sheet.write(count_line, 0, image_name)
        sheet.write(count_line, 1, page_idx)
        sheet.write(count_line, 2, 'cell_' + str(idx))
        sheet.write(count_line, 3, dict_text[idx][0])
        sheet.write(count_line, 4, dict_text[idx][1])
        sheet.write(count_line, 5, acc)
        count_line = count_line + 1
        avg_acc += acc
    avg_acc = avg_acc
    return avg_acc, count_line


def report_matching(predicted_json, ca_json, report_file, dpi_ratio=1):
    data = []
    for image_id in predicted_json:
        predicted = get_lines(predicted_json[image_id])
        answer = get_lines(ca_json.get(image_id))
        acc_file = 0
        if answer is None:
            continue
        for idx_page in answer:
            label_pred_page = predicted[idx_page]
            label_gt_page = answer[idx_page]
            dict_text = check_overlap(label_gt_page, label_pred_page, dpi_ratio=dpi_ratio)
            # acc_page, count_line = write_line_acc(count_line, dict_text, sheet_line, image_id, idx_page)
            for idx in dict_text:
                data.append({
                    'FILE': image_id,
                    'PAGE': idx_page,
                    'CELL': 'cell_' + str(idx),
                    'CA': dict_text[idx][0],
                    'OCR': dict_text[idx][1]
                })

    return BasicReport(os.path.dirname(report_file)).save(data, os.path.basename(report_file))


def make_report_acc(predicted_json, ca_json, report_file, dpi_ratio=1):
    workbook = xlsxwriter.Workbook(report_file)
    sheet_line = workbook.add_worksheet(name='OCR')
    count = 0
    header = ['FILE', 'PAGE', 'LINE', 'CA', 'OCR', 'ACCURACY', 'HARD TO READ']
    for i, text in enumerate(header):
        sheet_line.write(count, i, text)
    count += 1
    sheet_page = workbook.add_worksheet("PAGE ACCURACY")
    sheet_file = workbook.add_worksheet("FILE ACCURACY")
    count_line = count
    file_idx = 0
    acc_all = 0
    page_idx = 0
    for image_id in predicted_json:
        predicted = get_lines(predicted_json[image_id])
        answer = get_lines(ca_json.get(image_id))
        acc_file = 0
        if answer is None:
            continue
        for idx_page in answer:
            label_pred_page = predicted[idx_page]
            label_gt_page = answer[idx_page]
            dict_text = check_overlap(label_gt_page, label_pred_page, dpi_ratio=dpi_ratio)
            acc_page, count_line = write_line_acc(count_line, dict_text, sheet_line, image_id, idx_page)

            sheet_page.write_string(page_idx, 0, image_id)
            sheet_page.write_string(page_idx, 1, idx_page)
            sheet_page.write_number(page_idx, 2, acc_page/len(dict_text))

            acc_file += acc_page/len(dict_text)
            page_idx += 1
            acc_all += acc_page
        sheet_file.write_string(file_idx, 0, image_id)
        sheet_file.write_number(file_idx, 1, acc_file / len(answer))
        file_idx += 1
    sheet_file.write_string(0, 5, 'Total Acc')
    sheet_file.write_number(0, 6, acc_all / (count_line-count))
    workbook.close()
    return report_file


def read_datapile_lable(page_paths):
    output = {}
    raw_output = {}
    for i, file in enumerate(page_paths):
        print(file)
        with open(file, 'r', encoding='utf-8') as f:
            tmp = json.load(f)
            if '_via_img_metadata' in tmp:
                regions = list(tmp['_via_img_metadata'].items())[0][1]['regions']
            else:
                regions = tmp['attributes']['_via_img_metadata']['regions']

        cells = {}
        for j, region in enumerate(regions):
            if region['region_attributes']['label'].strip() in ('<?>', ''):
                continue
            if region['shape_attributes']['name'] != 'polygon':
                x1 = region['shape_attributes']['x']
                y1 = region['shape_attributes']['y']
                x2 = x1 + region['shape_attributes']['width']
                y2 = y1 + region['shape_attributes']['height']
                cells[j] = {
                    'location': (y1, x1, y2, x2),
                    'text': region['region_attributes']['label'],
                }
        sorted_tmp = collections.OrderedDict(
            sorted(cells.items(), key=lambda kv: (kv[1]['location'][0], kv[1]['location'][1])))

        if file[-9:] == '.png.json':
            page = int(file[:-9].rsplit('_', 1)[1]) - 1
        else:
            page = int(file[:-5].rsplit('_', 1)[1]) - 1
        raw_output['page_{}'.format(('000' + str(page))[-4:])] = sorted_tmp
        # output['page_{}'.format(('000' + str(page))[-4:])] = merge_cell(sorted_tmp)
    return collections.OrderedDict(sorted(raw_output.items(), key=lambda kv: kv[0]))


if __name__ == "__main__":
    read_datapile_lable('/Users/louis/Documents/FLAX_SCANNER/PROJECT/prj_alps/data/Json')