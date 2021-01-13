from pathlib import Path
import xmltodict
import argparse
from csv import DictReader
from collections import defaultdict
import sys

#https://github.com/CCMS-UCSD/ProteoSAFe-LiveSearch/blob/master/src/main/java/edu/ucsd/livesearch/util/Commons.java#L63-L64
PLACEHOLDER_DELIMITER = 'X9ZxTU0xlREnVkmE'

def arguments():
    parser = argparse.ArgumentParser(description='Demangle collection as aliases to folder')
    parser.add_argument('-p','--params', type = Path, help='ProteoSAFe params.xml')
    parser.add_argument('-i','--input_folder', type = Path, help='Input folder path')
    parser.add_argument('-o','--output_folder', type = Path, help='Output folder path')
    if len(sys.argv) < 3:
        parser.print_help()
        sys.exit(1)
    return parser.parse_args()

def read_params(input_file):
    return get_mangled_file_mapping(parse_xml_file(input_file))

def get_mangled_file_mapping(params):
    all_mappings = params["upload_file_mapping"]
    mangled_mapping = {}
    for mapping in all_mappings:
        splits = mapping.split("|")
        mangled_name = splits[0]
        original_name = Path(splits[1].replace('/',PLACEHOLDER_DELIMITER))
        mangled_mapping[mangled_name] = original_name

    return mangled_mapping

def parse_xml_file(input_file):
    with open(input_file) as f:
        key_value_pairs = defaultdict(list)
        xml_obj = xmltodict.parse(f.read())

        #print(json.dumps(xml_obj["parameters"]))
        for parameter in xml_obj["parameters"]["parameter"]:
            name = parameter["@name"]
            value = parameter["#text"]
            key_value_pairs[name].append(value)

    return key_value_pairs

def main():
    args = arguments()
    file_mapping = read_params(args.params)

    for mangled in args.input_folder.glob('*'):
        input_path = args.input_folder.joinpath(mangled.name).absolute()
        output_file = file_mapping.get(mangled.name,mangled.name)
        output_path = args.output_folder.joinpath(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.symlink_to(input_path)

if __name__ == "__main__":
    main()
