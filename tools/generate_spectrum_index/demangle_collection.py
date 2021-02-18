from pathlib import Path
import xmltodict
import argparse
from csv import DictReader
from collections import defaultdict
import sys

#https://github.com/CCMS-UCSD/ProteoSAFe-LiveSearch/blob/master/src/main/java/edu/ucsd/livesearch/util/Commons.java#L63-L64
PLACEHOLDER_DELIMITER = 'X9ZxTU0xlREnVkmE'

def arguments():
    parser = argparse.ArgumentParser(description='Demangle collection as aliases to folder', exit_on_error=False)
    parser.add_argument('-p','--params', type = Path, help='ProteoSAFe params.xml', required = True)
    parser.add_argument('-i','--input_folder', type = Path, help='Input folder path', required = True)
    parser.add_argument('-o','--output_folder', type = Path, help='Output folder path', required = True)
    parser.add_argument('-r','--reverse', dest='reverse', action='store_true', help='Flag to demangle file collection')
    parser.add_argument('-s','--preserve_suffix', dest='preserve_suffix', action='store_true', help='Flag to save suffix from demangled file collection')
    return parser.parse_args()

def read_params(input_file):
    return get_mangled_file_mapping(parse_xml_file(input_file))

def get_mangled_file_mapping(params):
    all_mappings = params["upload_file_mapping"]
    mangled_mapping = {}
    demangled_mapping = {}
    for mapping in all_mappings:
        splits = mapping.split("|")
        mangled_name = splits[0]
        original_name = splits[1].replace('/',PLACEHOLDER_DELIMITER)
        mangled_mapping[mangled_name] = Path(original_name)
        demangled_mapping[original_name] = Path(mangled_name)
    return mangled_mapping, demangled_mapping

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

    # don't fail on error, since it is likely to be run without inputs
    try:
        args = arguments()
    except argparse.ArgumentError as e:
        print(repr(e))
        sys.exit(0)

    mangled_mapping, demangled_mapping = read_params(args.params)

    for input_file in args.input_folder.glob('*'):
        input_path = args.input_folder.joinpath(input_file.name).absolute()

        if args.reverse:
            if args.preserve_suffix:
                suffix = input_file.suffix
                input_file_no_suffix = input_file.with_suffix('').name
                output_file = demangled_mapping.get(input_file_no_suffix).with_suffix(suffix)
            else:
                output_file = demangled_mapping.get(input_file.name)
        else:
            output_file = mangled_mapping.get(input_file.name)

        output_path = args.output_folder.joinpath(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.symlink_to(input_path)

if __name__ == "__main__":
    main()
