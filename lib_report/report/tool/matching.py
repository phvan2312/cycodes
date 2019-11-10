import os
from .accuracy import calculate_accuracy_by_char2
DPI_RATIO = 1
PROCESSED_THRESH = 0.5


def get_dict(dict_page, ratio):
    _dict = {}
    idx = 0
    for line in dict_page:
        line_info = dict_page[line]
        for box in line_info:
            location = box['location']
            dict_tmp = {}
            location_new = [int(location[0] / ratio), int(location[1] / ratio), int(location[2] / ratio),
                            int(location[3] / ratio)]
            dict_tmp['location'] = location_new
            dict_tmp['text'] = box['text']
            _dict[idx] = dict_tmp
            idx = idx + 1
    return _dict


def intersect_area(box_1, box_2, cell_no, processed_thresh=PROCESSED_THRESH):
    y_min_1, x_min_1, y_max_1, x_max_1 = box_1
    y_min_2, x_min_2, y_max_2, x_max_2 = box_2
    if y_max_1 <= y_min_2 or y_min_1 >= y_max_2:
        return 0, 0
    if x_max_1 <= x_min_2 or x_min_1 >= x_max_2:
        return 0, 0

    y_1, y_2, y_3, y_4 = sorted([y_min_1, y_min_2, y_max_1, y_max_2])
    x_1, x_2, x_3, x_4 = sorted([x_min_1, x_min_2, x_max_1, x_max_2])

    intersect_stretch = (y_3 - y_2) * (x_3 - x_2)
    box_1_stretch = (y_max_1 - y_min_1) * (x_max_1 - x_min_1)
    box_2_stretch = (y_max_2 - y_min_2) * (x_max_2 - x_min_2)

    redundant_1 = (box_1_stretch - intersect_stretch) / box_1_stretch
    redundant_2 = (box_2_stretch - intersect_stretch) / box_2_stretch
    is_is_processed = min(redundant_1, redundant_2) < processed_thresh
    if not is_is_processed:
        return 0, 0
    if (y_max_1 - y_min_1) > 2 * (x_max_1 - x_min_1):
        return 1, redundant_1

    if (x_max_1 - x_min_1) >= (x_max_2 - x_min_2):
        return 1, redundant_1
    else:
        return 2, redundant_2


def check_overlap(label_gt_dict, label_pred_dict, dpi_ratio=DPI_RATIO):
    label_pred_dict = get_dict(label_pred_dict, 1)
    label_gt_dict = get_dict(label_gt_dict, dpi_ratio)
    dict_text = {}
    min_extent = -20
    max_extent = 20
    bias = 0

    label_list = {}
    label_fill = {}
    for cell_no in label_gt_dict:
        label_bigger = True
        box_gt = label_gt_dict[cell_no]
        is_overlap = False
        if 1:
            fill = 0
            pred_list = []
            for i in range(min_extent + bias, max_extent + 1 + bias):
                if cell_no + i in label_pred_dict:
                    box_pred = label_pred_dict[cell_no + i]

                    intersect = intersect_area(box_gt['location'], box_pred['location'], cell_no)
                    if intersect[0] > 0:
                        if intersect[1] <= 0.1:
                            dict_text[str(cell_no)] = [box_gt['text'], box_pred['text']]
                            bias = i
                            is_overlap = True
                            break
                        else:
                            if intersect[0] == 1 and fill + 1 - intersect[1] <= 1:
                                fill += 1 - intersect[1]
                                bias = i
                                is_overlap = True
                                pred_list.append((cell_no + 1, label_pred_dict[cell_no + i]['text'],
                                                  label_pred_dict[cell_no + i]['location'][1]))
                            elif intersect[0] == 2 and label_fill.get(cell_no + i, 0) + 1 - intersect[1] <= 1:
                                label_bigger = False
                                label_fill[cell_no + i] = label_fill.get(cell_no + i, 0) + 1 - intersect[1]
                                bias = i
                                is_overlap = True
                                if cell_no + i not in label_list:
                                    label_list[cell_no + i] = [(cell_no, label_gt_dict[cell_no]['text'],
                                                                label_gt_dict[cell_no]['location'][1])]
                                else:
                                    label_list[cell_no + i].append((cell_no, label_gt_dict[cell_no]['text'],
                                                                    label_gt_dict[cell_no]['location'][1]))
                                break
            if len(pred_list) > 0:
                prd = ''.join([_[1] for _ in sorted(pred_list, key=lambda _: _[-1])])
                acc = calculate_accuracy_by_char2(box_gt['text'], prd)
                if acc > 0:  # prevent double matching in label_list
                    dict_text[str(cell_no)] = [box_gt['text'], prd]
                elif label_bigger:
                    dict_text[str(cell_no)] = [box_gt['text'], '']
            if not is_overlap:
                dict_text[str(cell_no)] = [box_gt['text'], '']
    if len(label_list.keys()) > 0:
        for key in label_list:
            # print('shit', key)
            lbl = ''.join([_[1] for _ in sorted(label_list[key], key=lambda _: _[-1])])
            acc = calculate_accuracy_by_char2(lbl, label_pred_dict[key]['text'])
            cell_nos = [str(_[0]) for _ in label_list[key]]
            tmp = cell_nos
            for cell_no in tmp:
                if cell_no in dict_text:
                    if calculate_accuracy_by_char2(dict_text[cell_no][0], dict_text[cell_no][1]) < acc:
                        dict_text.pop(cell_no, None)
                    else:
                        cell_nos.remove(cell_no)
            if len(cell_nos) > 0:
                cells_key = '_'.join(cell_nos)
                if acc > 0:
                    dict_text[cells_key] = \
                        [lbl, label_pred_dict[key]['text']]
                elif cells_key not in dict_text:
                    dict_text[cells_key] = [lbl, '']
    return dict_text

