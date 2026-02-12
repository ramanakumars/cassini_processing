"""
This script identifies and clusters the images by Jupiter rotations
so that we can mosaic all the images corresponding to one rotation
together for a given filter
"""

import datetime
import glob
import os
from collections import defaultdict

import numpy as np
import pvl
import tqdm

# Jupiter's rotation rate
rotation_rate = datetime.timedelta(hours=9, minutes=55)

if __name__ == "__main__":
    files = sorted(glob.glob('calibrated_cubs/*/*.cub'))

    times = []
    filters = []
    filenames = []

    for file in tqdm.tqdm(files):
        if 'backplane' in file or 'norm' in file:
            continue
        filt = file.split('/')[-2]
        fname = os.path.splitext(os.path.basename(file))[0]
        label = pvl.load(os.path.join("jupiter_imgs", filt, f"{fname}.LBL"))
        time = label['IMAGE_TIME']
        filters.append(filt)
        times.append(time)
        filenames.append(fname)

    start = np.min(times) - datetime.timedelta(seconds=10)
    end = np.max(times)
    time = start
    rot_start_time = time

    rotations = defaultdict(list)
    rotation = 1
    # we will start maching forward in time and identify
    # which images correspond to the closest one to our current
    # "query" time
    while time < end:
        row = {}
        # ignore images before this time since we've already
        # found the images
        time_mask = times > time
        for filt in ['BL1', 'CB2', 'GRN']:
            mask = filters[time_mask] == filt
            times_sub_filt = times[time_mask][mask]
            files_sub_filt = filenames[time_mask][mask]
            if len(times_sub_filt) < 1:
                continue

            # find the index closest to the query time
            ind = np.argmin(times_sub_filt)
            row[filt] = {'time': times_sub_filt[ind], 'filename': files_sub_filt[ind]}
        rotations[f'rot{rotation}'].append(row)

        # march the query time forward to just beyond the current image time
        time = np.max([rowi['time'] for rowi in row.values()]) + datetime.timedelta(
            minutes=30
        )

        # if we already pass one rotation before the previous
        # rotation index, then increment the rotation index
        # and update the start time of the new rotation cycle
        if time - rot_start_time > rotation_rate:
            rot_start_time = time
            rotation += 1

        # break if we have no more images
        # this just catches the end early
        if len(times[times > time]) < 1:
            break

    # save the data out to .txt files which can be used by the mosaicing code

    if not os.path.exists("filelists"):
        os.makedirs("filelists")

    for n, (key, val) in enumerate(rotations.items()):
        files = defaultdict(list)
        for v in val:
            if len(v) > 2:
                for key in ['CB2', 'GRN', 'BL1']:
                    files[key].append(v[key]['filename'])

        for key in ['CB2', 'GRN', 'BL1']:
            with open(f'filelists/filelist_rotation{n:d}_{key}.txt', 'w') as outfile:
                for file in files[key]:
                    outfile.write(f"maps_dynamics/{key}/{file}_norm.cub" + "\n")
