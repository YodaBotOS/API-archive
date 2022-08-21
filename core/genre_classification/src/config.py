# ⚠️ WARNING ⚠️
# DO NOT CHANGE THIS FILE UNLESS YOU KNOW WHAT YOU ARE DOING.
# CHANGING THIS FILE WILL CAUSE THE CURRENT CODE TO NOT WORK PROPERLY AS EXPECTED.
# IF YOU ARE LOOKING FOR THE CONFIG FILE, IT IS AT THE ROOT FOLDER OF THE REPOSITORY.

import os

# DEFINE PATHS
DATAPATH = 'core/genre_classification/data/'
RAW_DATAPATH = 'core/genre_classification/utils/raw_data.pkl'
SET_DATAPATH = 'core/genre_classification/utils/set.pkl'
MODELPATH = 'core/genre_classification/model/net.pt'

try:
    GENRES = os.listdir(DATAPATH)
except:
    GENRES = None

GENRES = GENRES or ['blues', 'classical', 'country',
                    'disco', 'hiphop', 'jazz', 'metal',
                    'pop', 'reggae', 'rock']
