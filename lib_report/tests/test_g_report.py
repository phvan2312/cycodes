from report.tool import rw_json
from report.g_report import GReport
import os


report = GReport('.')
data = rw_json.read_json_file('test_data/data.json')
os.system('rm GReport*.xlsx')
excel_file = report.save(data, 'GReport')
assert os.path.isfile(excel_file)