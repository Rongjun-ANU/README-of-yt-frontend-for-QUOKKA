import yt 
import numpy as np

def main():

    print("\nLoading ./sample/RadiatingParticles/plt026")
    ds = yt.load("./sample/RadiatingParticles/plt026")
    print(ds)
    print()
    print(ds.field_list)

    print("\nLoading ./sample/HydroWave/plt00004")
    ds = yt.load("./sample/HydroWave/plt00004")
    print(ds)

    # Check if face-centered datasets were loaded
    assert hasattr(ds, "ds_fc_x"), "Face-centered x dataset not loaded"
    assert hasattr(ds, "ds_fc_y"), "Face-centered y dataset not loaded"
    assert hasattr(ds, "ds_fc_z"), "Face-centered z dataset not loaded"

    print(ds.ds_fc_x)
    
    # Check that the face-centered datasets have the correct attributes
    assert ds.ds_fc_x.fc_direction == "x"
    assert ds.ds_fc_y.fc_direction == "y"
    assert ds.ds_fc_z.fc_direction == "z"
    
    # Check that the face-centered datasets have a reference to the parent dataset
    assert ds.ds_fc_x.parent_ds is ds
    assert ds.ds_fc_y.parent_ds is ds
    assert ds.ds_fc_z.parent_ds is ds
    
    assert isinstance(ds, yt.frontends.amrex.data_structures.QuokkaDataset)
    assert isinstance(ds.ds_fc_x, yt.frontends.amrex.data_structures.QuokkaDataset)

    # Print some basic information
    print(f"Main dataset fields: {ds.field_list}")
    print(f"Face-centered x dataset fields: {ds.ds_fc_x.field_list}")
    # print(f"Face-centered y dataset fields: {ds.ds_fc_y.field_list}")
    # print(f"Face-centered z dataset fields: {ds.ds_fc_z.field_list}")

    ad = ds.ds_fc_x.all_data()
    field =  ('boxlib', 'x-RiemannSolverVelocity')
    x_flux_array = np.array(ad[field])
    assert isinstance(x_flux_array, np.ndarray)

    return


if __name__ == "__main__":

    main()
