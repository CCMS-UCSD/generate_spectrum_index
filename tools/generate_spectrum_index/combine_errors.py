import argparse
import sys
from pathlib import Path
import xmltodict
from collections import defaultdict

def parse_xml_file(input_filename):
    key_value_pairs = defaultdict(list)
    xml_obj = xmltodict.parse(open(input_filename).read())

    for parameter in xml_obj["parameters"]["parameter"]:
        name = parameter["@name"]
        value = parameter["#text"]
        key_value_pairs[name].append(value)

    return key_value_pairs

def get_mangled_file_mapping(parsed_paramxml):
    all_mappings = parsed_paramxml["upload_file_mapping"]
    mangled_mapping = {}
    for mapping in all_mappings:
        splits = mapping.split("|")
        mangled_name = splits[0]
        original_name = splits[1]
        mangled_mapping[Path(mangled_name).stem] = original_name

    return mangled_mapping

def arguments():
    parser = argparse.ArgumentParser(description='Generate index from spectrum file')
    parser.add_argument('-p','--proteosafe_paramxml', type = Path, help='params.xml from ProteoSAFe')
    parser.add_argument('-e','--error_folder', type = Path, help='Folder of error files')
    if len(sys.argv) < 2:
        parser.print_help()
        sys.exit(1)
    return parser.parse_args()

def main():
    args = arguments()

    proteosafe_args = parse_xml_file(args.proteosafe_paramxml)
    mangled_mapping = get_mangled_file_mapping(proteosafe_args)

    err_messages = []

    for err_file in args.error_folder.glob('*.err'):
        err_messages.append(mangled_mapping[err_file.stem])

    if len(err_messages) > 0:
        if_plural_is = 'is'
        if_plural_s = ''
        if len(err_messages) > 1:
            if_plural_is = 'are'
            if_plural_s = 's'
        print('There {} {} file{} that {} malformed.  Please check the following:\n'.format(if_plural_is, len(err_messages), if_plural_s, if_plural_is))
        print('\n'.join(['\t({}) {}'.format(i+1,err_message) for i, err_message in enumerate(err_messages)]))
        print('')
        sys.exit(1)

if __name__ == "__main__":
    main()
