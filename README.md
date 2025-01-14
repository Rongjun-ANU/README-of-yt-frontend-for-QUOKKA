# The YT Frontend for the `QUOKKA` Dataset

## 1. Overview

Chongchong and I have developed a new YT frontend for the `QUOKKA` dataset, enabling seamless integration with YT's data structures and visualization capabilities.

## 2. Features

### **Header Management**
- **Dynamic Field Detection**:
  - Automatically detects and loads:
    - Six essential gas fields (density, energy, internal energy, and x/y/z-momentum)
    - Optional fields, including temperature, scalar, radiation, and magnetic fields (currently a placeholder)
  - **Units Management**:
    - Maps field names to (field_type, field_name) tuples, e.g., `('boxlib', 'gasDensity')` becomes `('gas', 'density')`.
    - Assigns physical units to dimensionless native fields.

### **Metadata Management**
- Reads `metadata.yaml` for simulation parameters.
- Parses header files for field information.
- Handles multi-dimensional data structures.

### **Particle Support**
- Dynamically detects particle types and fields from `*_particles` directories.
- Supports custom particle field units via `Fields.json`.

## 3. Changes

1. **`QuokkaDataset`**:
   - Modify `/yt/frontends/amrex/data_structures.py` to extend the `AMReXDataset` class:
     - Verify `QUOKKA` dataset compatibility.
     - Parse files and support additional fluid types.
2. **`QuokkaHierarchy`**:
   - Add `/yt/frontends/amrex/data_structures.py` for managing:
     - Header and metadata reading.
     - Particle information parsing.
3. **`QuokkaFieldInfo`**:
   - Add `/yt/frontends/amrex/fields.py` to manage:
     - Gas, derived, and particle fields.
4. Import the above modules in `/yt/frontends/amrex/api.py`.

## 4. Requirements

Ensure you use the modified `yt` version available [here](https://github.com/chongchonghe/yt).

## 5. Explanation

### **5.1 Classical `QUOKKA` Dataset**

A standard `QUOKKA` dataset includes the following components:

```bash
dataset_folder/
├── Level_0/         # `QUOKKA` data
├── Header           # Dataset header information
└── metadata.yaml    # Configuration file for YT integration
```

#### Metadata
The `metadata.yaml` file is critical for `yt` to recognize a `QUOKKA` dataset. It contains parameters such as:

```yaml
a_rad: 1
c_hat: 1
c: 1
G: 1
unit_length: .nan
unit_time: .nan
unit_temperature: .nan
unit_mass: .nan
k_B: 1
```

#### Particle Support
Datasets with particles include additional directories:

```bash
dataset_folder/
├── Level_0/
├── Header
├── metadata.yaml
├── XXX_particles/     # Particle fields (e.g., Rad or Sink)
│   ├── Fields.json    # Particle field names and units
│   ├── Header
│   └── Level_0/
```

The `Fields.json` file specifies particle fields and units, expressed using four fundamental units (`M`, `L`, `T`, and `Θ`).

Example `Fields.json`:

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

### **5.2 Loading a `QUOKKA` Dataset**

To load a `QUOKKA` dataset:
```python
ds = yt.load("plt007")
```

To verify:
```python
ds.parameters['HydroMethod']
```
It should return:
```python
'Quokka'
```
If it returns `'boxlib'`, ensure the dataset contains `metadata.yaml`.

### **5.3 Parsing Fields**

`QUOKKA` datasets always include six mandatory gas fields. These fields are represented as:
```python
[('boxlib', 'gasDensity'),
 ('boxlib', 'gasEnergy'),
 ('boxlib', 'gasInternalEnergy'),
 ('boxlib', 'x-GasMomentum'),
 ('boxlib', 'y-GasMomentum'),
 ('boxlib', 'z-GasMomentum')]
```
Derived fields are mapped with physical units:
```python
[('gas', 'density'),
 ('gas', 'energy'),
 ('gas', 'internalEnergy'),
 ('gas', 'x-momentum'),
 ('gas', 'y-momentum'),
 ('gas', 'z-momentum')]
```

For radiation fields:
```python
[('boxlib', 'radEnergy-Group0'),
 ('boxlib', 'x-RadFlux-Group0'),
 ('boxlib', 'y-RadFlux-Group0'),
 ('boxlib', 'z-RadFlux-Group0')]
```
Derived:
```python
[('rad', 'energy_density_0'),
 ('rad', 'flux_density_x_0'),
 ('rad', 'flux_density_y_0'),
 ('rad', 'flux_density_z_0')]
```

### **5.4 Metadata Parsing**
Simulation metadata can be accessed via:
```python
ds.parameters
```

### **5.5 Visualizations**

Visualize gas density on the x-y plane:
```python
yt.SlicePlot(ds, 'z', ('gas', 'density'))
```

For radiation fields:
```python
yt.SlicePlot(ds, 'z', ('rad', 'energy_density_0'))
```

For particles:
```python
yt.SlicePlot(ds, "z", ('rad', 'energy_density_0'), center='c')
.set_cmap(('rad', 'energy_density_0'), 'hot')
.annotate_particles(1, p_size=400., col='blue', marker='*', ptype='Rad_particles')
```

## 6. Usage

Load and visualize a dataset:
```python
import yt

ds = yt.load("path_to_quokka_output")
ad = ds.all_data()
ad['gas', 'density']

yt.SlicePlot(ds, 'z', ('gas', 'density'))
```

For debugging:
```python
import yt
yt.set_log_level("DEBUG")
```

## 7. Experiments

If `metadata.yaml` is missing, you can create it manually or bypass metadata parsing:
```python
from yt.frontends.amrex.data_structures import QuokkaDataset

class OldQuokkaDataset(QuokkaDataset):
    def _parse_metadata_file(self):
        pass

ds = OldQuokkaDataset("path_to_your_old_quokka_data")
```
