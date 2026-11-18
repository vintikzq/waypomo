import sys
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
    json_path.mkdir(parents=True, exist_ok=True)
    json_path.write_text(model.model_dump_json(indent=2), encoding="utf-8")


def load_json_into_model(json_path: Path, model):
    return model.model_validate_json(json_path.read_text(encoding="utf-8"))


if not state_file.exists():
    if not config_file.exists():
        default_config = PomoConfig()
        save_model_to_json(json_path=config_file, model=default_config)

    config: PomoConfig = load_json_into_model(json_path=config_file, model=PomoConfig)

    state = PomoState(
        config=config,
        current_cycle=1,
        phase="work",
        remaining_sec=config.work_min * 60,
        is_running=False,
    )

    save_model_to_json(json_path=state_file, model=state)

    mins, secs = divmod(state.remaining_sec, 60)

    print(
        get_waybar_print(
            config=config,
            state=state,
            mins=mins,
            secs=secs,
        )
    )

    sys.exit(0)
