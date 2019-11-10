import difflib


def get_matching_block(str1, str2):
    diff = difflib.SequenceMatcher(None, str1, str2)
    return diff.get_matching_blocks(), diff.get_opcodes()


def get_matching_block2(str1, str2, chunk=10, allow_miss=5):
    """Calculate accuracy by char of 2 string"""
    total_letters = len(str1)
    ocr_letters = len(str2)
    if total_letters == 0 and ocr_letters == 0:
        return []

    chunks = []
    total_chunk1 = 0
    total_chunk2 = 0

    while total_chunk1 < total_letters:
        block1 = str1[total_chunk1:total_chunk1 + chunk]
        if total_letters <= total_chunk1 + chunk and total_chunk2 + chunk < ocr_letters:
            block2 = str2[total_chunk2:ocr_letters]
        else:
            block2 = str2[total_chunk2:total_chunk2 + chunk]
        # print(block1, '  ---  ', block2)
        diff = difflib.SequenceMatcher(None, block1, block2)
        matching_blocks = diff.get_matching_blocks()

        if len(matching_blocks) > 1:
            last_matching_block = matching_blocks[-2]
            remain_letter1 = chunk - last_matching_block[0] - last_matching_block[2]
            remain_letter2 = chunk - last_matching_block[1] - last_matching_block[2]
        else:
            remain_letter1 = chunk - allow_miss
            remain_letter2 = chunk - allow_miss
        chunks.append(((total_chunk1, total_chunk2), matching_blocks, diff.get_opcodes(), chunk - remain_letter1))
        total_chunk1 = total_chunk1 + chunk - remain_letter1
        total_chunk2 = total_chunk2 + chunk - remain_letter2

    return chunks


def calculate_accuracy_by_char(str1, str2, matching_blocks):
    """Calculate accuracy by char of 2 string"""
    total_letters = len(str1)
    ocr_letters = len(str2)
    if total_letters == 0 and ocr_letters == 0:
        acc_by_char = 1.0
        return acc_by_char
    correct_letters = 0
    for block in matching_blocks:
        correct_letters = correct_letters + block[2]
    # print(correct_letters)
    if ocr_letters == 0:
        acc_by_char = 0
    elif correct_letters == 0:
        acc_by_char = 0
    else:
        acc_1 = correct_letters / total_letters
        acc_2 = correct_letters / ocr_letters
        acc_by_char = 2 * (acc_1 * acc_2) / (acc_1 + acc_2)
    return float(acc_by_char)


def calculate_accuracy_by_char1(str1, str2):
    """Calculate accuracy by char of 2 string"""
    total_letters = len(str1)
    ocr_letters = len(str2)
    if total_letters == 0 and ocr_letters == 0:
        acc_by_char = 1.0
        return acc_by_char
    diff = difflib.SequenceMatcher(None, str1, str2)
    correct_letters = 0
    for block in diff.get_matching_blocks():
        correct_letters = correct_letters + block[2]
    # print(correct_letters)
    if ocr_letters == 0:
        acc_by_char = 0
    elif correct_letters == 0:
        acc_by_char = 0
    else:
        acc_1 = correct_letters / total_letters
        acc_2 = correct_letters / ocr_letters
        acc_by_char = 2 * (acc_1 * acc_2) / (acc_1 + acc_2)
    return float(acc_by_char)


def calculate_accuracy_by_char2(str1, str2):
    """Calculate accuracy by char of 2 string"""
    chunk_sizes = [10, 20, 40, 80]
    allow_miss = 5
    acc = 0
    best_chunk_size = 10
    best_chunks = []
    max_len = len(str(str1))
    chunk_sizes.append(max_len)
    chunk_sizes = sorted(chunk_sizes)
    # print(max_len)
    for chunk_size in chunk_sizes:
        if chunk_size > max_len:
            break
        print(chunk_size)
        chunks = get_matching_block2(str1, str2, chunk_size, allow_miss)
        matching_blocks = [_ for chunk in chunks for _ in chunk[1]]
        acc_tmp = calculate_accuracy_by_char(str1, str2, matching_blocks)
        if acc_tmp > acc:
            acc = acc_tmp
            best_chunk_size = chunk_size
            best_chunks = chunks

    return acc, best_chunk_size, best_chunks


if __name__=="__main__":
    # print(calculate_accuracy_by_char('変更前11.3.2.1. 通常Is許可判', '変更前11.3.2.1.通常I 許可判定'))
    ocr = '''Tsuzuki-DensanAbcShanghaiMade inTaiwan,Philippines,JapanPallet 1/1 (21 Carton)'''
    ca = '''ShanghaiMade inTaiwan,Philippines,JapanPallet 1/1 (21 Carton)Tsuzuki-Densan2019/06/28'''
    print(calculate_accuracy_by_char2(ocr, ca)[:2])
    print(calculate_accuracy_by_char1(ocr, ca))
