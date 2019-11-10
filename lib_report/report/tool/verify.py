#!/usr/bin/env python
# -*- coding: utf-8 -*-
import traceback
import os
import json
import string
import difflib
import xlsxwriter
import unicodedata
import numpy as np
import pandas as pd
from .accuracy import calculate_accuracy_by_char2

AI_OCR = 'AI OCR'
CORRECT_ANSWER = 'Correct Answer'
COMMON_ATTRIBUTES = ('File Name', 'Item ID', 'Type')

T_F = 'T/F'
FORMATTING = 'Formatting'
OCR_LETTERS = 'OCR letters'
NUMBER_OF_LETTERS = 'Number of letters'
CORRECT_LETTERS = 'Correct letters'
CORRECT_LETTERS_LEVE = 'Correct letters leve'
LEVENSHTEIN = 'Levenshtein'
L_MEASURE = 'L_Measure'
F_MEASURE = 'F_Measure'

COMMON_COLUMN = (T_F, 'RIGHT -> WRONG', FORMATTING, 'RIGHT', OCR_LETTERS)
MEASURES = ['F', 'L']
EXPECTED_COLUMN = {
    'FL': (NUMBER_OF_LETTERS, LEVENSHTEIN, CORRECT_LETTERS_LEVE, L_MEASURE, CORRECT_LETTERS, F_MEASURE, *COMMON_COLUMN),
    'LF': (NUMBER_OF_LETTERS, LEVENSHTEIN, CORRECT_LETTERS_LEVE, L_MEASURE, CORRECT_LETTERS, F_MEASURE, *COMMON_COLUMN),
    'F': (NUMBER_OF_LETTERS, CORRECT_LETTERS, F_MEASURE, *COMMON_COLUMN),
    'L': (NUMBER_OF_LETTERS, LEVENSHTEIN, CORRECT_LETTERS_LEVE, L_MEASURE, *COMMON_COLUMN),
}
ALL_OUTPUT_COLUMNS = (NUMBER_OF_LETTERS, LEVENSHTEIN, CORRECT_LETTERS_LEVE, L_MEASURE, CORRECT_LETTERS, F_MEASURE,
                      *COMMON_COLUMN)

EXPECTED_COLUMN_SUMMARY_SHEET = {
    'FL': (CORRECT_LETTERS, 'Accuracy by letter (%)', CORRECT_LETTERS_LEVE, 'Accuracy by letter leve (%)'),
    'LF': (CORRECT_LETTERS, 'Accuracy by letter (%)', CORRECT_LETTERS_LEVE, 'Accuracy by letter leve (%)'),
    'F': (CORRECT_LETTERS, 'Accuracy by letter (%)'),
    'L': (CORRECT_LETTERS_LEVE, 'Accuracy by letter leve (%)'),
}


class Verification:
    AI_OCR = 'AI OCR'
    CORRECT_ANSWER = 'Correct Answer'

    def __init__(self, correct_dict_file='correct_dictionary.json'):
        print('Calculate accuracy between columns `{}` and `{}`'. format(self.AI_OCR, self.CORRECT_ANSWER))
        self.correct_dict = {}
        self.correct_dict_file = os.path.join(os.path.dirname(__file__), correct_dict_file)
        self.get_correct_dict()
        self.strip = False
        self.normalize = False

    def get_correct_dict(self):
        try:
            with open(self.correct_dict_file, 'r') as f:
                self.correct_dict = json.load(f)
        except:
            pass
        return self.correct_dict

    def set_correct_dict(self, correct_dict):
        if isinstance(correct_dict, dict):
            self.correct_dict = correct_dict

    @staticmethod
    def strip_value(old_string):
        new_string = str(old_string)
        while new_string.startswith(' ') or new_string.startswith('\n'):
            new_string = new_string.lstrip(' ').lstrip('\n')
        while new_string.endswith(' ') or new_string.endswith('\n'):
            new_string = new_string.rstrip(' ').rstrip('\n')
        return new_string

    def preprocess_value(self, old_string):
        if self.normalize:
            if '一' in old_string:
                index = old_string.find('一')
                new_string = unicodedata.normalize('NFKC', old_string[:index]) + '一' + unicodedata.normalize('NFKC',
                                                                                                             old_string[
                                                                                                             index + 1:])
            else:
                new_string = unicodedata.normalize('NFKC', old_string)
        else:
            new_string = old_string
        for key, values in self.get_correct_dict().items():
            for value in values:
                new_string = new_string.replace(value, key)
        if self.strip:
            new_string = self.strip_value(new_string)
        return new_string

    def levenshtein(self, s1, s2):
        if len(s1) < len(s2):
            return self.levenshtein(s2, s1)
        if len(s2) == 0:
            return len(s1)
        previous_row = range(len(s2) + 1)
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row
        return previous_row[-1]

    def preprocess_value_format(self, old_string):
        if self.normalize:
            if '一' in old_string:
                index = old_string.find('一')
                new_string = unicodedata.normalize('NFKC', old_string[:index]) + '一' + unicodedata.normalize('NFKC',
                                                                                                             old_string[
                                                                                                             index + 1:])
            else:
                new_string = unicodedata.normalize('NFKC', old_string)
        else:
            new_string = old_string
        if self.strip:
            new_string = self.strip_value(new_string)
        return new_string

    def diff_rows(self, df):
        s1 = self.preprocess_value(str(df[self.AI_OCR]))
        s2 = self.preprocess_value(str(df[self.CORRECT_ANSWER]))
        diff = difflib.SequenceMatcher(None, s1, s2)
        result = ''
        result1 = ''
        format_pairs = ''
        if s2 == '' and len(s1) > 0:
            result = 'OCR no value field'
        else:
            for tag, i1, i2, j1, j2 in diff.get_opcodes():
                print_s1 = 'SPACE' if s1[i1:i2] == ' ' else s1[i1:i2]
                print_s2 = 'SPACE' if s2[j1:j2] == ' ' else s2[j1:j2]
                print_s1 = 'ENTER' if s1[i1:i2] == '\n' else print_s1
                print_s2 = 'ENTER' if s2[j1:j2] == '\n' else print_s2
                if tag == 'replace':
                    result = result + 'Mistake {} -> {}\n'.format(print_s2, print_s1)
                    # format_pairs.append(('r', i1, i2))
                    format_pairs = format_pairs + " ('r',{},{})".format(i1, i2)
                elif tag == 'delete':
                    result = result + 'Excess {}(position {})\n'.format(print_s1, str(i1))
                    # format_pairs.append(('r', i1, i2))
                    format_pairs = format_pairs + " ('r',{},{})".format(i1, i2)
                elif tag == 'insert':
                    if len(s1) == 0:
                        result = result + 'Can not OCR'
                    else:
                        result = result + 'Lost {}(position {})\n'.format(print_s2, str(j1))
                elif tag == 'equal':
                    result1 = result1 + '{}'.format(print_s2)
        match_n = 0
        true_n = len(s2)
        pred_n = len(s1)
        for block in diff.get_matching_blocks():
            match_n = match_n + block[2]
        if match_n == len(s2) and len(s1) == len(s2):
            is_true = 'T'
        else:
            is_true = 'F'
        if 'Type' in df and df['Type'] == 'CHECKBOX':
            match_n = 0
            true_n = 0

        leve = len(s2) - self.levenshtein(s1, s2)
        leve = 0 if leve < 0 else leve

        if true_n + pred_n == 0:
            f_measure = 0
        else:
            f_measure = round((200 * match_n / (true_n + pred_n)), 2)
        if true_n > 0:
            l_measure = round((leve / true_n) * 100, 2)
        else:
            # l_measure = 0 if pred_n > 0 else 1
            l_measure = 0
        return true_n, self.levenshtein(s1, s2), leve, l_measure,  match_n, f_measure, is_true, result, format_pairs, result1, pred_n

    @staticmethod
    def compare_string(str1, str2):
        return calculate_accuracy_by_char2(str1, str2)[-1]

    def diff_rows2(self, df):
        s1 = self.preprocess_value(str(df[self.AI_OCR]))
        s2 = self.preprocess_value(str(df[self.CORRECT_ANSWER]))
        diffs = self.compare_string(s1, s2)
        result = ''
        result1 = ''
        format_pairs = ''
        match_n = 0
        if s2 == '' and len(s1) > 0:
            result = 'OCR no value field'
        else:
            tags = []
            for diff in diffs:
                for tag, i1, i2, j1, j2 in diff[2]:
                    if (tag, diff[0][0] + i1) in tags:
                        continue
                    if i1 >= diff[3]:
                        continue
                    tags.append((tag, diff[0][0] + i1))
                    # print(tag, i1, i2, j1, j2)
                    ss1 = s1[diff[0][0]:]
                    ss2 = s2[diff[0][1]:]
                    print_s1 = 'SPACE' if ss1[i1:i2] == ' ' else ss1[i1:i2]
                    print_s2 = 'SPACE' if ss2[j1:j2] == ' ' else ss2[j1:j2]
                    print_s1 = 'ENTER' if ss1[i1:i2] == '; ' else print_s1
                    print_s2 = 'ENTER' if ss2[j1:j2] == '; ' else print_s2
                    if tag == 'replace':
                        result = result + 'Mistake {} -> {}; '.format(print_s2, print_s1)
                        # format_pairs.append(('r', i1, i2))
                        format_pairs = format_pairs + " ('r',{},{})".format(diff[0][0] + i1, diff[0][0] + i2)
                    elif tag == 'delete':
                        result = result + 'Excess {}(position {}); '.format(print_s1, str(diff[0][0] + i1))
                        # format_pairs.append(('r', i1, i2))
                        format_pairs = format_pairs + " ('r',{},{})".format(diff[0][0] + i1, diff[0][0] + i2)
                    elif tag == 'insert':
                        if len(s1) == 0:
                            result = result + 'Can not OCR'
                        else:
                            result = result + 'Lost {}(position {}); '.format(print_s2, str(diff[0][1] + j1))
                    elif tag == 'equal':
                        result1 = result1 + '{}'.format(print_s2)
                for block in diff[1]:
                    match_n = match_n + block[2]

        true_n = len(s2)
        pred_n = len(s1)
        if match_n == len(s2) and len(s1) == len(s2):
            is_true = 'T'
        else:
            is_true = 'F'
        if 'Type' in df and df['Type'] == 'CHECKBOX':
            match_n = 0
            true_n = 0

        leve = len(s2) - self.levenshtein(s1, s2)
        leve = 0 if leve < 0 else leve

        if true_n + pred_n == 0:
            f_measure = 0
        else:
            f_measure = round((200 * match_n / (true_n + pred_n)), 2)
        if true_n > 0:
            l_measure = round((leve / true_n) * 100, 2)
        else:
            l_measure = 0 if pred_n > 0 else 1
        # Return: ALL_OUTPUT_COLUMNS
        return true_n, self.levenshtein(s1, s2), leve, l_measure, match_n, f_measure, is_true, result, format_pairs, result1, pred_n

    def color_wrong_letter(self, writer, sheet_name, df_value, df_format, color, df):
        workbook = writer.book
        worksheet = writer.sheets[sheet_name]
        color = workbook.add_format({'color': color})
        ind = df.columns.get_loc(self.AI_OCR)
        for row_num, (sequence, formating) in enumerate(zip(df_value, df_format)):
            if len(formating) == 0:
                continue
            else:
                result = []
                formating = formating.split(' ')
                formating = [eval(fm) for fm in formating[1:]]
                color_p = [n for fm in formating for n in list(
                    range(fm[1], fm[2]))]
                for index, s in enumerate(self.preprocess_value_format(str(sequence))):
                    if index in color_p:
                        result.append(color)
                        result.append(s)
                    else:
                        result.append(s)
                # Update index column will color
                worksheet.write_rich_string(row_num + 1, ind, *result)
        # worksheet.set_column('Y:Z', None, None, {'hidden': True})
        return True

    @staticmethod
    def color_false_field( writer, sheet_name, df_field, color, measures, df):
        workbook = writer.book
        worksheet = writer.sheets[sheet_name]
        num_row = len(df_field) + 1
        tem = string.ascii_uppercase[df.columns.get_loc('T/F')]
        color = workbook.add_format({'bg_color': color})
        worksheet.conditional_format(tem + '1:' + tem + '%d' % (num_row), {'type': 'text',
                                                                           'criteria': 'containing',
                                                                           'value': 'F',
                                                                           'format': color})
        return True

    @staticmethod
    def accuracy_pivot(dftable, index='Type', measures=MEASURES):
        if index in dftable.columns:
            # count total field for each type
            df_total_field = pd.pivot_table(dftable,
                                            index=index,
                                            values=NUMBER_OF_LETTERS, aggfunc=len
                                            ).rename(index=str,
                                                     columns={NUMBER_OF_LETTERS: 'Total field'})
            if df_total_field.empty:
                df_total_field.insert(loc=0, column='Total field', value=0)
            # count total true field for each type
            df_crr_field = pd.pivot_table(dftable,
                                          index=index,
                                          values='T/F',
                                          aggfunc=lambda x: sum(x == 'T')
                                          ).rename(index=str, columns={T_F: 'Correct field'})
            if df_crr_field.empty:
                df_crr_field.insert(loc=0, column='Correct field', value=0)
            # count total (correct) letter for each type
            df_letters = pd.pivot_table(dftable,
                                        index=index,
                                        values=[NUMBER_OF_LETTERS, CORRECT_LETTERS, CORRECT_LETTERS_LEVE, OCR_LETTERS],
                                        aggfunc=np.sum
                                        ).rename(index=str,
                                                 columns={
                                                     NUMBER_OF_LETTERS: 'Total CA letters',
                                                     OCR_LETTERS: 'Total OCR letters'
                                                 })

            df_all = pd.concat((df_total_field, df_crr_field, df_letters), axis=1)

            df_all['Accuracy by field (%)'] = round((df_all['Correct field'] / df_all['Total field']) * 100, 2)
            df_all['Accuracy by letter (%)'] = round(
                df_all[CORRECT_LETTERS] / (df_all['Total CA letters'] + df_all['Total OCR letters']) * 200, 2)
            df_all['Accuracy by letter leve (%)'] = round(
                (df_all[CORRECT_LETTERS_LEVE] / df_all['Total CA letters']) * 100, 2)
            df_all = df_all[['Total field', 'Correct field', 'Accuracy by field (%)', 'Total CA letters',
                             'Total OCR letters', *EXPECTED_COLUMN_SUMMARY_SHEET[''.join(measures)]]]
            if '' in df_all.index:
                df_all.drop('', inplace=True)
            return df_all
        else:
            return None

    def run(self, file_input, file_output,
            ocr=AI_OCR, ca=CORRECT_ANSWER, measures=MEASURES, attributes=COMMON_ATTRIBUTES,
            correct_dict=None, strip=False, normalize=False):
        self.AI_OCR = ocr
        self.CORRECT_ANSWER = ca
        try:
            self.set_correct_dict(correct_dict)
            self.strip = strip
            self.normalize = normalize
            df = pd.read_excel(file_input, converters={self.AI_OCR: str, self.CORRECT_ANSWER:  str, **{_: str for _ in attributes}})
            df.fillna('', inplace=True)
            df1 = df.loc[:, attributes]
            df2 = pd.DataFrame(columns=None)
            df3 = pd.DataFrame(columns=None)
            if self.AI_OCR in df.columns:
                df1[self.AI_OCR] = df[self.AI_OCR]
                df1[self.CORRECT_ANSWER] = df[self.CORRECT_ANSWER]
                if strip:
                    df1[self.AI_OCR] = df1[self.AI_OCR].apply(lambda x: self.strip_value(x))
                for i, column in enumerate(zip(*df1.apply(self.diff_rows2, axis=1))):
                    df1[ALL_OUTPUT_COLUMNS[i]] = column

                if 'L' in measures:
                    accuracy_by_text_l = round((df1[CORRECT_LETTERS_LEVE].sum() / df1[NUMBER_OF_LETTERS].sum()) * 100, 2)

                    if (df1[T_F] == 'T').any():
                        accuracy_by_field = round(
                            (df1[T_F].value_counts()['T'] / df1[NUMBER_OF_LETTERS].count()) * 100, 2)
                        df2 = pd.DataFrame([['ACCURACY_BY_TEXT(Levenshtein)', df1[NUMBER_OF_LETTERS].sum(),
                                             df1[CORRECT_LETTERS_LEVE].sum(), accuracy_by_text_l],
                                            ['ACCURACY_BY_FIELD(Levenshtein)', df1[NUMBER_OF_LETTERS].count(),
                                             df1[T_F].value_counts()['T'], accuracy_by_field]])
                    else:
                        df2 = pd.DataFrame([['ACCURACY_BY_TEXT(Levenshtein)', df1[NUMBER_OF_LETTERS].sum(),
                                             df1[CORRECT_LETTERS_LEVE].sum(), accuracy_by_text_l],
                                            ['ACCURACY_BY_FIELD(Levenshtein)', df1[NUMBER_OF_LETTERS].count(), 0, 0]])

                if 'F' in measures:
                    pl = df1[OCR_LETTERS].sum()
                    tl = df1[NUMBER_OF_LETTERS].sum()
                    cl = df1[CORRECT_LETTERS].sum()
                    accuracy_by_text = round((200 * cl / (pl + tl)), 2) # F-Measure
                    if (df1[T_F] == 'T').any():
                        accuracy_by_field = round(
                            (df1[T_F].value_counts()['T'] / df1[NUMBER_OF_LETTERS].count()) * 100, 2)
                        df3 = pd.DataFrame([['ACCURACY_BY_TEXT(F-Measure)', tl, pl, accuracy_by_text],
                                            ['ACCURACY_BY_FIELD(F-Measure)', df1[NUMBER_OF_LETTERS].count(),
                                             df1[T_F].value_counts()['T'], accuracy_by_field]])
                    else:
                        df3 = pd.DataFrame([['ACCURACY_BY_TEXT(F-Measure)', tl, pl, accuracy_by_text],
                                            ['ACCURACY_BY_FIELD(F-Measure)', df1[NUMBER_OF_LETTERS].count(), 0, 0]])

            writer = pd.ExcelWriter(file_output, engine='xlsxwriter')

            if self.AI_OCR in df.columns:
                expected_columns = EXPECTED_COLUMN[''.join(measures)]
                col_idx = df.columns.get_loc(self.CORRECT_ANSWER) + 1
                for i, column in enumerate(expected_columns):
                    df.insert(loc=col_idx + i, column=column, value=df1[column])
                df.to_excel(writer, sheet_name='Sheet1', index=False)
                row_idx = len(df[self.AI_OCR]) + 1
                if 'L' in measures:
                    df2.to_excel(writer, sheet_name='Sheet1', startrow=row_idx,
                                 startcol=df.columns.get_loc(self.AI_OCR), header=False,
                                 index=False)
                    row_idx += 3
                if 'F' in measures:
                    df3.to_excel(writer, sheet_name='Sheet1', startrow=row_idx,
                                 startcol=df.columns.get_loc(self.AI_OCR), header=False,
                                 index=False)

                for attribute in attributes:
                    df[attribute] = df1[attribute]

                self.color_wrong_letter(writer, 'Sheet1', df[self.AI_OCR], df1[FORMATTING], 'red', df)
                self.color_false_field(writer, 'Sheet1', df[T_F], 'red', measures, df)

                # Accuracy by field, file, id
                df[CORRECT_LETTERS] = df1[CORRECT_LETTERS]
                df[CORRECT_LETTERS_LEVE] = df1[CORRECT_LETTERS_LEVE]
                for attribute in attributes:
                    res = self.accuracy_pivot(df, attribute)
                    if res is not None:
                        res.to_excel(writer, sheet_name='Accuracy_by_' + attribute.replace(' ', '_'))
            writer.save()
            return True, None
        except Exception as ex:
            raise(ex)
            # return False, 'Error!'
