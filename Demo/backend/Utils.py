import re

def read_file(file_name):
    lines = []
    with open(file_name, "r", encoding="utf-8") as f:
        for line in f:
            lines.append(line)
    f.close()
    return lines

def get_first_number_from_string(line):

    match = re.search(r'\d+', line)
    if match:
        return int(match.group())
    return float('inf')

def create_dict_number_sorted(list):
    groups = {}
    for f in list:
        num = get_first_number_from_string(f)
        if num == float('inf'):
            continue  # Ignora i file senza un numero
        groups.setdefault(num, []).append(f)
    return sorted(groups.keys()), groups