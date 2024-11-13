
ORIGINAL_DATA_FOLDER = "original_data"

SPLIT_DATA_FOLDER = "amr_ldc/data/amrs/split"

SEARCH_RESULTS_FOLDER = "search_results"

MAPPINGS_FOLDER = "mappings"

VERBALIZATION_FILE = 'verbalization.txt'

NE_MAPPINGS = "ne_mappings.csv"

BAD_NOUN_PREDICATION_MOD_VALS = "noun_predication_bad_mod_values.csv"

SPATIAL_ROLESETS = "spatial_rolesets.csv"

RETROFITTED_FOLDER = "retrofitted_data/UMR_retrofit/"

LDC_FOLDER = "LDC"

def amrSplitDataFolder():
    return ORIGINAL_DATA_FOLDER + "/" + SPLIT_DATA_FOLDER


def ambiguousAMRTypes():
    return ["book", "company", "event", "facility", "family", "festival", "journal", "location", "magazine", \
            "organization", "newspaper", "natural-object", "molecular-physical-entity", "product", "publication", "show", "thing"]
    
    
    