import numpy as np
import yt
from yt.frontends.amrex.data_structures import QuokkaDataset

DATAROOT = "./sample"


def test_radiating_particles():
    ds = yt.load(f"{DATAROOT}/RadiatingParticles/plt026")
    assert isinstance(ds, QuokkaDataset), f"expected QuokkaDataset, got {type(ds)}"
    assert ("boxlib", "radEnergy-Group0") in ds.field_list
    assert ("rad", "energy_density_0") in ds.derived_field_list

    particle_info = ds.parameters["particle_info"]
    for ptype, info in particle_info.items():
        n_header = info["num_particles"]
        ad = ds.all_data()
        n_actual = int(ad[ptype, "particle_position_x"].size)
        assert n_header == n_actual, (
            f"{ptype}: header says {n_header} particles but data has {n_actual}"
        )


def test_hydro_wave_face_centered():
    ds = yt.load(f"{DATAROOT}/HydroWave/plt00001")
    assert isinstance(ds, QuokkaDataset), f"expected QuokkaDataset, got {type(ds)}"

    for direction in ("x", "y", "z"):
        fc_ds = getattr(ds, f"ds_fc_{direction}", None)
        assert fc_ds is not None, f"face-centered {direction} dataset not loaded"
        assert isinstance(fc_ds, QuokkaDataset), (
            f"ds_fc_{direction} is not a QuokkaDataset, got {type(fc_ds)}"
        )
        assert fc_ds.fc_direction == direction
        assert fc_ds.parent_ds is ds

    ad = ds.ds_fc_x.all_data()
    field = ("boxlib", "x-RiemannSolverVelocity")
    assert field in ds.ds_fc_x.field_list, f"{field} not in ds_fc_x.field_list"
    arr = np.array(ad[field])
    assert isinstance(arr, np.ndarray)
    assert arr.size > 0


def test_alfven_wave_bfield():
    ds = yt.load(f"{DATAROOT}/AlfvenWaveLinear/plt0000604")
    assert isinstance(ds, QuokkaDataset), f"expected QuokkaDataset, got {type(ds)}"

    for axis in ("x", "y", "z"):
        assert ("boxlib", f"{axis}-BField") in ds.field_list, (
            f"(boxlib, {axis}-BField) not in field_list"
        )
        assert ("gas", f"magnetic_field_{axis}") in ds.derived_field_list, (
            f"(gas, magnetic_field_{axis}) not in derived_field_list"
        )

    ad = ds.all_data()
    bx = np.array(ad["gas", "magnetic_field_x"])
    assert bx.size > 0


if __name__ == "__main__":
    test_radiating_particles()
    print("test_radiating_particles passed")

    test_hydro_wave_face_centered()
    print("test_hydro_wave_face_centered passed")

    test_alfven_wave_bfield()
    print("test_alfven_wave_bfield passed")

    print("\nAll tests passed.")
