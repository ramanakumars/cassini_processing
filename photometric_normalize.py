"""
This script calibrates the Cassini cubs from the cubs/ folder
and places the calibrated cubs in the calibrated_cubs/ folder
"""

import glob
import os
import signal
from multiprocessing import Pool

import tqdm
from kalasiris import photomet, cisscal, phocube


def initializer():
    """Ignore CTRL+C in the worker process."""
    signal.signal(signal.SIGINT, signal.SIG_IGN)


ISISDATA = os.environ.get("ISISDATA")

MINNAERT_K = {'GRN': 0.95, 'BL1': 0.88, 'CB2': 0.99}

def calibrate(cube_data):
    cube = cube_data['filename']
    k = MINNAERT_K[cube_data['filter']]
    try:
        # initialize the spice kernels to get positioning data
        calibrated_cube = cube.replace('cubs', 'calibrated_cubs')
        cisscal(from_=cube, to=calibrated_cube)
        normalized_cube = calibrated_cube.replace('.cub', '_norm.cub')
        photomet(
            from_=calibrated_cube,
            to=normalized_cube,
            phtname='minnaert',
            k=k,
            maxincidence=88,
            maxemission=88,
            normname='albedo',
            incref=0,
            thresh=2,
            albedo=0.6,
        )
        # # also generate the backplanes (emission/incidence angles, etc.)
        phocube(
            from_=cube,
            to=cube.replace('cubs', 'calibrated_cubs').replace(
                '.cub', '_backplane.cub'
            ),
        )
    except Exception as e:
        print(f"Skipping {cube}")
        print(e)
        if os.path.exists(calibrated_cube):
            os.remove(calibrated_cube)
        return


jupiter_cubes = []
for cube in sorted(glob.glob('cubs/*/*.cub')):
    filter_name = os.path.dirname(cube).split('/')[-1]
    if filter_name in ['CB2', 'GRN', 'BL1']:
        outfile = cube.replace('cubs', 'calibrated_cubs')
        if not os.path.exists(os.path.dirname(outfile)):
            os.makedirs(os.path.dirname(outfile))
        jupiter_cubes.append({ "filename": cube, "filter": filter_name })

print(f"Found {len(jupiter_cubes)} cubes")

with Pool(processes=10, initializer=initializer) as pool:
    try:
        with tqdm.tqdm(total=len(jupiter_cubes), desc='Normalizing data') as pbar:
            for _ in pool.imap_unordered(calibrate, jupiter_cubes):
                pbar.update()
    except KeyboardInterrupt:
        pool.terminate()
    finally:
        pool.join()
