import glob
import pandas as pd
import sys
from pathlib import Path
import argparse
import os
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
        mangled_mapping[mangled_name] = original_name
        mangled_mapping[os.path.splitext(mangled_name)[0]] = original_name

    return mangled_mapping

def arguments():
    parser = argparse.ArgumentParser(description='Generate index from spectrum file')
    parser.add_argument('input_folder_results', type = Path, help='Input folder of results.')
    parser.add_argument('proteosafe_paramxml', type = Path, help='Default MSlevel')
    parser.add_argument('output_summarize_file', type = Path, help='Folder to write out tab-separated index file to write out')
    
    parser.set_defaults(suppress_errors=False)

    return parser.parse_args()

def main():
    args = arguments()
    
    input_files = glob.glob("{}/*".format(args.input_folder_results))
    proteosafe_args = parse_xml_file(args.proteosafe_paramxml)
    mangled_mapping = get_mangled_file_mapping(proteosafe_args)

    print(mangled_mapping)

    list_df = []
    for input_file in input_files:
        try:
            df = pd.read_csv(input_file, sep="\t", header=0, names=["identifier", "mslevel", "index"])
            df["filename"] = os.path.basename(input_file)
            list_df.append(df)
        except:
            pass

    merged_list_df = pd.concat(list_df)

    # Demangling
    record_list = merged_list_df.to_dict(orient="records")
    for record in record_list:
        filename = os.path.splitext(record["filename"])[0]
        real_filename = mangled_mapping[filename]
        record["proteosafe_filename"] = real_filename

    # Creating USI
    for record in record_list:
        usi = ""
        proteosafe_path = record["proteosafe_filename"]
        if record["proteosafe_filename"].startswith("MSV0000"):
            dataset_accession = proteosafe_path.split("/")[0]
            identifier_type = record["identifier"].split("=")[0]
            identifier_value = record["identifier"].split("=")[1]

            usi = "mzspec:{}:{}:{}:{}".format(dataset_accession, 
            os.path.basename(proteosafe_path), identifier_type, identifier_value)

            

            record["usi"] = usi

    merged_list_df = pd.DataFrame(record_list)
    merged_list_df.to_csv(args.output_summarize_file, sep="\t", index=False)



if __name__ == "__main__":
    main()