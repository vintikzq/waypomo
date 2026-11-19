import json
from dataclasses import asdict, dataclass, is_dataclass
from typing import Literal, Self


class JsonMixin:
    def to_json(self) -> str:
        if not is_dataclass(self):
            raise TypeError("JsonMixin can only be used with dataclasses")
        return json.dumps(asdict(self))

    @classmethod
    def from_json(cls, raw: str) -> Self:
        return cls(**json.loads(raw))


@dataclass
class PomoConfig(JsonMixin):
    work_min: int = 45
    short_break_min: int = 15
    long_break_min: int = 60
    cycles_before_long: int = 4
    total_cycles: int = 7


@dataclass
class PomoState(JsonMixin):
    config: PomoConfig
    current_cycle: int
    phase: Literal["work", "short_break", "long_break"]
    remaining_sec: int
    end_time: float | None = None
    is_running: bool = False

    def __post_init__(self) -> None:
        if isinstance(self.config, dict):
            self.config = PomoConfig(**self.config)


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
    if not state.is_running:
        emoji = "⏸"
    else:
        emoji = phase_to_emoji(state.phase)

    mins, secs = divmod(state.remaining_sec, 60)

    return json.dumps(
        {
            "text": f"{mins:02d}:{secs:02d} {emoji}",
            "tooltip": f"Cycle: {state.current_cycle}/{config.total_cycles}\nPhase: {state.phase}",
        },
        ensure_ascii=False,
    )
