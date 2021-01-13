-include ../Makefile.credentials
include ../Makefile.deploytemplate

TOOL_FOLDER_NAME=generate_spectrum_index
WORKFLOW_VERSION=0.4.1
WORKFLOW_LABEL="Spectrum Index Generation"
WORKFLOW_DESCRIPTION="This is a script to read spectrum peak files and output the nativeID, MS-level, and MS2+ index (defined as the 0-based index for all spectra of MS-level 2 and higher) for each spectrum.  Supported input types are mzML, mzML.gz, mzXML, and mgf.<br /><br />A note on the nativeID column.  For mzML and mzML.gz the nativeID is read directly, for mzXML it is constructed as a scan=, and for mgf it is constructed as scan= IF there is a SCANS= field in the MGF, otherwise it is constructed as index= and is the 0-based index of all spectra in the file."
