import os

MR_BASE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.." ))
MR_CMAPPER_PATH = os.path.join(MR_BASE_PATH, "cmapper" )
MR_MRCAP_PATH = os.path.join(MR_BASE_PATH, "mrcap" )

os.sys.path += [ MR_BASE_PATH, MR_CMAPPER_PATH, MR_MRCAP_PATH ]
