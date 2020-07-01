import glob
import pandas as pd
import sys
from pathlib import Path

def arguments():
    parser = argparse.ArgumentParser(description='Generate index from spectrum file')
    parser.add_argument('input_folder_results', type = Path, help='Input folder of results.')
    parser.add_argument('proteosafe_paramxml', type = Path, help='Default MSlevel')
    parser.add_argument('output_summarize_file', type = Path, help='Folder to write out tab-separated index file to write out')
    
    parser.set_defaults(suppress_errors=False)
    return parser.parse_args()

def main():
    args = arguments()
    print(args)


if __name__ == "__main__":
    main()