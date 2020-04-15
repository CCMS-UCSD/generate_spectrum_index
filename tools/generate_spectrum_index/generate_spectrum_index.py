from pyteomics import mzxml, mzml, mgf
from collections import namedtuple
import csv
import argparse
import sys

Spectrum = namedtuple('Spectrum', 'nativeid mslevel ms2plusindex')

def arguments():
    parser = argparse.ArgumentParser(description='Generate index from spectrum file')
    parser.add_argument('-i','--input_spectrum', type = str, help='Single spectrum file of types mzML, mzXML, or mgf.')
    parser.add_argument('-o','--output_index', type = str, help='Tab-separated index file to write out')
    if len(sys.argv) < 2:
        parser.print_help()
        sys.exit(1)
    return parser.parse_args()

def main():
    args = arguments()

    # Get filetype by looking at extension, this will not work for
    # .mzML.gz (but I'm not sure the parser can read them anyways)
    input_filetype = args.input_spectrum.split('.')[-1]

    # List of output spectra
    spectra = []

    # Initialize MS2+ index at 0
    ms2plus_scan_idx = 0

    # In the highly unlikely chance that there are MS1 scans in the MGF set warning flag
    mgf_ms1_warn = False

    if input_filetype == 'mzXML':
        with mzxml.read(args.input_spectrum) as reader:
            for s in reader:
                # Always use scan= for nativeID for mzXML
                spectra.append(Spectrum('scan={}'.format(s['num']),s['msLevel'],-1 if s['msLevel'] == 1 else ms2plus_scan_idx))
                # Increment MS2+ counter, if spectrum was MS2+
                if s['msLevel'] > 1:
                    ms2plus_scan_idx += 1
    elif input_filetype == 'mzML':
        precursor_func = lambda spectrum: float(s['precursorList']['precursor'][0]['isolationWindow']['isolation window target m/z'])
        with mzml.read(args.input_spectrum) as reader:
            for s in reader:
                # Always use given nativeID for mzML
                spectra.append(Spectrum(s['id'],s['ms level'],-1 if s['ms level'] == 1 else ms2plus_scan_idx))
                # Increment MS2+ counter, if spectrum was MS2+
                if s['ms level'] > 1:
                    ms2plus_scan_idx += 1
    elif input_filetype == 'mgf':
        all_scan_idx = 0
        with mgf.read(args.input_spectrum) as reader:
            for s in reader:
                # Check for MSLEVEL but assume 2
                ms_level = s['params'].get('mslevel', 2)

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

    with open(args.output_index, 'w') as f:
        r = csv.writer(f, delimiter = '\t')
        for spectrum in spectra:
            r.writerow(list(spectrum))

if __name__ == "__main__":
    main()
