import glob
import pandas as pd
import sys
from pathlib import Path
import argparse

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

    list_df = []
    for input_file in input_files:
        try:
            df = pd.read_csv(input_file, sep="\t")
            list_df.append(df)
        except:
            pass

    merged_list_df = pd.concat(list_df)

    merged_list_df.to_csv(args.output_summarize_file, sep="\t", index=False)



if __name__ == "__main__":
    main()