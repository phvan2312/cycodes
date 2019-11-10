from report.tool import rw_json
from report.basic_report import BasicReport
import os


def test_basic_report():
    report = BasicReport('.')
    data = rw_json.read_json_file('test_data/diff_key_name_data.json')
    os.system('rm BasicReport*.xlsx')
    excel_file = report.save(data, 'BasicReport')
    assert os.path.isfile(excel_file)


if __name__ == "__main__":
    test_basic_report()
