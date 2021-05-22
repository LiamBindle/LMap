import xarray as xr
import splint.linear_transform


# transform = ezRemap.esmf.load_weights(
#     'my_esmf_regrid_weights.nc',
#     input_transform_dims=[('lat', 'lon'), (181, 360)],
#     output_transform_dims=[('nf', 'Ydim', 'Xdim'), (6, 24, 24)],
# )

def load_weights(filename, input_dims, output_dims):
    ds_weights = xr.open_dataset(filename)

    # Get sparse matrix elements
    weights = ds_weights.S
    row_ind = ds_weights.row
    col_ind = ds_weights.col

    # Create a linear transform object
    transform = splint.linear_transform.SparseLinearTransform(
        weights, row_ind, col_ind,
        input_transform_dims=input_dims,
        output_transform_dims=output_dims,
        one_based_indices=True,
        order="C",
    )

    return transform