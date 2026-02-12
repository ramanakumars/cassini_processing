"""
This script generates fullglobe mosaics for each rotation in the cassini images
"""

import numpy as np
from kalasiris import automos
from osgeo import gdal_array

for rot in range(22):
    imgs = []
    for filt in ['CB2', 'GRN', 'BL1']:
        print(rot, filt)
        outfile = f"mosaics/{filt}_automos_rotation{rot}.cub"
        automos(
            fromlist=f"filelists/filelist_rotation{rot}_{filt}.txt",
            mosaic=outfile,
            priority="average",
            grange="user",
            minlat=-90,
            maxlat=90,
            minlon=-180,
            maxlon=180,
        )
        imgs.append(gdal_array.LoadFile(outfile)[0])

    np.save(f"npys/rotation{rot}.npy", np.dstack(imgs))
