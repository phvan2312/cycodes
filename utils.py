import os, json
import numpy as np
from PIL import Image

def insert_image_worksheet(worksheet, img_path, index, col_index, scale=3, positioning=2):
    img = np.array(Image.open(img_path))
    height = img.shape[0]
    worksheet.insert_image(scale * index - scale + 1, col_index, img_path, {
        'x_offset': 2, 'y_offset': 2,
        # 'x_scale': 20.0/height, 'y_scale': 20.0/height,
        'x_scale': scale * 18.0 / height, 'y_scale': scale * 18.0 / height,
        'positioning': positioning
    })

import xlsxwriter
def write_to_excel(excel_out_fn, preds, lbls, fns, formal_kies, sub_img_fns):
    workbook  = xlsxwriter.Workbook(excel_out_fn)
    worksheet = workbook.add_worksheet()

    worksheet.write(0, 0, 'File Name')
    worksheet.write(0, 1, 'Image')
    worksheet.write(0, 2, 'Formal Key')
    worksheet.write(0, 3, 'GT')
    worksheet.write(0, 4, 'Predict')

    worksheet.set_column('A:A', 120)
    worksheet.set_column('B:B', 70)
    worksheet.set_column('C:C', 30)
    worksheet.set_column('D:D', 30)
    worksheet.set_column('E:E', 15)

    id = 1
    scale = 1

    for pred, lbl, fn, sub_img_fn, formal_key in zip(preds, lbls, fns, sub_img_fns, formal_kies):
        worksheet.set_row(id, 50)

        worksheet.write("A%d" % (id + 1), fn)
        insert_image_worksheet(worksheet,sub_img_fn, id, col_index=1, scale=scale)
        worksheet.write("C%d" % (id + 1), formal_key)
        worksheet.write("D%d" % (id + 1), lbl)
        worksheet.write("E%d" % (id + 1), pred)

        id += 1

    workbook.close()

import matplotlib.pyplot as plt
def imgshow(img):
    return

    plt.imshow(img)
    plt.show()

def normalize(val):
    return val.strip()

global_img = 0
accepted_formal_kies = ["company_name", "company_address", "account_name_kana", "account_name_kanji", "item_name"]
def process_one_json(json_dct, image, image_file_name, json_output_folder, model):
    _id = 1
    dct_infos = []
    statistic = {}

    for region in json_dct['attributes']['_via_img_metadata']['regions']:
        shape_attbs = region['shape_attributes']
        region_attbs = region['region_attributes']

        formal_key = region_attbs.get("formal_key", "")
        formal_key = normalize(formal_key)

        if formal_key in accepted_formal_kies:
            # just show up the region which has value of field "key_type"/"type" is "value"
            if not 'value' in [region_attbs.get("key_type",""), region_attbs.get("type","")]:
                break

            label = region_attbs['label']

            x,y,w,h = shape_attbs['x'], shape_attbs['y'], shape_attbs['width'], shape_attbs['height']
            image_region = image[y:y+h, x: x+w, :]

            predict = model.predict(image_region)

            image_out_fn = os.path.join(json_output_folder, "%s_%d.png" % (formal_key, _id))
            print ("writing to %s ..." % image_out_fn)

            _id += 1
            write_image(image_region, image_out_fn)

            dct_info = {
                'file name': image_file_name,
                'formal_key': formal_key,
                'sub_image_fn': image_out_fn,
                'predict': predict,
                'label': label
            }

            dct_infos += [dct_info]

            statistic['save_fn'] = image_out_fn
            statistic['shape_attribute'] = json.dumps(shape_attbs, ensure_ascii=False)
            statistic.update(region_attbs)

    return dct_infos, statistic

def read_folder_with_basename(folder):
    dct = {}
    for fn in os.listdir(folder):
        base_name = os.path.splitext(fn)[0]
        dct[base_name] = os.path.join(folder, fn)

    return dct

import numpy as np
from PIL import Image
def read_image(image_path):
    pil_image = Image.open(image_path)
    return np.array(pil_image)

def write_image(image, out_fn):
    global global_img
    Image.fromarray(image).save(out_fn)

    if os.path.exists(out_fn):
        print ("save %s successful" % out_fn)
        global_img += 1
    else:
        raise Exception("Not save %s !!!!" % out_fn)