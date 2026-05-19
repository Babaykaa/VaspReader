# ProChem

ProChem is a Python library and application toolkit for reading, analyzing and
visualizing atomistic simulation results from quantum-chemistry and molecular
simulation packages.

The current codebase is centered on a backend-independent core:

- core models: `Atom`, `Structure`, `Structures`, `StructureDataset`,
  `Calculation`, `Cell`;
- VASP I/O: `vasprun.xml`, restart-sequence merging, `POSCAR`/`CONTCAR`,
  `XDATCAR`, `OUTCAR`, `CHG`/`CHGCAR`, `OSZICAR`, `DOSCAR`, `EIGENVAL`;
- typed VASP result models: `ElectronicSteps`, `IonicSteps`,
  `DensityOfStates`, `ProjectedDensityOfStates`, `BandStructure`;
- MLIP-style structure datasets that are not forced into Structures semantics;
- structure-sequence analysis tables: coordinates, velocities, kinetic energies,
  distances, angles, center of mass, export to CSV/XLSX/HTML;
- backend-independent rendering DTOs: `SceneData`, atoms, inferred bonds, cell,
  axes;
- Jupyter helpers on top of `SceneData`: Plotly figures, animations and a frame
  slider;
- initial Qt, web, Quantum ESPRESSO and LAMMPS adapter scaffolding.

## Requirements

ProChem currently requires:

- Python `>=3.10`;
- `numpy>=1.23.5`;
- `pandas>=2.0.3`.

These lower bounds keep Python 3.10 users supported while allowing pip to pick
newer wheels automatically on Python 3.11, 3.12 and later.

Optional integrations are installed through extras defined in
`pyproject.toml`.

## Installation

Install from a local checkout. Run commands from the repository root.

### Base Library

PowerShell/bash/zsh:

```powershell/bash
python -m pip install -e .
```

This installs the core package, parser registry, VASP/QE/LAMMPS parser modules,
analysis helpers and backend-independent rendering DTOs.

### Development And Tests

PowerShell:

```powershell
python -m pip install -e ".[dev]"
python -m pytest
```

Bash/zsh:

```bash
python -m pip install -e '.[dev]'
python -m pytest
```

The `dev` extra installs `pytest` and `ruff`.

With `uv`, an equivalent one-off test run is:

PowerShell/bash/zsh:

```powershell/bash
uv run --with pytest python -m pytest
```

### Jupyter / Plotly

PowerShell:

```powershell
python -m pip install -e ".[jupyter]"
```

Bash/zsh:

```bash
python -m pip install -e '.[jupyter]'
```

This installs `plotly` and `ipywidgets`. The adapter functions are imported
without these dependencies, but calling Plotly/widget rendering requires this
extra.

Use it as:

```python
from prochem.io import parse
from prochem.rendering import to_scene_data
from prochem.adapters.jupyter import scene_figure, scene_animation

calculation = parse("vasprun.xml")
scene = to_scene_data(
    calculation,
    frame_indices=[0, calculation.step_count - 1],
    atom_colors={"Si": "#d9b36c", "O": "#e74c3c"},
    atom_radius_scales={"H": 0.65, "Si": 1.15},
    bond_max_lengths={"Si-O": 2.1, ("O", "H"): 1.2},
    periodic_image_depth=1,
)

fig = scene_figure(scene, frame_index=0)
fig.show()
```

### Qt GUI

PowerShell:

```powershell
python -m pip install -e ".[qt]"
prochem
```

Bash/zsh:

```bash
python -m pip install -e '.[qt]'
prochem
```

The `qt` extra installs PySide6, PyOpenGL, matplotlib, numba and Pillow. The
`prochem` console script points to `prochem.adapters.qt.app:main`.

The Qt adapter uses the same core models and `SceneData` contract as the
notebook/web layers. `value_to_draw_buffer()` converts atoms to sphere batches
and bonds/cell edges to OpenGL line-segment batches:

```python
from prochem.adapters.qt import QtSceneOptions, parse_calculation, value_to_draw_buffer

calculation = parse_calculation("vasprun.xml")
draw_buffer = value_to_draw_buffer(
    calculation,
    options=QtSceneOptions(
        atom_colors={"Si": "#d9b36c", "O": "#e74c3c"},
        bond_max_lengths={"Si-O": 2.1},
    ),
)
```

### Web Adapter

PowerShell:

```powershell
python -m pip install -e ".[web]"
```

Bash/zsh:

```bash
python -m pip install -e '.[web]'
```

The web adapter exposes a FastAPI app factory and Pydantic schemas for
`SceneData` JSON payloads:

```python
from prochem.adapters.web.api import create_app
from prochem.adapters.web.schemas import SceneDataSchema
from prochem.io import parse
from prochem.rendering import to_scene_data

app = create_app()

calculation = parse("path/to/vasprun.xml")
scene = to_scene_data(calculation)
payload = SceneDataSchema.from_scene_data(scene).model_dump(mode="json")
```

### Full Local Environment

For a workstation with all optional adapters and development tooling:

PowerShell:

```powershell
python -m pip install -e ".[dev,jupyter,qt,web]"
```

Bash/zsh:

```bash
python -m pip install -e '.[dev,jupyter,qt,web]'
```

Keep the extras expression quoted. In bash/zsh this avoids shell glob
expansion; in PowerShell it keeps the extras spec as one argument.

## Core Data Model

`Atom` is the source of element metadata and per-atom state. It can be created
from an element symbol and is prefilled from the periodic table:

```python
from prochem.core import Atom

carbon = Atom(name="C")
same_carbon = Atom(name=6)

print(carbon.charge)          # 6
print(carbon.valent_charge)   # 4
print(carbon.mass)            # 12.011
print(carbon.position)        # [0. 0. 0.]
print(same_carbon.name)       # C
```

`position`, `direct_position`, `velocity` and `force` are 3D NumPy vectors.
`potential_energy`, `kinetic_energy` and `total_energy` are separate optional
fields. Unknown energies are stored as `None` on `Atom` / `Structure` and as
`NaN` in dense arrays. `approximate_force()` / `kinetic_energy_from_velocity()`
cover the common velocity-based estimates.
`size` and `color` are shared by element name, which is useful for
visualization-wide styling:

```python
c1 = Atom(name="C")
c2 = Atom(name="C")

c1.size = 1.2
c1.color = (0.1, 0.1, 0.1, 1.0)

assert c1.size is c2.size
assert c1.color is c2.color
```

`Structure` stores a list of `Atom` objects plus `cell`, `stress`,
`potential_energy`, `kinetic_energy`, `total_energy` and `properties`. Array views such as
`structure.positions`, `structure.species` and `structure.forces` are derived
from atoms so parsers, analysis and renderers all read the same source of truth:

```python
from prochem.core import Atom, Cell, Structure
import numpy as np

structure = Structure(
    atoms=[
        Atom(name="H", index=0, position=(0.0, 0.0, 0.0)),
        Atom(name="H", index=1, position=(0.0, 0.0, 0.74)),
    ],
    cell=Cell(np.eye(3) * 5.0),
)
```

`Structures` is an ordered frame container. Its `timestep` can be one float, a
dictionary `{start_step: timestep}` for merged segments with different time
steps, or `None`. `sources` stores one optional source path per frame.

`Structure`, `Structures` and `StructureDataset` expose dense array helpers:
`positions_array()` / `coordinates_array()`, `velocities_array()`,
`forces_array()`, `atom_potential_energies_array()`,
`atom_kinetic_energies_array()`, `atom_total_energies_array()`,
`structure_potential_energies_array()`, `structure_kinetic_energies_array()` and
`structure_total_energies_array()`. Structure energies are one scalar per
structure frame: for `vasprun.xml` this is the last energy value before the next
ionic step. Per-atom potential/total energies stay `NaN` unless the source
really provides per-atom energies; ProChem does not silently spread the total
structure energy over atoms. Per-atom kinetic energy is computed from velocity
when no explicit atom kinetic energy is stored. For datasets with different
atom counts, per-atom arrays are padded with `NaN`.

## Quick Start

Parse any supported input through the registry:

```python
from prochem.io import parse

calculation = parse(r"B:\Science\Calculations\VASP\example\vasprun.xml")

print(calculation.engine)
print(calculation.step_count)
print(calculation.atom_count)
```

Build a pandas-based analysis table:

```python
from prochem.analysis import AnalysisTable, Selection

structures = calculation.structures
selected = Selection("first3", structures.atom_ids[:3])

analysis = AnalysisTable(structures, selected)
analysis.add_coordinates("first3")
analysis.add_atom_velocities("first3")
analysis.add_atom_kinetic_energies("first3")
df = analysis.dataframe()
```

Read typed VASP result data:

```python
from prochem.io import parse

oszicar = parse("OSZICAR")
doscar = parse("DOSCAR")
eigenval = parse("EIGENVAL")

ionic_df = oszicar.ionic_steps.to_dataframe()
dos_df = doscar.density_of_states.to_dataframe(shifted=True)
bands_df = eigenval.band_structure.to_dataframe()
```

Create backend-independent scene data:

```python
from prochem.rendering import to_scene_data

scene = to_scene_data(calculation, frame_indices=[0])
frame = scene.frame(0)

print(len(frame.atoms), len(frame.bonds), frame.cell is not None)
```

Rendering customization is applied before a backend sees the data:

```python
scene = to_scene_data(
    calculation,
    atom_colors={"C": "#444444", "H": (1.0, 1.0, 1.0, 1.0)},
    atom_radius_scales={"H": 0.7, "O": 1.2},
    bond_max_lengths={"C-H": 1.25, "C-O": 1.55},
    include_periodic_images=True,
    periodic_image_depth=1,
    periodic_image_cutoff=2.0,
)
```

For periodic systems, inferred bonds use minimum-image endpoints. When a
connected component crosses the cell boundary, `SceneData` adds the required
image atoms and image bonds in neighboring cells, so Plotly can draw the local
molecular fragment instead of a line through the whole cell. The default
`periodic_image_depth=1` keeps this bounded to adjacent periodic images, while
`periodic_image_cutoff=2.0` hides image atoms farther than 2 Angstrom from the
cell. Use `periodic_image_cutoff_fraction=0.1` to express the same limit as a
fraction of the shortest lattice-vector length. If both cutoff styles are set,
the stricter distance is used.

## Examples

Runnable scripts live in `examples/`:

```powershell/bash
python examples/parse_vasp_file.py path\to\vasprun.xml
python examples/merge_vasprun_directory.py path\to\restart_directory
python examples/analyze_structures.py path\to\calculation --export table.csv
```

The notebook `notebooks/core_functionality_demo.ipynb` demonstrates the current
core workflow: `Atom`, `Structure`, `Structures`, parsing, restart merging,
tables, MLIP dataset mode, typed VASP results, `SceneData` and Jupyter/Plotly
rendering.

## Tests

The test suite uses small synthetic fixtures and does not require real
production calculations:

```powershell/bash
python -m pytest
```

Covered areas:

- core `Atom`, `Structure`, `Structures`, missing atoms and `StructureDataset`;
- analysis table helpers;
- VASP `POSCAR`, `OSZICAR`, `DOSCAR`, `EIGENVAL` parsing;
- parser registry detection;
- `SceneData` conversion;
- optional Jupyter adapter imports and missing-dependency behavior.

## Project Layout

```text
src/prochem/
  core/        domain models, units, typed result models
  io/          parser registry and package-specific parsers
  analysis/    structure-sequence analysis, table building, export
  rendering/   backend-independent SceneData and primitives
  adapters/    Qt, Jupyter and web integration layers
  storage/     project persistence helpers
```

## Current Development Context

The current architectural direction is:

1. Keep parsers and analysis independent from GUI code.
2. Use typed models for structured result data instead of unstructured
   `Calculation.properties` dictionaries.
3. Keep one core entity per module where practical: `atom.py`, `structure.py`,
   `structures.py`, `calculation.py`, `structure_dataset.py`, `cell.py`.
4. Treat MLIP datasets as `StructureDataset`, not as physical trajectories.
5. Convert core structures to `SceneData` before handing data to Qt, Jupyter or
   web layers.
6. Grow tests from synthetic fixtures first, then add carefully selected real
   regression fixtures only when necessary.

## License

ProChem is distributed under the GNU Lesser General Public License v3.0. See
`LICENCE` for details.

## Citation

If you use this software, cite:

```text
asolovykh (2023). ProChem repository [Computer software].
https://github.com/asolovykh/ProChem
```

BibTeX:

```bibtex
@misc{ProChem,
  author = {asolovykh},
  title = {ProChem repository},
  year = {2023},
  publisher = {github.com},
  journal = {github.com repository},
  howpublished = {\url{https://github.com/asolovykh/ProChem.git}},
  url = {https://github.com/asolovykh/ProChem.git}
}
```
