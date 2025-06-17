"""
This script will convert the calibrad cubs to equirectangular maps
"""

import glob
import os
import signal
from multiprocessing import Pool

import tqdm
from pysis.isis import cam2map, spiceinit

mapfile = os.path.join(
    os.environ.get('ISISROOT'), 'appdata/templates/maps/equirectangular.map'
)


def initializer():
    """Ignore CTRL+C in the worker process."""
    signal.signal(signal.SIGINT, signal.SIG_IGN)


def project(cube):
    filename = os.path.basename(cube)
    try:
        filter = os.path.dirname(cube).split('/')[-1]
        spiceinit(
            from_=cube,
            pck=os.path.join(
                os.environ.get('ISISDATA'), 'base/kernels/pck/pck00008.tpc'
            ),
        )
        cam2map(
            from_=cube,
            map='maps/template.map',
            resolution=25,
            pixres='ppd',
            defaultrange='map',
            minlat=-90,
            minlon=-180,
            maxlat=90,
            maxlon=180,
            to=f"maps/{filter}/{filename}",
        )
    except Exception as e:
        print(e.stderr)
        print(e)
        print(f"Skipping {cube}")
        return


jupiter_cubes = []
for cube in tqdm.tqdm(
    sorted(glob.glob('calibrated_cubs/*/*.cub')), desc='Getting list of files'
):
    filter_name = os.path.dirname(cube).split('/')[-1]
    if filter_name in ['RED', 'GRN', 'BL1']:
        outfile = cube.replace('calibrated_cubs', 'maps_dynamics')
        if not os.path.exists(os.path.dirname(outfile)):
            os.makedirs(os.path.dirname(outfile))
        if not os.path.exists(outfile):
            jupiter_cubes.append(cube)

print(f"Found {len(jupiter_cubes)} cubes")

with Pool(processes=10, initializer=initializer) as pool:
    try:
        with tqdm.tqdm(total=len(jupiter_cubes), desc='Projecting data') as pbar:
            for _ in pool.imap_unordered(project, jupiter_cubes):
                pbar.update()
            pool.close()
    except KeyboardInterrupt:
        pool.terminate()
    finally:
        pool.join()
