"""Parse one VASP file or directory and print a compact summary.

Run from the repository root, for example:

    python examples/parse_vasp_file.py B:\\Science\\Calculations\\VASP\\Low-k\\Poss_with_Ar\\POSS_Ar_30_grad_20eV\\vasprun.xml
    python examples/parse_vasp_file.py B:\\Science\\Calculations\\VASP\\ALE\\C12F26\\Ar\\C\\30eV
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from prochem.io import parse  # noqa: E402


DEFAULT_SOURCE = (
    r"B:\Science\Calculations\VASP\Low-k\Poss_with_Ar\POSS_Ar_30_grad_20eV\vasprun.xml"
)


def main() -> None:
    parser = argparse.ArgumentParser(description="Parse a VASP file or directory.")
    parser.add_argument("source", nargs="?", default=DEFAULT_SOURCE)
    args = parser.parse_args()

    calculation = parse(args.source)
    print(f"source: {calculation.source}")
    print(f"engine: {calculation.engine}")
    print(f"error: {calculation.errors.exist}")
    if calculation.errors.exist:
        print(calculation.errors.message)
        return

    print(f"steps: {calculation.step_count}")
    print(f"registry atoms: {calculation.atom_count}")
    print(f"property keys: {sorted(calculation.properties.keys())}")
    if calculation.ionic_steps is not None:
        print(f"ionic steps: {len(calculation.ionic_steps)}")
    if calculation.electronic_steps is not None:
        print(f"electronic steps: {len(calculation.electronic_steps)}")
    if calculation.density_of_states is not None:
        dos = calculation.density_of_states
        print(f"DOS: nedos={dos.nedos} efermi={dos.fermi_energy}")
    if calculation.band_structure is not None:
        bands = calculation.band_structure
        print(f"bands: kpoints={bands.kpoint_count} bands={bands.band_count}")
    if calculation.structures is not None:
        structures = calculation.structures
        print(f"dense positions: {structures.positions_array().shape}")
        print(f"presence mask: {structures.presence_mask().shape}")
        print(f"first frame atoms: {structures.frame(0).atom_count}")
        print(f"last frame atoms: {structures.frame(-1).atom_count}")
        print(f"first species: {', '.join(structures.species[:8])}")


if __name__ == "__main__":
    main()
