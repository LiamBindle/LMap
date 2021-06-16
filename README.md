# sparselt

sparselt is a small library for regridding Earth system model data. 
More generally, sparselt makes it easy to apply vectorized sparse linear transforms to high-dimensionality datasets.

Operations like regridding can be written as a linear transform. 
The matrix has shape (M,N) where N is the flat-size of the output grid and M is the flat-size of the input grid. 
Tools like `ESMF_RegridWeightGen` can generate these "regridding weights" for a variety of methods 
(e.g., bilinear, conservative, etc.)
for a variety of grid types (e.g., lat-lon, gaussian, cubed-sphere, stretched cubed-sphere, etc.).
sparselt is a small formalization for applying sparse transforms like this. 

sparselt is intended to be used in combination with 
* [gridspec](https://github.com/LiamBindle/gridspec) for generating grid definition files
* [ESMF](https://earthsystemmodeling.org/) and specifically the `ESMF_RegridWeightGen` tool
* [xarray](http://xarray.pydata.org/en/stable/) for working with NetCDF datasets

The workflow for using sparselt for regridding is

1. Create grid definitions files for the input and output grids using a tool like [gridspec](https://github.com/LiamBindle/gridspec)
2. Generate regridding weights using a tool like `ESMF_RegridWeightGen`
3. Apply the weights to your dataset with sparselt

What about [xESMF](https://xesmf.readthedocs.io/en/latest/)? xESMF is a terrific for regridding logically rectangular 
grids, however, it has limited support for higher-order grids like cubed-sphere grids 
(see [here](https://xesmf.readthedocs.io/en/latest/limitations.html)).


## Installation

For the meantime, you can install sparselt like so
```console
$ pip install git+https://github.com/LiamBindle/sparselt.git 
```

## Examples

See the `examples/` subdirectory for an example, and `examples/sample_data/README.md` for a description of how the sample data files were generated.

## Applying ESMF regrid weights

The following is an example of regridding a C48 dataset to a lat-lon grid using weights 
generated by `ESMF_RegridWeightGen`.

```python
import xarray as xr
import sparselt.esmf
import sparselt.xr

# Load dataset on C48 grid
ds = xr.open_dataset('my_c48_dataset.nc')

# Create a linear transformer object from an ESMF weights file
transform = sparselt.esmf.load_weights(
    'regrid_weights.nc',                               # Generated by ESMF_RegridWeightGen
    input_dims=[('nf', 'Ydim', 'Xdim'), (6, 48, 48)],  # applied along input dimensions
    output_dims=[('lat', 'lon'), (90, 180)],           # result dimensions
)

# Apply the transform to ds
ds = sparselt.xr.apply(transform, ds)

```

Initially, the dataset looks like this:
```
<xarray.Dataset>
Dimensions:          (Xdim: 48, Ydim: 48, lev: 24, nf: 6, time: 1)
Coordinates:
  * Xdim             (Xdim) float64 305.8 307.4 309.0 ... 31.01 32.63 34.21
  * Ydim             (Ydim) float64 -44.21 -42.62 -41.01 ... 41.01 42.62 44.21
  * lev              (lev) float64 1.0 2.0 3.0 4.0 5.0 ... 21.0 22.0 23.0 24.0
  * nf               (nf) int32 1 2 3 4 5 6
  * time             (time) datetime64[ns] 2019-09-16
Data variables:
    SpeciesConc_CO   (time, lev, nf, Ydim, Xdim) float32 ...
    SpeciesConc_NO2  (time, lev, nf, Ydim, Xdim) float32 ...
    SpeciesConc_O3   (time, lev, nf, Ydim, Xdim) float32 ...
```

After regridding, the dataset looks like this:
```
<xarray.Dataset>
Dimensions:          (lat: 90, lev: 24, lon: 180, time: 1)
Coordinates:
  * lev              (lev) float64 1.0 2.0 3.0 4.0 5.0 ... 21.0 22.0 23.0 24.0
  * time             (time) datetime64[ns] 2019-09-16
Dimensions without coordinates: lat, lon
Data variables:
    SpeciesConc_CO   (time, lev, lat, lon) float64 6.006e-08 ... 1.06e-07
    SpeciesConc_NO2  (time, lev, lat, lon) float64 4.517e-15 ... 2.317e-12
    SpeciesConc_O3   (time, lev, lat, lon) float64 2.247e-08 ... 4.854e-08
```

## General sparse linear transforms

Below is an example of apply a general sparse linear transform 
(e.g., could be extended for using weights generated by an alternative tool, 
3D regridding, vector regridding, 4D spacetime sampling, etc.).

```python
import xarray as xr
import sparselt
import sparselt.xr

# Open input dataset
ds = xr.open_dataset('my_input_data.nc')

# Load weights from file
ds_weights = xr.open_dataset('my_weights.nc')

# Get sparse matrix elements
weights = ds_weights.S
row_ind = ds_weights.row
col_ind = ds_weights.col

# Create a linear transformation object
transform = sparselt.SparseLinearTransform(
    weights, row_ind, col_ind,
    input_transform_dims=[('lat', 'lon'), (361, 576)], 
    output_transform_dims=[('nf', 'Ydim', 'Xdim'), (6, 180, 180)],
    one_based_indices=True,
    order="C",
)

# Apply the transformation
ds = sparselt.xr.apply(transform, ds[['tas', 'pr']])
``` 
