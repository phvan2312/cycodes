import os, json
import numpy as np
from PIL import Image
import cv2

def normalize(val):
    return val.strip()

def get_bounding_box(shape_attbs):
    if shape_attbs["name"] == "rect":
        x, y, w, h = shape_attbs['x'], shape_attbs['y'], shape_attbs['width'], shape_attbs['height']
    else:
        cnt = [(x, y) for (x,y) in zip(shape_attbs["all_points_x"],shape_attbs["all_points_y"])]
        x, y, w, h = cv2.boundingRect(np.array(cnt))
    return (x, y, w, h)

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

            x, y, w, h = get_bounding_box(shape_attbs)
            image_region = image[y:y + h, x: x + w, :]

            predict = model.predict(image_region)

            image_out_fn = os.path.join(json_output_folder, "%s_%d.png" % (formal_key, _id))

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

def read_image(image_path):
    stream = open(image_path, "rb")
    bytes = bytearray(stream.read())
    numpyarray = np.asarray(bytes, dtype=np.uint8)
    img = cv2.imdecode(numpyarray, cv2.IMREAD_COLOR)
    return img

def write_image(image, out_fn):
    Image.fromarray(image).save(out_fn)

    if os.path.exists(out_fn):
        print ("Saved %s successfully ..." % out_fn)
    else:
        raise Exception("Not save %s !!!!" % out_fn)