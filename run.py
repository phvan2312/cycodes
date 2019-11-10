import os
import json
import shutil
from ocr_model_wrapper import OcrWrapper
from excel_wrapper import ExcelWrapper
import utils
import pandas as pd
from lib_report.wrapper import write_colored_wrong_case, update_reporting_columns

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

def write_to_excel(df, output_excel_fn, hidding_column_names):
    excel_writer = ExcelWrapper(output_excel_fn)
    excel_writer.add_work_sheet("Sheet1")

    index_column = 0

    for col_name in list(df.columns):
        v = list(df[col_name])

        if col_name == 'Images':
            excel_writer.add_column(index_column, "Sheet1", v, col_name, column_width=70, is_image=True,
                                    is_hidden=col_name in hidding_column_names)
        else:
            excel_writer.add_column(index_column, "Sheet1", v, col_name,
                                    is_hidden=col_name in hidding_column_names,
                                    column_width=5 if col_name in ['T/F', "Box ID"] else 30)

        index_column += 1

    write_colored_wrong_case(df, ai_ocr_col_name='Predict by cannet_ocr', ca_col_name='Label',
                             writer=excel_writer.get_fake_writer())

    # close
    excel_writer.close()

# 3 modes: run single files, run single folder,
import click
@click.command()
@click.option('-args_fn', type=str, required=True, default="./arguments/args_nancy_ffg.json")
def main(args_fn):

    """
    Load arguments from file
    """
    args = json.load(open(args_fn,'r'))

    use_lucas = args.get('use_lucas', False)
    use_cannet = args.get('use_cannet', True)
    use_kush   = args.get('use_kush', False)
    use_pika   = args.get('use_pika', False)

    input_image = args['input_image']
    input_json_folder = args['input_json_folder']
    output_excel_fn = args['output_excel_fn']
    output_folder = args['output_folder']

    hidding_column_names = args['hidding_column_names']
    batch_size = args['batch_size']

    """
    Configurations
    """
    print ("+" * 20)
    print (json.dumps(args, ensure_ascii=False, indent=2))
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
        final_err_msgs = []

        #
        json_fns = list(os.listdir(input_json_folder))
        s_id = 0

        while(s_id < len(json_fns)):
            try:
                for _id in range(s_id, len(json_fns)):
                    json_fn = json_fns[_id]

                    # finding the corresponding image for the specified json
                    base_name = os.path.splitext(json_fn)[0]
                    corr_image_fn = image_with_base_names.get(base_name, None)
                    ####

                    full_path_json_fn = os.path.join(input_json_folder, json_fn)
                    json_dct = json.load(open(full_path_json_fn, 'r', encoding='utf-8'))

                    sub_image_folder = os.path.join(output_folder, base_name)
                    if not os.path.exists(sub_image_folder):
                        os.makedirs(sub_image_folder)

                    if corr_image_fn is not None:
                        image = utils.read_image(corr_image_fn)

                        result, statistic, err_msgs = utils.process_one_json(json_dct, image, corr_image_fn,
                                                                   sub_image_folder, ocr_wrapper,
                                                                   accepted_formal_kies=args['accepted_formal_kies'],
                                                                   key_type_=args['key_type_'],
                                                                   text_type_=args['text_type_'],
                                                                   only_label_diff_ocr=args['only_label_diff_ocr'])

                        statistic['org_image_fn'] = corr_image_fn
                        final_statistics += [statistic]

                        final_results += result
                        final_err_msgs += err_msgs

                    else:
                        print("Can not find coressponding image for json: %s !!!" % json_fn)

                    s_id = _id + 1

            except KeyboardInterrupt as e:
                user_input = enter_input("Press (r) for resume, (q) for quit: ", valid_input=['r', 'q'])
                if user_input == 'r':
                    print("Resuming ...")
                    continue
                elif user_input == 'q':
                    print('Exitting ...')
                    break

        print ("Writing to excel %s ..." % output_excel_fn)

        """
        Prepare DF 
        """
        # get unique
        final_results = utils.get_unique_list_of_dict(final_results)

        index_column = 0

        labels = [elem['label'] for elem in final_results]
        box_ids = [elem['box_id'] for elem in final_results]
        bboxs  = [elem['bbox'] for elem in final_results]
        file_names = [os.path.basename(elem['file name']) for elem in final_results]
        formal_kies = [elem['formal_key'] for elem in final_results]
        sub_img_fns = [elem['sub_image_fn'] for elem in final_results]
        base_name = os.path.splitext(output_excel_fn)[0]

        n_samples = len(labels)
        print ("Total row:", n_samples)
        if n_samples <= 0:
            print ("There's no wrong case !!")
            exit()

        # Update dataframe (for easier excel control)
        df = pd.DataFrame.from_dict(
            {
                'Box ID': box_ids,
                'File Name': file_names,

                'Images': sub_img_fns,
                'Sub Image Fns': sub_img_fns,
                'Formal Key': formal_kies,
                'Label': labels,

                'Bbox': bboxs
            }
        )

        for model_name in list(ocr_wrapper.models.keys()):
            preds_by_model_name = [v['predict'][model_name] for v in final_results]
            df['Predict by %s_ocr' % model_name] = preds_by_model_name

        # update some colums used for reporting
        df = update_reporting_columns(df, ai_ocr_col_name='Predict by cannet_ocr', ca_col_name='Label')

        # save df to disk for debug or more additional requirements
        csv_path = base_name + ".csv"
        df.to_csv(csv_path)
        print ("Writing df to %s ..." % csv_path)

        ###

        """
        Write error to disk (If any)
        """
        writer = open(base_name + "_error.txt", "w")
        writer.write("\n".join(final_err_msgs))
        writer.close()

        """
        Writting to excel:
        > 1. Split to batch
        > 2. For each batch, write to excel
        """
        batch_ids = [(s, min(s + batch_size, df.shape[0])) for s in range(0, df.shape[0], batch_size)]
        for (s, e) in batch_ids:
            _df = df[s:e]
            _out_fn = base_name + "_from_%d_to_%d" % (s,e) + ".xlsx"

            write_to_excel(_df, _out_fn, hidding_column_names)
            print (">> Writing to %s ..." % _out_fn)

        # finish
        print ("Finished (T.T)")

if __name__ == "__main__":
    main()