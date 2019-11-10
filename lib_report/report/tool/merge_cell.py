import collections


def get_central(location):
    y1, x1, y2, x2 = location
    return {
        'central': (y1 + y2)/2,
        'height': y2 - y1,
        'start': x1,
        'length': x2 - x1
    }


def is_inline(central_line, current_height, central_box, box_height, height_penalty_rate=2, central_penalty_rate=6.4):
    if current_height/height_penalty_rate >= box_height or box_height >= height_penalty_rate * current_height:
        return False

    lower_central_threshold = central_box - box_height/central_penalty_rate
    upper_central_threshold = central_line + current_height/central_penalty_rate
    if lower_central_threshold <= central_line <= central_box <= upper_central_threshold:
        return True

    return False


def sort_in_line(line, height_penalty=5):
    return sorted(line, key=lambda item: item['info']['start'] + height_penalty * item['info']['central'])


def merge_cell(sorted_tmp):
    page_i = {}
    line_height = -3
    line_no = -1
    current_height = 0
    for line in sorted_tmp:
        if is_inline(line_height, current_height,
                     sorted_tmp[line]['info']['central'], sorted_tmp[line]['info']['height']):
            line_height = (line_height + sorted_tmp[line]['info']['central']) / 2
            page_i['line_{}'.format(line_no)].append(sorted_tmp[line])
        else:
            line_height = sorted_tmp[line]['info']['central']
            line_no += 1
            page_i['line_{}'.format(line_no)] = [sorted_tmp[line]]
        page_i['line_{}'.format(line_no)] = sort_in_line(page_i['line_{}'.format(line_no)])
        current_height = sorted_tmp[line]['info']['height']
    return page_i


def get_lines(one_file_pages_result):
    if one_file_pages_result is None:
        return None
    output = {}
    for page in one_file_pages_result:
        tmp = one_file_pages_result[page]
        for cell in tmp:
            tmp[cell]['info'] = get_central(tmp[cell]['location'])
            tmp[cell].pop('confidences', None)
        sorted_tmp = collections.OrderedDict(
            sorted(tmp.items(), key=lambda kv: (kv[1]['info']['central'], kv[1]['info']['start'])))
        output[page] = merge_cell(sorted_tmp)
    return output