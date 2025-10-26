"""
GÎ!W

Ð›ÍGÎž°Œå‚ýp
"""

import os
from typing import Literal

from src.domain.interfaces.i_slicer import ISlicer
from src.infrastructure.slicing.orca_slicer import OrcaSlicer
from src.infrastructure.slicing.cura_slicer import CuraEngineSlicer
from src.infrastructure.slicing.mock_slicer import MockSlicer


SlicerType = Literal["orca", "cura", "mock"]


def get_slicer(slicer_type: SlicerType = "orca") -> ISlicer:
    """
    ·ÖGÎž‹ (å‚ýp)

    /Ç¯ƒØÏ SLICER_ENGINE MnGÎ{‹:
    - orca: OrcaSlicer (Ø¤,¨P(Ž Bambu Lab Sp:)
    - cura: CuraEngine ((GÎ)
    - mock: MockSlicer (KÕ()

    Args:
        slicer_type: GÎ{‹,Ø¤Î¯ƒØÏûÖ

    Returns:
        ISlicer: GÎž‹

    Raises:
        ValueError: ‚œš„GÎ{‹/

    Example:
        >>> slicer = get_slicer("orca")
        >>> result = await slicer.slice_model(...)
    """
    # Î¯ƒØÏûÖMn,H§: Âp > ¯ƒØÏ > Ø¤<
    env_slicer = os.getenv("SLICER_ENGINE", "orca").lower()
    selected_slicer = slicer_type or env_slicer

    if selected_slicer == "orca":
        orca_path = os.getenv(
            "ORCA_SLICER_PATH",
            "/usr/local/bin/orcaslicer"
        )
        return OrcaSlicer(orca_slicer_path=orca_path)

    elif selected_slicer == "cura":
        cura_path = os.getenv(
            "CURA_ENGINE_PATH",
            "/usr/local/bin/CuraEngine"
        )
        definitions_dir = os.getenv(
            "CURA_DEFINITIONS_DIR",
            "/app/resources/cura_definitions"
        )
        return CuraEngineSlicer(
            cura_engine_path=cura_path,
            definitions_dir=definitions_dir
        )

    elif selected_slicer == "mock":
        return MockSlicer()

    else:
        raise ValueError(
            f"Unsupported slicer type: {selected_slicer}. "
            f"Supported types: orca, cura, mock"
        )


__all__ = [
    "ISlicer",
    "OrcaSlicer",
    "CuraEngineSlicer",
    "MockSlicer",
    "get_slicer",
    "SlicerType"
]
