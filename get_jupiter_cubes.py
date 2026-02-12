"""
This script will copy over relevant image files and convert them from PDS format to Cassini ISIS3 format
"""

import glob
import os
import shutil

import pvl
import pytz
import tqdm
from dateutil import parser
from kalasiris import ciss2isis

# get the list of PDS labels that we need to process
# labels = sorted(glob.glob('../cassini/data/raw_data/*/*.LBL'))
labels = sorted(glob.glob('../cassini/coiss_1002/data/*/*.LBL'))

# get the existing LBLs in the processing folder (useful when restarting code)
jupiter_lbls = sorted(glob.glob('jupiter_imgs/*.LBL'))

# search patterns to find the target name and filter

# time mask to process data only between these time stamps
start = pytz.utc.localize(parser.parse("2000-10-30T00:00:00"))
end = pytz.utc.localize(parser.parse("2000-11-17T00:00:00"))


filters_all = []

for label_file in tqdm.tqdm(labels, dynamic_ncols=True):
    filename = os.path.basename(label_file)

    labels = pvl.load(label_file)

    if (
        labels['TARGET_NAME'].lower() == 'jupiter'
        and 'NARROW ANGLE' in labels['INSTRUMENT_NAME']
    ):
        filters = labels['FILTER_NAME']
        filters_all.append(tuple(filters))
        # make sure we're getting a filter (we want to ignore open filters)

        if filters[0] == "BL1" and filters[1] == "CL2":
            filter_name = "BL1"
        elif filters[0] == "CL1" and filters[1] == "GRN":
            filter_name = "GRN"
        elif filters[0] == "CL1" and filters[1] == "CB2":
            filter_name = "CB2"
        else:
            # print(filters, labels['INSTRUMENT_NAME'])
            continue

        start_time = labels['IMAGE_TIME']

        # process only between the given times
        if start_time > start and start_time < end:
            # create the folder and move images over to the processing folder
            if not os.path.exists(f'jupiter_imgs/{filter_name}'):
                os.makedirs(f'jupiter_imgs/{filter_name}')

            shutil.copyfile(label_file, f'jupiter_imgs/{filter_name}/{filename}')
            shutil.copyfile(
                label_file.replace('.LBL', '.IMG'),
                f'jupiter_imgs/{filter_name}/{filename.replace(".LBL", ".IMG")}',
            )

            jupiter_lbls.append(f'jupiter_imgs/{filter_name}/{filename}')

print(set(filters_all))

# now loop over all files in the processing directory and convert them to ISIS3 format
for label in tqdm.tqdm(jupiter_lbls):
    # the ISIS3 files will be stored in the cubs/ folder
    outfile = label.replace('jupiter_imgs', 'cubs').replace('.LBL', '')
    if not os.path.exists(os.path.dirname(outfile)):
        os.makedirs(os.path.dirname(outfile))

    if os.path.exists(outfile + '.cub'):
        continue

    ciss2isis(from_=label, to=outfile)
