# cassini_processing
Processing Cassini images using USGS ISIS3 software

## Dependencies

You will need to set up USGS/ISIS3 software and make sure you are able to access the individual ISIS3 functions (e.g., spiceinit, qview, etc.)

### Getting the Cassini kernels

You will need to download the base and Cassini SPICE kernels for these scripts. Instructions are given ![here](https://astrogeology.usgs.gov/docs/how-to-guides/environment-setup-and-maintenance/isis-data-area/#the-base-data-area).

### Python dependencies

The following packages are required for these scripts:

```bash
numpy
tqdm
pysis
```

You can install this using `uv` or `pip`:

```bash
uv sync
```

## Running the code

### Folder structure
The folder structure for the code and data is as follows:
```
cassini_processing
    | -- ** main scripts **
    | -- jupiter_imgs/  # where the PDS LBL/IMG files are stored
            | -- ** each folder contains .LBL and .IMG files from a specific time range **
    | -- cubs/  # where the ISIS3 format (uncalibrated) .cub files are stored
            | -- RED/  # red filter data
            | -- GRN/  # green filter data
            | -- ...
    | -- calibrated_cubs/   # where the calibrated cubs + backplane data are stored
            | -- RED/  # red filter data
            | -- GRN/  # green filter data
            | -- ...
    | -- maps/  # where the equirectangular maps are stored
            | -- RED/  # red filter data
            | -- GRN/  # green filter data
            | -- ...
```

### Running the processing scripts
The scripts can be run with `uv` or `python`. 

1. Convert the data to ISIS3 format:

Run `get_jupiter_cubes.py` which will fetch the data (folder for PDS LBLs/IMGs is hardcoded so change as needed):

```bash
uv run get_jupiter_cubes.py
```

This will create and populate the `jupiter_imgs/` and `cubs/` folder with images taken between 2000-10-30 and 2000-09-15.

2. Calibrate the ISIS3 cubes:

```bash
uv run calibrated_jupiter_cubes.py
```

This will create the `calibrated_cubs/` folder and populate it with the calibrated cubes and the associated backplane files (`xxxx_backplane.cub`)

3. Map-project the calibrated cubes:

```bash
uv run generate_maps.py
```

This will create the `maps/` folder and populate it with the equirectangular maps (and projected backplane data)
