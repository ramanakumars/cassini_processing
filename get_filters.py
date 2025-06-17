"""
This is a utility script to get a list of filters in the cubs/ directory
"""
import glob
import signal
from multiprocessing import Pool

import tqdm
from pysis.isis import getkey


def initializer():
    """Ignore CTRL+C in the worker process."""
    signal.signal(signal.SIGINT, signal.SIG_IGN)


def calibrate(cube):
    return getkey(from_=cube, grpname='BandBin', keyword='FilterName')


jupiter_cubes = sorted(glob.glob('cubs/*.cub'))

filters = []

with Pool(processes=16, initializer=initializer) as pool:
    try:
        with tqdm.tqdm(total=len(jupiter_cubes), desc='Getting filters') as pbar:
            for result in pool.imap_unordered(calibrate, jupiter_cubes):
                filters.append(result)
                pbar.update()
        pool.close()
    except KeyboardInterrupt:
        pool.terminate()
    finally:
        pool.join()

print(set(filters))
