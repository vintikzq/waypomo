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
