import json
from typing import Literal

from pydantic import BaseModel


class PomoConfig(BaseModel):
    work_min: int = 45
    short_break_min: int = 15
    long_break_min: int = 60
    cycles_before_long: int = 4
    total_cycles: int = 7


class PomoState(BaseModel):
    config: PomoConfig
    current_cycle: int
    phase: Literal["work", "short_break", "long_break"]
    remaining_sec: int
    end_time: float | None = None
    is_running: bool = False


phase_to_emoji_dict: dict[str, str] = {
    "work": "▶",
    "short_break": "☕",
    "long_break": "🍽️",
}


def phase_to_emoji(phase: str) -> str:
    return phase_to_emoji_dict.get(phase, "⏱️")


def get_waybar_print(
    state: PomoState,
    config: PomoConfig,
) -> str:
    if not state:
        emoji: str = "⏸"
    else:
        emoji: str = phase_to_emoji(state.phase)

    mins, secs = divmod(state.remaining_sec, 60)

    return json.dumps(
        {
            "text": f"{mins:02d}:{secs:02d} {phase_to_emoji(state.phase)}",
            "tooltip": f"Cycle: {state.current_cycle}/{config.total_cycles}\nPhase: {state.phase}",
        },
        ensure_ascii=False,
    )
