from __future__ import annotations

import pathlib
import runpy
import sys

from aeye.runtime import bootstrap_runtime, configure_runtime


def launch_target(target_file: pathlib.Path, file_args: list[str]) -> None:
    configure_runtime(target_file.parent)
    bootstrap_runtime()

    sys.argv = [str(target_file), *file_args]
    sys.path.insert(0, str(target_file.parent))
    runpy.run_path(str(target_file), run_name="__main__")
