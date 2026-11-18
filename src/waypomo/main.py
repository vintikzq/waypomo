import subprocess
import sys
import time
from pathlib import Path
from typing import NoReturn

from pydantic import BaseModel

from waypomo.schemas.config_schema import (
    PomoConfig,
    PomoState,
    get_waybar_print,
)


def main() -> NoReturn:
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

    def get_or_create_state() -> PomoState:
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
            return state

        return load_json_into_model(json_path=state_file, model=PomoState)

    state: PomoState = get_or_create_state()

    def advance_phase(phase, state: PomoState) -> PomoState:
        phase_minutes: dict[str, int] = {
            "work": state.config.work_min,
            "short_break": state.config.short_break_min,
            "long_break": state.config.long_break_min,
        }
        state.phase = phase
        state.remaining_sec = phase_minutes[phase] * 60
        state.end_time = time.time() + state.remaining_sec if state.is_running else None
        return state

    def step_to_next_phase(state: PomoState) -> PomoState:
        match state.phase:
            case "work" if state.current_cycle >= state.config.total_cycles:
                state_file.unlink(missing_ok=True)
                state = get_or_create_state()
            case "work" if state.current_cycle % state.config.cycles_before_long == 0:
                state = advance_phase("long_break", state=state)
            case "work":
                state = advance_phase("short_break", state=state)
            case "long_break" | "short_break":
                state = advance_phase("work", state=state)
                state.current_cycle += 1

        return state

    def send_notification(phase: str):
        phase_pharases = {
            "work": "It's time to work!",
            "short_break": "Short break started. Rest your eyes for a few minutes.",
            "long_break": "Long break started. Time to recharge!",
        }

        subprocess.run(
            [
                "notify-send",
                "-u",
                "normal",
                "Waypomo",
                f"{phase_pharases[phase]}",
            ],
            check=False,
        )

    match cmd:
        case "toggle":
            state.is_running = not state.is_running

            if state.is_running:
                state.end_time = time.time() + state.remaining_sec
            else:
                state.end_time = None

            save_model_to_json(json_path=state_file, model=state)
        case "next":
            state = step_to_next_phase(state)
        case "reset":
            state_file.unlink(missing_ok=True)
            state = get_or_create_state()
        case _:
            if not state.is_running:
                print(
                    get_waybar_print(
                        config=state.config,
                        state=state,
                    )
                )
                sys.exit(0)
            elif state.is_running and state.end_time:
                state.remaining_sec = max(0, int(state.end_time - time.time()))
            if state.remaining_sec == 0:
                state = step_to_next_phase(state)
                send_notification(state.phase)

    save_model_to_json(json_path=state_file, model=state)
    print(
        get_waybar_print(
            config=state.config,
            state=state,
        )
    )
    sys.exit(0)


if __name__ == "__main__":
    main()
