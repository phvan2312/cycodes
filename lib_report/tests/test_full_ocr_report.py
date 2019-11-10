from report.tool import rw_json
from report import full_ocr_report
from tests.test_tool_verify import test_verification
import os


def test_full_ocr_report():
    data = rw_json.read_json_file('test_data/full_ocr_data.json')
    os.system('rm FullReport*.xlsx')
    # excel_file = full_ocr_report.make_report_no_image(data, 'FReport.xlsx')
    excel_file = full_ocr_report.report_line(data, 'FullReport')
    assert os.path.isfile(excel_file)
    image_paths = {
        "(仕様変更依頼書)TWBA_DAN0_001": {
            "page_0000": "test_data/image/(仕様変更依頼書)TWBA_DAN0_001/pages/0000_comp.png",
            "page_0001": "test_data/image/(仕様変更依頼書)TWBA_DAN0_001/pages/0001_comp.png",
            "page_0002": "test_data/image/(仕様変更依頼書)TWBA_DAN0_001/pages/0002_comp.png",
            "page_0003": "test_data/image/(仕様変更依頼書)TWBA_DAN0_001/pages/0003_comp.png",
            "page_0004": "test_data/image/(仕様変更依頼書)TWBA_DAN0_001/pages/0004_comp.png"
        }
    }
    excel_file = full_ocr_report.make_report_attach_image(data, image_paths, 'FullReportImage.xlsx')
    assert os.path.isfile(excel_file)

    label = {
        '(仕様変更依頼書)TWBA_DAN0_001': full_ocr_report.read_datapile_lable([
            'test_data/datapile_label/(仕様変更依頼書)TWBA_DAN0_001_1.json',
            'test_data/datapile_label/(仕様変更依頼書)TWBA_DAN0_001_2.json',
            'test_data/datapile_label/(仕様変更依頼書)TWBA_DAN0_001_3.json',
            'test_data/datapile_label/(仕様変更依頼書)TWBA_DAN0_001_4.json'
        ])
    }
    label_dpi = 600
    ocr_image_dpi = 200
    dpi_ratio = label_dpi/ocr_image_dpi
    # excel_file = full_ocr_report.make_report_acc(data, label, 'FReport_acc.xlsx', dpi_ratio=dpi_ratio)
    excel_file = full_ocr_report.report_matching(data, label, 'FullReport_matching', dpi_ratio=dpi_ratio)

    assert os.path.isfile(excel_file)

    test_verification(excel_file, 'FullReport_matching_verified.xlsx',
                      ca='CA',
                      ocr='OCR',
                      attributes=['FILE', 'PAGE'])


if __name__ == "__main__":
    test_full_ocr_report()