from enum import Enum

class Checkpoint(Enum):
    GENERATE_FILE_LIST = "1_generate_file_list"
    GENERATE_SHARED_LIBRARIES = "2_generate_shared_libraries"
    GENERATE_CODE = "3_generate_code"
