import os, json
import numpy as np
from PIL import Image
import cv2

def normalize(val):
    return val.strip()

def check_valid_shape_attribute(shape_attrb):
    # currently only support for checking the validity of rectangle
    # There's stil some kind of different shapes need to be checked
    if shape_attrb.get('name', '') == 'rect':
        x = shape_attrb.get('x', -1)
        y = shape_attrb.get('y', -1)
        width = shape_attrb.get('width', -1)
        height = shape_attrb.get('height', -1)

        if np.any(np.array([x,y,width,height]) < 0): return False
        else:
            return True

    return True

def get_sub_image(image, shape_attbs):
    if shape_attbs["name"] == "rect":
        x, y, w, h = shape_attbs['x'], shape_attbs['y'], shape_attbs['width'], shape_attbs['height']

        sub_image =  image[y:y + h, x: x + w, :]
    elif shape_attbs["name"] == 'polygon':
        # the root cause of polygon maybe becaused of the rotated sub-regions. So need to de-warp
        cnts = [(x, y) for (x, y) in zip(shape_attbs["all_points_x"], shape_attbs["all_points_y"])]

        # transoform to the right direction
        sub_image = four_point_transform(image, np.array(cnts))
    else:
        raise Exception("WTF region type?, must be rect/polygon")

    return sub_image

def convert_kv_json_to_datapile_json(kv_json_dct):
    results = {
        #json_dct['attributes']['_via_img_metadata']['regions']
        'attributes':{
            '_via_img_metadata': {
                'regions':[]
            }
        }
    }

    for region in kv_json_dct:
        p1, p2, p3, p4 = region['location']
        x_min, y_min, x_max, y_max = p1 + p3

        x,y,w,h = x_min, y_min, x_max - x_min, y_max - y_min
        shape_attrbs = {
            'name':'rect',
            'x':x,
            'y':y,
            'width':w,
            'height':h
        }

        label_info = region['label_info']
        region_attrbs = {
            'formal_key': label_info.get('formal_key',''),
            'key_type': label_info.get('key_type',''),
            "text_type": label_info.get('text_type',''),
            "text_category": label_info.get('text_category',''),
            "note": label_info.get('note',''),
            "label": region.get('text','')
        }

        results['attributes']['_via_img_metadata']['regions'] += [
            {
                'shape_attributes': shape_attrbs,
                'region_attributes': region_attrbs
            }
        ]

    return results


global_img = 0
accepted_formal_kies = [] #["company_name", "company_address", "account_name_kana", "account_name_kanji", "item_name"]
def process_one_json(json_dct, image, image_file_name, json_output_folder, model):
    _id = 1
    dct_infos = []
    statistic = {}

    # adding detect type of json here (from kv/datapile)
    if 'attributes' in json_dct: pass #datapile
    else:
        # kv
        json_dct = convert_kv_json_to_datapile_json(json_dct)

    print ("Processing file: %s ..." % image_file_name)

    #
    for region in json_dct['attributes']['_via_img_metadata']['regions']:
        shape_attbs = region['shape_attributes']
        region_attbs = region['region_attributes']

        formal_key = region_attbs.get("formal_key", "")
        formal_key = normalize(formal_key)

        # Some files from Daiichi 4 contains X,Y coordinates which less than 0.
        if not check_valid_shape_attribute(shape_attbs):
            print ("In file: %s, shape_attributes: %s, is not valid !!!" % (image_file_name, json.dumps(shape_attbs)))
            continue

        if formal_key in accepted_formal_kies \
                or \
                len(accepted_formal_kies) == 0: # accept all the formal keys

            # just show up the region which has value of field "key_type"/"type" is "value"
            if not 'value' in [region_attbs.get("key_type", ""), region_attbs.get("type", "")]:
                continue

            if not 'printed' in [region_attbs.get("text_type", "")]:
                continue

            label = region_attbs['label']

            image_region = get_sub_image(image, shape_attbs)

            predict = model.predict(image_region)

            image_out_fn = os.path.join(json_output_folder, "%s_%d.png" % (formal_key, _id))

            if label == predict['cannet']:
                continue

            _id += 1
            write_image(image_region, image_out_fn)

            dct_info = {
                'file name': image_file_name,
                'formal_key': formal_key,
                'sub_image_fn': image_out_fn,
                'predict': predict,
                'label': label,
                'bbox': json.dumps(shape_attbs, ensure_ascii=False)
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

def get_unique_list_of_dict(list_of_dict):
    results = {}

    for dct in list_of_dict:
        k = "_cy_oc_".join([str(x) for x in dct.values()])

        if k not in results:
            results[k] = dct

    return list(results.values())

def four_point_transform(image, pts):
    # obtain a consistent order of the points and unpack them
    # individually
    rect = order_points(pts)
    (tl, tr, br, bl) = rect

    # compute the width of the new image, which will be the
    # maximum distance between bottom-right and bottom-left
    # x-coordiates or the top-right and top-left x-coordinates
    widthA = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
    widthB = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))
    maxWidth = max(int(widthA), int(widthB))

    # compute the height of the new image, which will be the
    # maximum distance between the top-right and bottom-right
    # y-coordinates or the top-left and bottom-left y-coordinates
    heightA = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
    heightB = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))
    maxHeight = max(int(heightA), int(heightB))

    # now that we have the dimensions of the new image, construct
    # the set of destination points to obtain a "birds eye view",
    # (i.e. top-down view) of the image, again specifying points
    # in the top-left, top-right, bottom-right, and bottom-left
    # order
    dst = np.array([
        [0, 0],
        [maxWidth - 1, 0],
        [maxWidth - 1, maxHeight - 1],
        [0, maxHeight - 1]], dtype="float32")

    # compute the perspective transform matrix and then apply it
    M = cv2.getPerspectiveTransform(rect, dst)
    warped = cv2.warpPerspective(image, M, (maxWidth, maxHeight))

    # return the warped image
    return warped

def order_points(pts):
    # initialzie a list of coordinates that will be ordered
    # such that the first entry in the list is the top-left,
    # the second entry is the top-right, the third is the
    # bottom-right, and the fourth is the bottom-left
    rect = np.zeros((4, 2), dtype="float32")

    # the top-left point will have the smallest sum, whereas
    # the bottom-right point will have the largest sum
    s = pts.sum(axis=1)
    rect[0] = pts[np.argmin(s)]
    rect[2] = pts[np.argmax(s)]

    # now, compute the difference between the points, the
    # top-right point will have the smallest difference,
    # whereas the bottom-left will have the largest difference
    diff = np.diff(pts, axis=1)
    rect[1] = pts[np.argmin(diff)]
    rect[3] = pts[np.argmax(diff)]

    # return the ordered coordinates
    return rect