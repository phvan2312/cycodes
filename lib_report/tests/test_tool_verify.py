from report.tool.verify import Verification
import os


def test_verification(file_input='test_data/report.xlsx',
                      file_output='report_verified.xlsx',
                      ca='Correct Answer',
                      ocr='AI OCR',
                      attributes=('File Name', 'Item ID', 'Type'),
                      measures=('L', 'F')):
    verification = Verification()
    print(verification.correct_dict)
    if os.path.isfile(file_output):
        os.remove(file_output)
    correct_dict=None
    is_strip=False
    is_normalize=False
    verification.run(file_input, file_output,
                     ca=ca,
                     ocr=ocr,
                     attributes=attributes,
                     measures=measures,
                     correct_dict=correct_dict, strip=is_strip, normalize=is_normalize)
    assert os.path.isfile(file_output)

if __name__ == "__main__":
    test_verification()