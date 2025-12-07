"""Cross-platform pexpect spawner abstraction.

Provides a unified API for spawning processes that works on both Windows and POSIX.
"""

import sys
from typing import TYPE_CHECKING

import pexpect

if TYPE_CHECKING:
    import pexpect.popen_spawn

if sys.platform.startswith("win32"):
    import pexpect.popen_spawn

    class _CrossPlatformSpawn(pexpect.popen_spawn.PopenSpawn):
        """Windows-compatible spawn with isalive/terminate methods."""

        def isalive(self) -> bool:
            return self.proc.poll() is None

        def terminate(self, force: bool = False) -> None:
            if force:
                self.proc.kill()
            else:
                self.proc.terminate()
else:
    _CrossPlatformSpawn = pexpect.spawn


def spawn_cli(
    cmd_args: list[str],
    encoding: str = "utf-8",
    timeout: float = 10.0,
    env: dict[str, str] | None = None,
):
    """Spawn a command cross-platform using pexpect.

    Args:
        cmd_args: Command and arguments as a list
        encoding: Text encoding
        timeout: Timeout in seconds
        env: Environment variables

    Returns:
        A spawn object compatible with pexpect API
    """
    if sys.platform.startswith("win32"):
        # Windows requires command as a single string
        cmd = " ".join(cmd_args)
        return _CrossPlatformSpawn(
            cmd,
            encoding=encoding,
            timeout=timeout,
            env=env,
        )
    else:
        # POSIX uses exec-style args
        return pexpect.spawn(
            cmd_args[0],
            args=cmd_args[1:],
            encoding=encoding,
            timeout=timeout,
            env=env,
        )
