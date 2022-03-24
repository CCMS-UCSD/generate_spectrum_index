import argparse
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

SCRIPT_DIRECTORY = os.path.dirname(os.path.realpath(__file__))
GENERATE_SPECTRUM_INDEX_SCRIPT = os.path.join(SCRIPT_DIRECTORY, "generate_spectrum_index.py")
MASSIVE_REPOSITORY_ROOT = "/data/massive"

def arguments():
    parser = argparse.ArgumentParser(description='Generate index from MassIVE peak list file')
    parser.add_argument('-s','--input_list', type=Path, help='Text input file containing list of paths to peak list files, one per line.')
    parser.add_argument('-o','--output_folder', type=Path, help='Output directory into which to write tab-separated index file')
    parser.add_argument('-l','--default_ms_level', type=str, help='Default MS level', default='0')
    parser.add_argument('-e','--error_folder', type=Path, help='Output directory into which to write error files')
    return parser.parse_args()

def main():
    args = arguments()
    if not (args.input_list and args.output_folder):
        print("Input spectra and output folder are required.")
        sys.exit(0)
    input_spectra = []
    with open(args.input_list) as file_reader:
        for line in file_reader:
            input_spectra.append(line.rstrip())
    for input_spectrum in input_spectra:
        input_spectrum_path = Path(input_spectrum)
        output = Path(args.output_folder).joinpath('/'.join(input_spectrum_path.with_suffix(input_spectrum_path.suffix + '.scans').parts[1:]))
        # check for a cached index file for this spectrum file
        cached_scans_file = None
        path = input_spectrum.split("/")
        # a valid dataset file will have at least 4 path elements:
        # demangledPeak/<dataset>/<collection>/<rest of path>
        if len(path) >= 4:
            # username should be the second path element, under the "demangledPeak" collection
            username = path[1]
            # only dataset files can have their index files cached
            if re.match("^MSV[0-9]{9}$", username):
                # determine cached scans file location, if present in the dataset
                cached_path = os.path.join(MASSIVE_REPOSITORY_ROOT, username, "ccms_metadata/ccms_peak", "/".join(path[3:]) + ".scans")
                if os.path.exists(cached_path):
                    cached_scans_file = cached_path
        if cached_scans_file is not None:
            print("Copying cached scans file [" + cached_scans_file + "] for input spectrum file [" + input_spectrum  + "] to intermediate location [" + str(output) + "].")
            output.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy(cached_scans_file, str(output))
        else:
            print("No cached scans file cound be found for input spectrum file [" + input_spectrum  + "] - generating now.")
            command = sys.executable + " \"" + GENERATE_SPECTRUM_INDEX_SCRIPT + "\" -i \"" + input_spectrum + "\" -o \"" + str(args.output_folder) + "\""
            if args.error_folder:
                command += " -e " + str(args.error_folder)
            if args.default_ms_level:
                command += " -l " + args.default_ms_level
            print("Command = [" + command + "]")
            subprocess.run(command, shell=True)

if __name__ == "__main__":
    main()
