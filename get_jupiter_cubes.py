"""
This script will copy over relevant image files and convert them from PDS format to Cassini ISIS3 format
"""

import datetime
import glob
import os
import re
import shutil

import tqdm
from dateutil import parser
from pysis.isis import ciss2isis

# get the list of PDS labels that we need to process
labels = sorted(glob.glob('../cassini/data/raw_data/*/*.LBL'))

# get the existing LBLs in the processing folder (useful when restarting code)
jupiter_lbls = sorted(glob.glob('jupiter_imgs/*.LBL'))

# search patterns to find the target name and filter
target_pattern = r'TARGET_NAME = "(\S+)"'
filter_pattern = r"FILTER_NAME = \(\"(?:(?:CL\d)|(\w+))\",\"(?:(?:CL\d)|(\w+))\"\)"
image_time_pattern = r"IMAGE_TIME = \"?([^Z\"\n]+)"

# time mask to process data only between these time stamps
start = parser.parse("2000-10-30")
end = parser.parse("2000-11-17")

for label in tqdm.tqdm(labels):
    filename = os.path.basename(label)

    with open(label, 'r') as infile:
        label_data = infile.read()

    matches = re.findall(target_pattern, label_data)
    filter_matches = list(re.findall(filter_pattern, label_data)[0])
    filter_matches = list(filter(lambda e: e != '', filter_matches))
    time_matches = re.findall(image_time_pattern, label_data)

    if len(matches) > 0:
        if matches[0].lower() == 'jupiter':
            # make sure we're getting a filter (we want to ignore open filters)
            if len(filter_matches) > 1 or len(filter_matches) == 0:
                print(f"No filters found for {label}")
                print(filter_matches)
                continue

            filter_name = filter_matches[0]

            if len(time_matches) > 1 or len(time_matches) == 0:
                print(f"No time found for {label}")
                print(time_matches)
                continue

            image_time = time_matches[0]
            start_time = datetime.datetime.strptime(
                image_time.strip()[:-4],
                "%Y-%jT%H:%M:%S",
            )

            # process only between the given times
            if start_time > start and start_time < end:
                # create the folder and move images over to the processing folder
                if not os.path.exists(f'jupiter_imgs/{filter_name}'):
                    os.makedirs(f'jupiter_imgs/{filter_name}')

                shutil.copyfile(label, f'jupiter_imgs/{filter_name}/{filename}')
                shutil.copyfile(
                    label.replace('.LBL', '.IMG'),
                    f'jupiter_imgs/{filter_name}/{filename.replace(".LBL", ".IMG")}',
                )

                jupiter_lbls.append(f'jupiter_imgs/{filter_name}/{filename}')


# now loop over all files in the processing directory and convert them to ISIS3 format
for label in tqdm.tqdm(jupiter_lbls):
    # the ISIS3 files will be stored in the cubs/ folder
    outfile = label.replace('jupiter_imgs', 'cubs').replace('.LBL', '')
    if not os.path.exists(os.path.dirname(outfile)):
        os.makedirs(os.path.dirname(outfile))

    if os.path.exists(outfile + '.cub'):
        continue

    ciss2isis(from_=label, to=outfile)
