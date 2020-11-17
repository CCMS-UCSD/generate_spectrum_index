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
    parser.add_argument('-i','--input_spectrum', type = Path, help='Single spectrum file of types mzML, mzXML, or mgf.')
    parser.add_argument('-o','--output_folder', type = Path, help='Folder to write out tab-separated index file to write out')
    parser.add_argument('-l','--default_ms_level', type = str, help='Default MSlevel', default='0')
    parser.add_argument('-e','--error_folder', type = Path, help='Write error file to this folder')
    if len(sys.argv) < 2:
        parser.print_help()
        sys.exit(1)
    return parser.parse_args()

def main():
    args = arguments()

    input_suffixes = [suffix.lower() for suffix in args.input_spectrum.suffixes]
    if '.mzml' in input_suffixes:
        if '.gz' in input_suffixes:
            input_filetype = '.mzml.gz'
        else:
            input_filetype = '.mzml'
    elif '.mgf' in input_suffixes:
        if '.gz' in input_suffixes:
            input_filetype = '.mgf.gz'
        else:
            input_filetype = '.mgf'
    elif '.mzxml' in input_suffixes:
        input_filetype = '.mzxml'
    else:
        input_filetype = ''.join(input_suffixes)

    #Apache FilenameUtils.getBaseName method just takes off the
    #last extension so to match the downstream code,
    #we just remove the final suffix
    
    output = Path(args.output_folder).joinpath(args.input_spectrum.name.with_suffix('.scans'))
    input_filetype = input_filetype.lower()
    if args.error_folder and args.error_folder.is_dir():
        output_err = Path(args.error_folder).joinpath(args.input_spectrum.name)
    else:
        output_err = None
    # List of output spectra
    spectra = []

    # Initialize MS2+ index at 0
    ms2plus_scan_idx = 0

    # In the highly unlikely chance that there are MS1 scans in the MGF set warning flag
    mgf_ms1_warn = False

    if input_filetype == '.mzxml':
        try:
            with open(args.input_spectrum, 'rb') as mzxml_file:
                with mzxml.read(mzxml_file) as reader:
                    for s in reader:
                        # Always use scan= for nativeID for mzXML
                        spectra.append(Spectrum('scan={}'.format(s['num']),int(s['msLevel']),-1 if int(s['msLevel']) <= 1 else ms2plus_scan_idx))
                        # Increment MS2+ counter, if spectrum was MS2+
                        if int(s.get('msLevel',2)) > 1:
                            ms2plus_scan_idx += 1
        except Exception as e:
            if output_err:
                with open(output_err, 'w') as w_err:
                    w_err.write("{}: {}".format(args.input_spectrum.name,repr(e)))
                sys.exit(0)
            else:
                raise Exception(e)
    elif input_filetype == '.mzml':
        try:
            with open(args.input_spectrum, 'rb') as mzml_file:
                mzml_object = mzml.read(mzml_file)
                param_groups = {}
                for ref in mzml_object.iterfind("referenceableParamGroupList/referenceableParamGroup"):
                    param_groups[ref['id']] = ref
            with open(args.input_spectrum, 'rb') as mzml_file:
                with mzml.read(mzml_file) as reader:
                    for s in reader:
                        ms_level = s.get('ms level')
                        if not ms_level:
                            spec_param_group = s.get('ref')
                            if spec_param_group:
                                ms_level = param_groups[spec_param_group].get('ms level')
                            else:
                                ms_level = args.default_ms_level
                        # Always use given nativeID for mzML
                        spectra.append(Spectrum(s['id'],int(ms_level),-1 if int(ms_level) <= 1 else ms2plus_scan_idx))
                        # Increment MS2+ counter, if spectrum was MS2+
                        if int(ms_level) > 1:
                            ms2plus_scan_idx += 1
        except Exception as e:
            if output_err:
                with open(output_err, 'w') as w_err:
                    w_err.write("{}: {}".format(args.input_spectrum.name,repr(e)))
                sys.exit(0)
            else:
                raise Exception(e)
    elif input_filetype == '.mzml.gz':
        try:
            with gzip.open(args.input_spectrum, 'rb') as mzmlgz_file:
                mzml_object = mzml.read(mzmlgz_file)
                param_groups = {}
                for ref in mzml_object.iterfind("referenceableParamGroupList/referenceableParamGroup"):
                    param_groups[ref['id']] = ref
            with gzip.open(args.input_spectrum, 'rb') as mzmlgz_file:
                with mzml.read(mzmlgz_file) as reader:
                    for s in reader:
                        ms_level = s.get('ms level')
                        if not ms_level:
                            spec_param_group = s.get('ref')
                            if spec_param_group:
                                ms_level = param_groups[spec_param_group].get('ms level')
                            else:
                                ms_level = args.default_ms_level
                        # Always use given nativeID for mzML
                        spectra.append(Spectrum(s['id'],int(ms_level),-1 if int(ms_level) <= 1 else ms2plus_scan_idx))
                        # Increment MS2+ counter, if spectrum was MS2+
                        if int(ms_level) > 1:
                            ms2plus_scan_idx += 1
        except Exception as e:
            if output_err:
                with open(output_err, 'w') as w_err:
                    w_err.write("{}: {}".format(args.input_spectrum.name,repr(e)))
                sys.exit(0)
            else:
                raise Exception(e)
    elif input_filetype == '.mgf':
        # try to parse this mgf file with the pyteomics library
        try:
            all_scan_idx = 0
            with open(args.input_spectrum) as mgf_file:
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
        # if that didn't work, just count spectra in the file (marked by lines containing the word "BEGIN")
        except:
            try:
                ms2_count = 0
                with open(args.input_spectrum) as mgf_file:
                    for i,line in enumerate(mgf_file):
                        if "BEGIN" in line:
                            ms2_count += 1
                # assume all spectra are MS level 2 and write out one row for each
                spectra = []
                for index in range(0, ms2_count):
                    spectra.append(Spectrum('index={}'.format(index), 2, index))
            except Exception as e:
                if output_err:
                    with open(output_err, 'w') as w_err:
                        w_err.write("{}: {}".format(args.input_spectrum.name,repr(e)))
                    sys.exit(0)
                else:
                    raise Exception(e)
        # Check if there are extra scans, that aren't MS2+
        if ms2plus_scan_idx < all_scan_idx:
            print("MS1s found in MGF file, proceed with caution!")
    elif input_filetype == '.mgf.gz':
        # try to parse this mgf file with the pyteomics library
        try:
            all_scan_idx = 0
            with gzip.open(args.input_spectrum) as mgf_gz_file:
                with mgf.read(mgf_gz_file) as reader:
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
        # if that didn't work, just count spectra in the file (marked by lines containing the word "BEGIN")
        except:
            try:
                ms2_count = 0
                with gzip.open(args.input_spectrum) as mgf_gz_file:
                    for i,line in enumerate(mgf_gz_file):
                        if "BEGIN" in line:
                            ms2_count += 1
                # assume all spectra are MS level 2 and write out one row for each
                spectra = []
                for index in range(0, ms2_count):
                    spectra.append(Spectrum('index={}'.format(index), 2, index))
            except Exception as e:
                if output_err:
                    with open(output_err, 'w') as w_err:
                        w_err.write("{}: {}".format(args.input_spectrum.name,repr(e)))
                    sys.exit(0)
                else:
                    raise Exception(e)
        # Check if there are extra scans, that aren't MS2+
        if ms2plus_scan_idx < all_scan_idx:
            print("MS1s found in MGF file, proceed with caution!")
    else:
        if output_err:
            with open(output_err, 'w') as w_err:
                w_err.write("{}: Unknown filetype ({}).".format(args.input_spectrum.name,input_filetype))
            sys.exit(0)
        else:
            raise Exception("{}: Unknown filetype ({}).".format(args.input_spectrum.name,input_filetype))

    with open(output, 'w') as f:
        r = csv.writer(f, delimiter = '\t')
        for spectrum in spectra:
            r.writerow(list(spectrum))

if __name__ == "__main__":
    main()
