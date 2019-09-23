import os
import json
import shutil
from ocr_model_wrapper import OcrWrapper
from excel_wrapper import ExcelWrapper
import utils

"""
The main function: 
- SINGLE_INPUT  : input a <single input>, run ocr, print to console.
- SINGLE_FOLDER : input a <single folder> (#contain images ONLY), run ocr for all images within, report an excel file.
- BOTH_FOLDER_JSON_IMAGE (MOSTLY USED) : input a <image folder> (#contain invoice's images) and <json folder> (#datapile).
split the big image invoice into sub regions. Then run ocr, report to an excel.
"""

SINGLE_INPUT  = 0
SINGLE_FOLDER = 1
BOTH_FOLDER_JSON_IMAGE = 2
MODES = {
    SINGLE_INPUT: "SINGLE_INPUT",
    SINGLE_FOLDER: "SINGLE_FOLDER",
    BOTH_FOLDER_JSON_IMAGE: "BOTH_FOLDER_JSON_IMAGE"
}

def choose_mode(input_image, input_json_folder):
    if os.path.isdir(input_json_folder) and os.path.isdir(input_image):
        return BOTH_FOLDER_JSON_IMAGE
    else:
        if os.path.isdir(input_image): return SINGLE_FOLDER
        elif os.path.isfile(input_image): return SINGLE_INPUT

    raise Exception("Unknown mode")

def enter_input(help_str, valid_input):
    user_input = ""
    while user_input not in valid_input:
        user_input = input(help_str)

        if user_input not in valid_input:
            print ("> OC !!")

    return user_input

# 3 modes: run single files, run single folder,
import click
@click.command()
@click.option('-use_lucas', is_flag=True)
@click.option('-use_cannet', is_flag=True)
@click.option('-use_kush', is_flag=True)
@click.option('-use_pika', is_flag=True)

@click.option('-input_image', type=str, required=True)
@click.option('-input_json_folder', type=str, default='')
@click.option('-output_excel_fn', type=str, required=True, default="./excel_output2.xlsx")
@click.option('-output_folder', type=str, required=True, default="./output")
def main(use_lucas, use_cannet, use_kush, use_pika, input_image, input_json_folder,
         output_excel_fn, output_folder):
    """
    Configurations
    """
    print ("+" * 20)
    print ("use_lucas_ocr:", use_lucas)
    print ("use_cannet_ocr:", use_cannet)
    print ("use_kush_ocr:", use_kush)
    print ("use_pika_ocr:", use_pika)
    print ("input_image", input_image)
    print ("input_json_folder", input_json_folder)
    print ("+" * 20)

    config_fn = "./configs/configs.json"
    config = json.load(open(config_fn, 'r', encoding='utf-8'))

    """
    Adding modules
    """
    ocr_wrapper = OcrWrapper(src_model_path=os.path.join(os.path.dirname(os.path.realpath(__file__)), 'saved_models'))
    if use_lucas: ocr_wrapper.add_ocr_model('lucas', config.get('lucas', None))
    if use_cannet: ocr_wrapper.add_ocr_model('cannet', config.get('cannet', None))
    if use_kush: ocr_wrapper.add_ocr_model('kush', config.get('kush', None))
    if use_pika: ocr_wrapper.add_ocr_model('pika', config.get('pika', None))

    """
    Predict
    """
    mode = choose_mode(input_image, input_json_folder)

    if mode == SINGLE_INPUT:
        dct_result = ocr_wrapper.predict(input_image)
        print (json.dumps(dct_result, ensure_ascii=False, indent=2))

    elif mode == SINGLE_FOLDER:
        dct_results = ocr_wrapper.predict_folder(input_image)

        # write_to_excel
        excel_writer = ExcelWrapper(output_excel_fn)
        excel_writer.add_work_sheet("Sheet1")

        index_column = 0

        file_names = list(dct_results.keys())

        # insert file_names
        excel_writer.add_column(index_column, "Sheet1", file_names, 'file name', column_width=70)
        index_column += 1

        # insert images
        excel_writer.add_column(index_column, "Sheet1", file_names, 'image', column_width=70, is_image=True)
        index_column += 1

        # insert predict
        for model_name in list(ocr_wrapper.models.keys()):
            preds_by_model_name = [v[model_name] for _,v in dct_results.items()]
            excel_writer.add_column(index_column, "Sheet1", preds_by_model_name, 'predict by %s_ocr' % model_name)

            index_column += 1

        excel_writer.close()

    elif mode == BOTH_FOLDER_JSON_IMAGE:
        if os.path.isdir(output_folder):
            shutil.rmtree(output_folder)

        image_with_base_names = utils.read_folder_with_basename(input_image)

        #
        final_results = []
        final_statistics = []

        #
        json_fns = list(os.listdir(input_json_folder))
        s_id = 0

        while(s_id < len(json_fns)):
            try:
                for _id in range(s_id, len(json_fns)):
                    json_fn = json_fns[_id]

                    base_name = os.path.splitext(json_fn)[0]
                    corr_image_fn = image_with_base_names.get(base_name, None)

                    full_path_json_fn = os.path.join(input_json_folder, json_fn)
                    json_dct = json.load(open(full_path_json_fn, 'r', encoding='utf-8'))

                    json_output_folder = os.path.join(output_folder, base_name)
                    if not os.path.exists(json_output_folder):
                        os.makedirs(json_output_folder)

                    if corr_image_fn is not None:
                        image = utils.read_image(corr_image_fn)

                        result, statistic = utils.process_one_json(json_dct, image, corr_image_fn,
                                                                   json_output_folder, ocr_wrapper)

                        statistic['org_image_fn'] = corr_image_fn
                        final_statistics += [statistic]

                        final_results += result
                    else:
                        print("Can not find coressponding image for json: %s !!!" % json_fn)

                    s_id = _id + 1

            except KeyboardInterrupt as e:
                print (e)
                print (s_id)

                user_input = enter_input("Press (r) for resume, (q) for quit: ", valid_input=['r', 'q'])
                if user_input == 'r':
                    print("Resuming ...")
                    continue
                elif user_input == 'q':
                    print('Exitting ...')
                    break

        print ("Writing to excel %s ..." % output_excel_fn)

        # get unique
        final_results = utils.get_unique_list_of_dict(final_results)

        # write to excel
        excel_writer = ExcelWrapper(output_excel_fn)
        excel_writer.add_work_sheet("Sheet1")

        index_column = 0

        labels = [elem['label'] for elem in final_results]
        file_names = [os.path.basename(elem['file name']) for elem in final_results]
        formal_kies = [elem['formal_key'] for elem in final_results]
        sub_img_fns = [elem['sub_image_fn'] for elem in final_results]

        excel_writer.add_column(index_column, "Sheet1", file_names, 'File Name', column_width=70)
        index_column += 1

        excel_writer.add_column(index_column, "Sheet1", sub_img_fns, 'Images', column_width=70, is_image=True)
        index_column += 1

        excel_writer.add_column(index_column, "Sheet1", formal_kies, 'Formal Key')
        index_column += 1

        excel_writer.add_column(index_column, "Sheet1", labels, 'Label')
        index_column += 1

        for model_name in list(ocr_wrapper.models.keys()):
            preds_by_model_name = [v['predict'][model_name] for v in final_results]
            excel_writer.add_column(index_column, "Sheet1", preds_by_model_name, 'Predict by %s_ocr' % model_name)

            index_column += 1

        excel_writer.add_work_sheet("Statistics")

        # close
        excel_writer.close()

        # finish
        print ("Finished (T.T)")

if __name__ == "__main__":
    main()

    # for example
    """
    # for example, run the following commands:
    1. python run.py -use_lucas -use_cannet -input_image "/home/vanph/Desktop/for_nancy/cycodes/test_338_files/img/" -input_json_folder "/home/vanph/Desktop/for_nancy/cycodes/test_338_files/processed-labels_v2"
    
    """
