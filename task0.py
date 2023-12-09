def parse_xml(string):
    children = []
    while string:
        string = string.strip()

        start_tag_start = string.find('<')
        start_tag_end = string.find('>')

        if string.startswith("<xml?"):
            string = string[start_tag_end + 1:].strip()
            continue
        if start_tag_start != -1 and start_tag_end != -1 and start_tag_start < start_tag_end:
            tag_name_start = start_tag_start + 1
            tag_name_end = start_tag_end if (string.find(' ', tag_name_start) == -1
                                             or string.find(' ', tag_name_start) > start_tag_end) else string.find(' ', tag_name_start)
            tag_name = string[tag_name_start:tag_name_end]

            end_tag_start = string.find('</' + tag_name + '>', tag_name_start + 1)
            test_for_duplicate = string.find('<' + tag_name + '>', tag_name_start + 1)
            while test_for_duplicate < end_tag_start and test_for_duplicate != -1:
                end_tag_start = string.find('</' + tag_name + '>', end_tag_start + 1)
                test_for_duplicate = string.find('<' + tag_name + '>', test_for_duplicate + 1)
            end_tag_end = end_tag_start + len(tag_name) + 3

            attributes = {}
            attr_start = string.find(' ', tag_name_start)
            while True:
                attr_name_start = string.find(' ', attr_start, start_tag_end)
                if attr_name_start == -1:
                    break
                attr_name_end = string.find('=', attr_name_start)
                if attr_name_end == -1:
                    break
                attr_name = string[attr_name_start:attr_name_end].strip()
                attr_value_start = string.find('"', attr_name_end)
                if attr_value_start == -1:
                    break
                attr_value_end = string.find('"', attr_value_start + 1)
                if attr_value_end == -1:
                    break
                attr_value = string[attr_value_start + 1:attr_value_end]
                attributes[attr_name] = attr_value
                attr_start = attr_value_end

            text = ''
            text_start = start_tag_end + 1
            while string[text_start].isspace():
                text_start += 1
            if not string[text_start] == '<':
                text_end = end_tag_start
                text = string[text_start:text_end].strip()

            inner_xml_start = start_tag_end + 1
            inner_xml_end = end_tag_start
            inner_xml = string[inner_xml_start:inner_xml_end]
            children.append({
                'name': tag_name,
                'attributes': attributes,
                'text': text,
                'children': parse_xml(inner_xml)
            })

            while end_tag_end < len(string):
                xml_string_nextstart = string.find('<', end_tag_end + 1)
                xml_string_nextstart_end = string.find('>', xml_string_nextstart + 1)
                xml_string_nextstart_nameend = string.find(' ', xml_string_nextstart + 1)
                if xml_string_nextstart_nameend == -1 or xml_string_nextstart_nameend > xml_string_nextstart_end:
                    xml_string_nextstart_nameend = xml_string_nextstart_end
                tagname = string[xml_string_nextstart + 1:xml_string_nextstart_nameend]
                xml_closetagname = string.find('</' + tagname + '>', xml_string_nextstart_end + 1)
                test_for_duplicate = string.find('<' + tagname + '>', xml_string_nextstart_end + 1)
                while test_for_duplicate < xml_closetagname and test_for_duplicate != -1:
                    xml_closetagname = string.find('</' + tagname + '>', xml_closetagname + 1)
                    test_for_duplicate = string.find('<' + tagname + '>', test_for_duplicate + 1)
                xml_string_nextstop = xml_closetagname + len(tagname) + 3
                if string[xml_string_nextstart + 1] == '/':
                    break
                single_xml = string[xml_string_nextstart:xml_string_nextstop]
                parsed_xml = parse_xml(single_xml)
                if len(parsed_xml) == 1:
                    children.append(parsed_xml[0])
                end_tag_end = xml_string_nextstop
        return children

    return children


def find_nth(haystack, needle, n):
    start = haystack.find(needle)
    while start >= 0 and n > 1:
        start = haystack.find(needle, start + len(needle))
        n -= 1
    return start


def to_json_str(elements_xml, tab_count=0, is_first_iter=True):
    result = ''
    is_array = False
    union = union_by_name(elements_xml)
    if len(union) < len(elements_xml):
        is_array = True
    if is_first_iter:
        result += '{\n'
        tab_count += 1
    if is_array:
        for union_array_index in union:
            matched_non_single_element = len(union[union_array_index]) > 1
            if matched_non_single_element:
                result += '\t' * tab_count + '\"' + union_array_index + '\" : [\n'
                tab_count += 1
            for element in union[union_array_index]:
                if matched_non_single_element:
                    result += '\t' * tab_count + '{\n'
                    tab_count += 1
                for atr in element['attributes']:
                    result += '\t' * tab_count + '\"' + atr + '\":\"' + element['attributes'][atr] + '\",\n'
                if element['text']:
                    result += '\t' * tab_count + '\"' + element['name'] + '\":\"' + element['text'] + '\",\n'
                if element['children']:
                    result += to_json_str(element['children'], tab_count, False)
                if matched_non_single_element:
                    result = result.rstrip(',\n')
                    result += '\n'
                    tab_count -= 1
                    result += '\t' * tab_count + '},\n'
            if matched_non_single_element:
                result = result.rstrip(',\n')
                result += '\n'
            if len(union[union_array_index]) > 1:
                tab_count -= 1
                result += '\t' * tab_count + '],\n'
        result = result.rstrip(',\n')
        result += '\n'
    else:
        for element in elements_xml:
            if len(element['children']) > 1:
                result += '\t' * tab_count + '\"' + element['name'] + '\": {\n'
                tab_count += 1
            for atr in element['attributes']:
                result += '\t' * tab_count + '\"' + atr + '\":\"' + element['attributes'][atr] + '\",\n'
            if element['text']:
                result += '\t' * tab_count + '\"' + element['name'] + '\":\"' + element['text'] + '\",\n'
            if element['children']:
                result += to_json_str(element['children'], tab_count, False)
            if len(element['children']) > 1:
                tab_count -= 1
                result += '\t' * tab_count + '},\n'
        result = result.rstrip(',\n')
        result += '\n'
    if is_first_iter:
        result += '}\n'
    return result


def union_by_name(list_data):
    result_dict = {}

    for value in list_data:
        name = value["name"]
        if name in result_dict:
            result_dict[name].append(value)
        else:
            result_dict[name] = [value]

    return result_dict


elements_from_xml = parse_xml(open('schedule.xml').read())
open('output.json', mode='w').write(to_json_str(elements_from_xml))