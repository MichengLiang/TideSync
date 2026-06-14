from __future__ import annotations

import importlib
from pathlib import Path

CONTROLLED_SOURCE = Path("forks/vision-agents-qwen-native")


def test_vision_agents_runtime_uses_controlled_source() -> None:
    project_root = Path(__file__).resolve().parents[1]
    controlled_root = (project_root / CONTROLLED_SOURCE).resolve()

    module_names = [
        "vision_agents.core",
        "vision_agents.plugins.qwen",
        "vision_agents.plugins.qwen.qwen_realtime",
        "vision_agents.plugins.getstream",
    ]

    loaded_paths = {
        module_name: Path(str(importlib.import_module(module_name).__file__)).resolve()
        for module_name in module_names
    }

    for module_name, module_path in loaded_paths.items():
        assert module_path.is_relative_to(controlled_root), (
            f"{module_name} loaded from {module_path}, expected a path under {controlled_root}"
        )
