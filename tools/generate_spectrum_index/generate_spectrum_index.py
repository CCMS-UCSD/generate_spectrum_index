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
    input_filetype = args.input_spectrum.split('.')[-1]

    spectra = []
    ms2plus_scan_idx = 0

    if input_filetype == 'mzXML':
        with mzxml.read(args.input_spectrum) as reader:
            for s in reader:
                if s['msLevel'] > 1:
                    ms2plus_scan_idx += 1
                spectra.append(Spectrum('scan={}'.format(s['num']),s['msLevel'],-1 if s['msLevel'] == 1 else ms2plus_scan_idx))
    elif input_filetype == 'mzML':
        precursor_func = lambda spectrum: float(s['precursorList']['precursor'][0]['isolationWindow']['isolation window target m/z'])
        with mzml.read(args.input_spectrum) as reader:
            for s in reader:
                if s['ms level'] > 1:
                    ms2plus_scan_idx += 1
                spectra.append(Spectrum(s['id'],s['ms level'],-1 if s['ms level'] == 1 else ms2plus_scan_idx))
    elif input_filetype == 'mgf':
        with mgf.read(args.input_spectrum) as reader:
            for s in reader:
                scan_num = s['params'].get('scans')
                if scan_num:
                    native_id = ','.join('scan={}'.format(s) for s in scan_num.split(','))
                else:
                    native_id = 'NULL'
                ms_level = s['params'].get('mslevel', 2)
                if ms_level > 1:
                    ms2plus_scan_idx += 1
                spectra.append(Spectrum(native_id,ms_level,-1 if ms_level == 1 else ms2plus_scan_idx))

    with open(args.output_index, 'w') as f:
        r = csv.writer(f, delimiter = '\t')
        for spectrum in spectra:
            r.writerow(list(spectrum))

if __name__ == "__main__":
    main()
