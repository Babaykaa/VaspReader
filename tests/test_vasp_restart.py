from __future__ import annotations

import pytest
import numpy as np

from prochem.core import StructuresMergePolicy
from prochem.io.vasp import parse_vasprun_sequence


def test_parse_vasprun_sequence_drops_exact_restart_overlap(tmp_path) -> None:
    _write_vasprun(
        tmp_path / "vasprun1.xml",
        ["H", "O"],
        [
            [[0.0, 0.0, 0.0], [0.5, 0.5, 0.5]],
            [[0.1, 0.0, 0.0], [0.6, 0.5, 0.5]],
        ],
    )
    _write_vasprun(
        tmp_path / "vasprun2.xml",
        ["H", "O"],
        [
            [[0.1, 0.0, 0.0], [0.6, 0.5, 0.5]],
            [[0.2, 0.0, 0.0], [0.7, 0.5, 0.5]],
        ],
    )

    calculation, report = parse_vasprun_sequence(
        tmp_path,
        policy=StructuresMergePolicy(boundary_search_frames=2, allow_mismatch_fallback=False),
    )

    assert report.events[1].status == "exact_overlap"
    assert report.events[1].dropped_next_frames == 1
    assert calculation.structures.step_count == 3
    assert calculation.structures.atom_count == 2
    assert calculation.structures.frame(-1).properties["source_step"] == 1
    assert calculation.structures.source(-1).name == "vasprun2.xml"
    assert calculation.structures.structure_potential_energies_array().shape == (3,)
    np.testing.assert_allclose(
        calculation.structures.structure_total_energies_array(),
        calculation.structures.structure_potential_energies_array()
        + calculation.structures.structure_kinetic_energies_array(),
    )


def test_parse_vasprun_sequence_keeps_topology_change_frame_for_deletion(tmp_path) -> None:
    _write_vasprun(
        tmp_path / "vasprun1.xml",
        ["H", "O", "C"],
        [
            [[0.0, 0.0, 0.0], [0.3, 0.3, 0.3], [0.7, 0.7, 0.7]],
            [[0.1, 0.0, 0.0], [0.4, 0.3, 0.3], [0.8, 0.7, 0.7]],
        ],
    )
    _write_vasprun(
        tmp_path / "vasprun2.xml",
        ["H", "C"],
        [
            [[0.1, 0.0, 0.0], [0.8, 0.7, 0.7]],
            [[0.2, 0.0, 0.0], [0.9, 0.7, 0.7]],
        ],
    )

    calculation, report = parse_vasprun_sequence(
        tmp_path,
        policy=StructuresMergePolicy(
            boundary_search_frames=1,
            allow_mismatch_fallback=False,
            keep_topology_change_frame=True,
        ),
    )
    structures = calculation.structures

    assert report.events[1].status == "deletion_overlap"
    assert report.events[1].deleted_atom_ids == (1,)
    assert report.deleted_atom_ids == (1,)
    assert structures.step_count == 4
    assert structures.atom_count == 3
    assert structures.frame(2).atom_ids.tolist() == [0, 2]
    assert structures.presence_mask()[2].tolist() == [True, False, True]


def test_parse_vasprun_sequence_no_fallback_raises_on_mismatch(tmp_path) -> None:
    _write_vasprun(
        tmp_path / "vasprun1.xml",
        ["H"],
        [
            [[0.0, 0.0, 0.0]],
            [[0.1, 0.0, 0.0]],
        ],
    )
    _write_vasprun(
        tmp_path / "vasprun2.xml",
        ["H"],
        [
            [[0.8, 0.0, 0.0]],
            [[0.9, 0.0, 0.0]],
        ],
    )

    with pytest.raises(ValueError, match="Boundary frames could not be matched"):
        parse_vasprun_sequence(
            tmp_path,
            policy=StructuresMergePolicy(boundary_search_frames=1, allow_mismatch_fallback=False),
        )


def _write_vasprun(path, symbols: list[str], direct_frames: list[list[list[float]]]) -> None:
    atom_count = len(symbols)
    atom_types = {symbol: index + 1 for index, symbol in enumerate(dict.fromkeys(symbols))}
    masses = {"H": 1.008, "C": 12.011, "O": 15.999}
    unique_symbols = tuple(dict.fromkeys(symbols))
    pomass = " ".join(str(masses.get(symbol, 10.0)) for symbol in unique_symbols)
    rows = [
        "<modeling>",
        f"  <atoms>{atom_count}</atoms>",
        f'  <i name="POTIM">1.0</i>',
        f'  <v name="POMASS"> {pomass} </v>',
        '  <field type="int">atomtype</field>',
    ]
    rows.extend(
        f"  <c>{symbol}</c><c>{atom_types[symbol]}</c>"
        for symbol in symbols
    )
    rows.extend(
        [
            '  <varray name="basis">',
            "    <v>10.0 0.0 0.0</v>",
            "    <v>0.0 10.0 0.0</v>",
            "    <v>0.0 0.0 10.0</v>",
            "  </varray>",
        ]
    )
    for frame in direct_frames:
        rows.extend(
            [
                "  <calculation>",
                "    <energy>",
                f"      <i name=\"e_fr_energy\">{-float(len(rows))}</i>",
                "      <i name=\"kinetic\">1.5</i>",
                "    </energy>",
                '    <varray name="basis">',
                "      <v>10.0 0.0 0.0</v>",
                "      <v>0.0 10.0 0.0</v>",
                "      <v>0.0 0.0 10.0</v>",
                "    </varray>",
                '    <varray name="positions">',
            ]
        )
        rows.extend(f"      <v>{x} {y} {z}</v>" for x, y, z in frame)
        rows.extend(
            [
                "    </varray>",
                '    <varray name="forces">',
            ]
        )
        rows.extend("      <v>0.0 0.0 0.0</v>" for _ in frame)
        rows.extend(
            [
                "    </varray>",
                "  </calculation>",
            ]
        )
    rows.append("</modeling>")
    path.write_text("\n".join(rows), encoding="utf-8")
