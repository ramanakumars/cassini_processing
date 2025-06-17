from pysis.isis import spiceinit, cisscal, phocube
import glob
import os
import tqdm
import signal
from multiprocessing import Pool


def initializer():
    """Ignore CTRL+C in the worker process."""
    signal.signal(signal.SIGINT, signal.SIG_IGN)


def calibrate(cube):
    try:
        spiceinit(from_=cube, pck=os.path.join(os.environ.get('ISISDATA'), 'base/kernels/pck/pck00008.tpc'))
        cisscal(from_=cube, to=cube.replace('cubs', 'calibrated_cubs'))
        phocube(from_=cube, to=cube.replace('cubs', 'calibrated_cubs').replace('.cub', '_backplane.cub'))
    except Exception:
        print(f"Skipping {cube}")
        return


jupiter_cubes = []
for cube in sorted(glob.glob('cubs/*/*.cub')):
    filter_name = os.path.dirname(cube).split('/')[-1]
    if filter_name in ['RED']:
        outfile = cube.replace('cubs', 'calibrated_cubs')
        if not os.path.exists(os.path.dirname(outfile)):
            os.makedirs(os.path.dirname(outfile))
        if not os.path.exists(cube.replace('cubs', 'calibrated_cubs').replace('.cub', '_backplane.cub')):
            jupiter_cubes.append(cube)

print(len(jupiter_cubes))

with Pool(processes=10, initializer=initializer) as pool:
    try:
        with tqdm.tqdm(total=len(jupiter_cubes), desc='Calibrating data') as pbar:
            for _ in pool.imap_unordered(calibrate, jupiter_cubes):
                pbar.update()
    except KeyboardInterrupt:
        pool.terminate()
    finally:
        pool.join()
