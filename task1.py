import xmltodict
import json

xml = open('task1_input.xml').read()
xml_dict = xmltodict.parse(xml)
open('task1_output.json', 'w').write(json.dumps(xml_dict, ensure_ascii=False, indent=4))