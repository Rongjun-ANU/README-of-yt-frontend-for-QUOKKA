# The YT Frontend for the `QUOKKA` Dataset

## 1. Overview

Chongchong and I developed a new YT frontend developed for the `QUOKKA` dataset. It provides seamless integration with YT's data structures and visualization capabilities.

## 2. Features

- **Header Management**:
    - **Dynamic Field Detection**: Automatically detects and loads:
        - 6 compulsory Gas fields (density, energy, internal energy, x/y/z-momentum)
        - Optional Temperature field
        - Optional Scalar fields
        - Optional Radiation fields
        - Optional Magnetic fields (placeholder) 
    - **Units Management**:
        - Maps field names to (field_type, field_name) tuples (e.g., `('boxlib', 'gasDensity')` to `('gas', 'density')`)
        - Assigns physical units to dimensionless native fields
    
- **Metadata Management**:
    - Reads `metadata.yaml` for simulation parameters
    - Parses header files for field information
    - Handles multi-dimensional data structures

- **Particle Support**:
    - Dynamic detection of particle types
    - Automatic parsing of particle fields from `*_particles` directories
    - Support for custom particle field units via `Fields.json`

## 3. Changes

1. Modify `QuokkaDataset` in `/yt/frontends/amrex/data_structures.py`: Main dataset class extending `AMReXDataset`
     - Verify `QUOKKA` dataset
     - Handles file parsing
     - Supports additional fluid types
2. Add `QuokkaHierarchy` in `/yt/frontends/amrex/data_structures.py`: Data hierarchy class handling:
     - Header and metadata reading
     - Particles information reading
3. Add `QuokkaFieldInfo` in `/yt/frontends/amrex/fields.py`: Field management class providing:
     - Gas fields
     - Derived fields (velocities, radiation, magnetic fields) 
     - Particle fields (Rad/CIC/Sink/... particles)
4. Import `QuokkaDataset`, `QuokkaHierarchy` and `QuokkaFieldInfo` in `/yt/frontends/amrex/api.py`


## 4. Requirements

Please check out our [modified `yt`](https://github.com/chongchonghe/yt) at https://github.com/chongchonghe/yt. 

## 5. Explaination

### 5.1 Classical `QUOKKA` dataset

A standard `QUOKKA` dataset consists of the following essential components:

```bash
dataset_folder/
├── Level_0/         # `QUOKKA` data
├── Header           # Dataset header information
└── metadata.yaml    # Configuration file for YT integration
```

Here, `metadata.yaml` is the key for `yt` to verify the `QUOKKA` dataset. It contains some parameters and it may contain:

```yaml
a_rad: 1
c_hat: 1
c: 1
G: 1
unit_length: .nan
unit_time: .nan
k_B: 1
unit_temperature: .nan
unit_mass: .nan
```

For datasets with particles, additional directories `XXX_particles` (`XXX` here can be `Rad` for radiation particles, `Sink` for sink particles, ...) are included:

```bash
dataset_folder/
├── Level_0/
├── Header
├── metadata.yaml
├── XXX_particles/     # Particle fields
│   ├── Fields.json    # Particle field names and units
│   ├── Header
│   └── Level_0/
```

Here, `Fields.json` contains field names and units for each type of particle. The unit of each field here is expressed by 4 fundamental units: M  (mass),  L (length), T (time) and  Θ (temperature). For example, for velocity, the corresponding unit is `L^1 T^-1` and it will be expressed as `[0, 1, -1, 0]`; while for thermal conductivity, the corresponding unit is `M^1 L^1 T^-3 Θ^-1` and it will be expressed as `[1, 1, -3, -1]`. In this case, such `Fields.json` may contain: 

```json
{
    "fields": {
        "velocity": "",
        "thermal_conductivity": ""
    }, 
    "units": {
        "velocity": [0, 1, -1, 0], 
        "thermal_conductivity": [1, 1, -3, -1]
    }
}
```

### 5.2 Load `QUOKKA` dataset 

For example, if we load a calssical `QUOKKA` dataset 

```python
ds = yt.load("plt007")
```

and we can use the following code to verify if the loaded data is a `QUOKKA` dataset:

```python
ds.parameters['HydroMethod']
```

Normally, it should return

```python
'Quokka'
```

Otherwise, if it returns `'boxlib'` then that means `yt` fails to recognize your data as a `QUOKKA` dataset and only treat it as a regular `boxlib` dataset. In this case, you should go back the your path and make sure that `metadata.yaml` is contained in the dataset. For more details, see Section 7. 

### 5.3 Parsing fields

Each `QUOKKA` dataset will contains 6 compulsory `gas` fields: density, energy, internal density and momentum in x/y/z components. 

Besides these 6 fundamental `gas` fields, `yt`will continue to check the existence of other optional fields, including temperature, some passive scalars,  and velocities in x/y/z components for `gas` fields; energy and fluxes in x/y/z components in some particular bands of `rad` (radiation) fields; and `mag` (magnetic) fields as a placeholder for future updates of `QUOKKA` code. 

We may use `ds.field_list` to check the native fields of the dataset; while `ds.derived_field_list` can be used to check these derived fields. For example, those 6 mandantory fields are stored as the following native fields in the dataset:

```python
[('boxlib', 'gasDensity'),
 ('boxlib', 'gasEnergy'),
 ('boxlib', 'gasInternalEnergy'),
 ('boxlib', 'x-GasMomentum'),
 ('boxlib', 'y-GasMomentum'),
 ('boxlib', 'z-GasMomentum')]
```

Meanwhile, you can also find them in derived fields:
```python
[('gas', 'density'),
 ('gas', 'energy'),
 ('gas', 'internalEnergy'),
 ('gas', 'x-momentum'),
 ('gas', 'y-momentum'),
 ('gas', 'z-momentum')]
```

Similarly, if `rad` fields are detected in the dataset, then in `ds.field_list` we may also see: 

```python
[('boxlib', 'radEnergy-Group0'),
 ('boxlib', 'x-RadFlux-Group0'),
 ('boxlib', 'y-RadFlux-Group0'),
 ('boxlib', 'z-RadFlux-Group0')]
```

Also, we can find them in `ds.derived_field_list`: 

```python
[('rad', 'energy_density_0'),
 ('rad', 'flux_density_x_0'),
 ('rad', 'flux_density_y_0'),
 ('rad', 'flux_density_z_0')]
```

Since all the native `boxlib` fields do not contain physical units in the dataset, we also add corresponding units to these derived list. For example, for gas density, if we use `ds.r[('boxlib', 'gasDensity')]`, we may see 

```python
unyt_array([1., 1., 1., ..., 1., 1., 1.], 'code_mass/code_length**3')
```

However, if we do `ds.r[('gas', 'density')]`, we will have

```python
unyt_array([1., 1., 1., ..., 1., 1., 1.], 'g/cm**3')
```

The reason why we convert all the native `boxlib` fields to corresponding derived fields and add physical units to them is that many `Python` packages based on `yt` require tuples in the form of `('type', 'field_name')` and correct physical units, i.e., `boxlib` and `code_unit` are not allowed. 

### 5.4 Parsing information in `Header` and `metadata.yaml`

Moreover, for all the information from `Header` and `metadata.yaml` files, you may check out by 

```python
ds.parameters
```

### 5.5 Some Visualisations

Now we can try to do some visualisations with `yt`.  For example, we can use the following code to see the slice plot of gas density at the x-y plane:

```python
yt.SlicePlot(ds, 'z', ('gas', 'density'))
```

And we get

![image-20250114194056391](/Users/maclaptop29/Library/Application Support/typora-user-images/image-20250114194056391.png)

Or if `rad` fields are included, we can try 

```python
yt.SlicePlot(ds, 'z', ('rad', 'energy_density_0'))
```

![image-20250114194036515](/Users/maclaptop29/Library/Application Support/typora-user-images/image-20250114194036515.png)

Or if radiating particles are included, we may try

```python
yt.SlicePlot(ds, "z", ('rad', 'energy_density_0'), center='c').set_cmap(('rad', 'energy_density_0'), 'hot').annotate_particles(1, p_size=400., col='blue', marker='*', ptype='Rad_particles')
```

![image-20250114195202535](/Users/maclaptop29/Library/Application Support/typora-user-images/image-20250114195202535.png)

## 6. Usage

Good luck.

```python
import yt

# Load a `QUOKKA` dataset
ds = yt.load("path_to_quokka_output")

# Access fields
ad = ds.all_data()
ad['gas', 'density'] # print gas density field

# Create a slice plot of density field
yt.SlicePlot(ds, 'z', ('gas', 'density'))
```

Debug: 

```python
import yt
yt.set_log_level("DEBUG")
```

## 7. Experience

If for some reason your `QUOKKA` dataset is missing `metadata.yaml` and thus fails to be recognised as a `QUOKKA` dataset by `yt`, you may manually add a `metadata.yaml` in your dataset. Or, you may try:

```python
# The way to read the non-yaml data
from yt.frontends.amrex.data_structures import QuokkaDataset

class OldQuokkaDataset(QuokkaDataset):
    def _parse_metadata_file(self):
        # Override to do nothing
        pass

# Load the dataset
ds = OldQuokkaDataset("path_to_your_old_quokka_data")
```

