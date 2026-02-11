"""
This script calibrates the Cassini cubs from the cubs/ folder
and places the calibrated cubs in the calibrated_cubs/ folder
"""

import glob
import os
import signal
from multiprocessing import Pool

import tqdm
from kalasiris import spiceinit


def initializer():
    """Ignore CTRL+C in the worker process."""
    signal.signal(signal.SIGINT, signal.SIG_IGN)


ISISDATA = os.environ.get("ISISDATA")


def calibrate(cube):
    try:
        # initialize the spice kernels to get positioning data
        spiceinit(
            from_=cube,
            pck=os.path.join(
                os.environ.get('ISISDATA'), 'base/kernels/pck/pck00009.tpc'
            ),
            shape="ellipsoid",
            ik=os.path.join(ISISDATA, 'cassini/kernels/ik/cas_iss_v10.ti'),
            ck=os.path.join(
                ISISDATA,
                'cassini/kernels/ck/00306_00335ca_ISS.bc',
            ),
            spk=os.path.join(
                ISISDATA, 'cassini/kernels/spk/010420R_SCPSE_EP1_JP83.bsp'
            ),
            iak=os.path.join(ISISDATA, 'cassini/kernels/iak/IssNAAddendum005.ti'),
        )
        # calibrated_cube = cube.replace('cubs', 'calibrated_cubs')
        # cisscal(from_=cube, to=calibrated_cube)
    except Exception as e:
        print(f"Skipping {cube}")
        print(e)
        return


jupiter_cubes = []
for cube in sorted(glob.glob('cubs/*/*.cub')):
    filter_name = os.path.dirname(cube).split('/')[-1]
    if filter_name in ['RED', 'GRN', 'BL1']:
        outfile = cube.replace('cubs', 'calibrated_cubs')
        if not os.path.exists(os.path.dirname(outfile)):
            os.makedirs(os.path.dirname(outfile))
        jupiter_cubes.append(cube)

print(f"Found {len(jupiter_cubes)} cubes")

with Pool(processes=10, initializer=initializer) as pool:
    try:
        with tqdm.tqdm(total=len(jupiter_cubes), desc='Calibrating data') as pbar:
            for _ in pool.imap_unordered(calibrate, jupiter_cubes):
                pbar.update()
    except KeyboardInterrupt:
        pool.terminate()
    finally:
        pool.join()
