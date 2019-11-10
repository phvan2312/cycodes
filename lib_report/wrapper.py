import pandas as pd
from report.tool.verify import Verification, ALL_OUTPUT_COLUMNS, FORMATTING, T_F

def update_reporting_columns(df, ai_ocr_col_name = 'Predict by cannet_ocr', ca_col_name = 'Label'):
    # Initialize
    verification_model = Verification()
    verification_model.AI_OCR = ai_ocr_col_name
    verification_model.CORRECT_ANSWER = ca_col_name
    verification_model.strip = False
    verification_model.normalize = False
    verification_model.correct_dict = None

    # Update column to df
    accpeted_column_names = ['T/F', 'RIGHT -> WRONG', 'Formatting']
    accpeted_column_idxs = [list(ALL_OUTPUT_COLUMNS).index(column_name) for column_name in accpeted_column_names]

    for i, column in enumerate(zip(*df.apply(verification_model.diff_rows2, axis=1))):
        if i not in accpeted_column_idxs: continue
        df[ALL_OUTPUT_COLUMNS[i]] = column

    return df

def write_colored_wrong_case(df, ai_ocr_col_name = 'Predict by cannet_ocr',
                                        ca_col_name = 'Label', writer = None):
    # Initialize
    verification_model = Verification()
    verification_model.AI_OCR = ai_ocr_col_name
    verification_model.CORRECT_ANSWER = ca_col_name
    verification_model.strip = False
    verification_model.normalize = False
    verification_model.correct_dict = None

    verification_model.color_wrong_letter(writer, "Sheet1", df[ai_ocr_col_name], df[FORMATTING], 'red', df)
    verification_model.color_false_field(writer, "Sheet1", df[T_F], 'red', ('L', 'F'), df)


if __name__ == "__main__":
    """
    Testing
    """

    input_excel_fn = "./../1573033149_IP_Daiichi_training_4.xlsx"
    df = pd.read_excel(input_excel_fn)

    verification_model = Verification()
    verification_model.AI_OCR = 'Predict by cannet_ocr'
    verification_model.CORRECT_ANSWER = 'Label'
    verification_model.strip = False
    verification_model.normalize = False
    verification_model.correct_dict = None

    result = verification_model.diff_rows2(df)
    print (result)
    print (ALL_OUTPUT_COLUMNS)

    accpeted_column_names = ['T/F', 'RIGHT -> WRONG', 'Formatting']
    accpeted_column_idxs  = [list(ALL_OUTPUT_COLUMNS).index(column_name) for column_name in accpeted_column_names]

    for i, column in enumerate(zip(*df.apply(verification_model.diff_rows2, axis=1))):
        if i not in accpeted_column_idxs: continue
        df[ALL_OUTPUT_COLUMNS[i]] = column

    file_output = "excel_output.xlsx"
    writer = pd.ExcelWriter(file_output, engine='xlsxwriter')
    df.to_excel(writer, sheet_name='Sheet1', index=False)

    verification_model.color_wrong_letter(writer, "Sheet1", df[verification_model.AI_OCR], df[FORMATTING], 'red', df)
    verification_model.color_false_field(writer,  "Sheet1", df[T_F], 'red', ('L', 'F'), df)

    writer.close()