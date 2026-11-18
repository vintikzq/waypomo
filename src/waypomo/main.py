import sys
import time
from pathlib import Path

from pydantic import BaseModel

from waypomo.schemas.config_schema import (
    PomoConfig,
    PomoState,
    get_waybar_print,
)

home_dir: Path = Path.home()

state_dir: Path = home_dir / ".cache" / "pomo"
config_dir: Path = home_dir / ".config" / "pomo"

config_file: Path = config_dir / "config.json"
state_file: Path = state_dir / "state.json"


def save_model_to_json(json_path: Path, model: BaseModel) -> None:
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(model.model_dump_json(indent=2), encoding="utf-8")


def load_json_into_model(json_path: Path, model):
    return model.model_validate_json(json_path.read_text(encoding="utf-8"))


cmd: str = sys.argv[1] if len(sys.argv) > 1 else "tick"


if cmd == "toggle":
    state: PomoState = load_json_into_model(json_path=state_file, model=PomoState)

    state.is_running = not state.is_running

    if state.is_running:
        state.end_time = time.time() + state.remaining_sec
    else:
        state.end_time = None

    save_model_to_json(json_path=state_file, model=state)

    sys.exit(0)

elif cmd == "tick":
    if not state_file.exists():
        if not config_file.exists():
            default_config = PomoConfig()
            save_model_to_json(json_path=config_file, model=default_config)

        config: PomoConfig = load_json_into_model(
            json_path=config_file, model=PomoConfig
        )

        state = PomoState(
            config=config,
            current_cycle=1,
            phase="work",
            remaining_sec=config.work_min * 60,
            is_running=False,
        )

        save_model_to_json(json_path=state_file, model=state)

        print(
            get_waybar_print(
                config=config,
                state=state,
            )
        )

        sys.exit(0)

    state: PomoState = load_json_into_model(json_path=state_file, model=PomoState)

    if not state.is_running:
        print(
            get_waybar_print(
                config=state.config,
                state=state,
            )
        )
        sys.exit(0)

    if state.is_running and state.end_time:
        state.remaining_sec = max(0, int(state.end_time - time.time()))
        try:
            if state.current_cycle == state.config.total_cycles:
                state.current_cycle = 1
                config: PomoConfig = load_json_into_model(
                    json_path=config_file, model=PomoConfig
                )
                state.config = config
                state.is_running = False
                state.end_time = None
                state.phase = "work"
                state.remaining_sec = state.config.work_min * 60

            elif (
                state.remaining_sec == 0
                and state.phase == "work"
                and state.current_cycle == state.config.cycles_before_long
            ):
                state.phase = "long_break"
                state.remaining_sec = state.config.long_break_min * 60
                state.end_time = time.time() + state.remaining_sec

            elif state.remaining_sec == 0 and (
                state.phase == "long_break" or state.phase == "short_break"
            ):
                state.phase = "work"
                state.remaining_sec = state.config.work_min * 60
                state.current_cycle += 1
                state.end_time = time.time() + state.remaining_sec

            elif state.remaining_sec == 0 and state.phase == "work":
                state.phase = "short_break"
                state.remaining_sec = state.config.short_break_min * 60
                state.end_time = time.time() + state.remaining_sec

        finally:
            save_model_to_json(json_path=state_file, model=state)
            print(
                get_waybar_print(
                    config=state.config,
                    state=state,
                )
            )
            sys.exit(0)


else:
    pass
