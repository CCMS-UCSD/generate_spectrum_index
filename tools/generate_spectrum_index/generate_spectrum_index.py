from pyteomics import mzxml, mzml, mgf
from collections import namedtuple
import csv
import argparse
import sys
from pathlib import Path
import gzip

Spectrum = namedtuple('Spectrum', 'nativeid mslevel ms2plusindex')

def arguments():
    parser = argparse.ArgumentParser(description='Generate index from spectrum file')
    parser.add_argument('-i','--input_spectrum', type = str, help='Single spectrum file of types mzML, mzXML, or mgf.')
    parser.add_argument('-o','--output_folder', type = str, help='Folder to write out tab-separated index file to write out')
    if len(sys.argv) < 2:
        parser.print_help()
        sys.exit(1)
    return parser.parse_args()

def main():
    args = arguments()

    input = Path(args.input_spectrum)

    input_filetype = ''.join(input.suffixes)

    print(input_filetype)
    output = Path(args.output_folder).joinpath(input.name.replace(input_filetype, '.scans'))

    # List of output spectra
    spectra = []

    # Initialize MS2+ index at 0
    ms2plus_scan_idx = 0

    # In the highly unlikely chance that there are MS1 scans in the MGF set warning flag
    mgf_ms1_warn = False

    if input_filetype == '.mzXML':
        with open(input, 'rb') as mzxml_file:
            with mzxml.read(mzxml_file) as reader:
                for s in reader:
                    # Always use scan= for nativeID for mzXML
                    spectra.append(Spectrum('scan={}'.format(s['num']),int(s['msLevel']),-1 if int(s['msLevel']) == 1 else ms2plus_scan_idx))
                    # Increment MS2+ counter, if spectrum was MS2+
                    if int(s.get('msLevel',2)) > 1:
                        ms2plus_scan_idx += 1
    elif input_filetype == '.mzML':
        with open(input, 'rb') as mzml_file:
            with mzml.read(mzml_file) as reader:
                for s in reader:
                    # Always use given nativeID for mzML
                    spectra.append(Spectrum(s['id'],int(s['ms level']),-1 if int(s['ms level']) == 1 else ms2plus_scan_idx))
                    # Increment MS2+ counter, if spectrum was MS2+
                    if int(s.get('ms level',2)) > 1:
                        ms2plus_scan_idx += 1
    elif input_filetype == '.mzML.gz':
        with gzip.open(input, 'rb') as mzmlgz_file:
            with mzml.read(mzmlgz_file) as reader:
                for s in reader:
                    # Always use given nativeID for mzML
                    spectra.append(Spectrum(s['id'],int(s['ms level']),-1 if int(s['ms level']) == 1 else ms2plus_scan_idx))
                    # Increment MS2+ counter, if spectrum was MS2+
                    if int(s.get('ms level',2)) > 1:
                        ms2plus_scan_idx += 1
    elif input_filetype == '.mgf':
        all_scan_idx = 0
        with open(input) as mgf_file:
            with mgf.read(mgf_file) as reader:
                for s in reader:
                    # Check for MSLEVEL but assume 2
                    ms_level = int(s['params'].get('mslevel', 2))

                    scan_num = s['params'].get('scans')
                    if scan_num:
                        # If SCANS is in the mgf, then use scan= nativeID format
                        native_id = ','.join('scan={}'.format(s) for s in scan_num.split(','))
                    else:
                        # Format as an index= nativeID
                        native_id = 'index={}'.format(all_scan_idx)

                    spectra.append(Spectrum(native_id,ms_level,-1 if ms_level == 1 else ms2plus_scan_idx))

                    # In the highly unlikely chance that there are MS1 scans in the MGF increment global scan idx
                    all_scan_idx += 1

                    if ms_level > 1:
                        ms2plus_scan_idx += 1

        # Check if there are extra scans, that aren't MS2+
        if ms2plus_scan_idx < all_scan_idx:
            print("MS1s found in MGF file, proceed with caution!")

    with open(output, 'w') as f:
        r = csv.writer(f, delimiter = '\t')
        for spectrum in spectra:
            r.writerow(list(spectrum))

if __name__ == "__main__":
    main()
