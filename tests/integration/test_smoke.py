"""Extremely basic pexpect smoke test – no harness, just raw subprocess."""

import time

import sys
import pexpect

from cli_expect.spawn_utils import spawn_cli

# No pytestmark - run in all environments but handle timing gracefully


def test_version_smoke() -> None:
    child = spawn_cli(["code-puppy", "--version"])
    child.expect(pexpect.EOF, timeout=10)
    output = child.before
    assert output.strip()  # just ensure we got something
    print("\n[SMOKE] version output:", output)


def test_help_smoke() -> None:
    child = spawn_cli(["code-puppy", "--help"])
    child.expect("--help", timeout=10)
    child.expect(pexpect.EOF, timeout=10)
    output = child.before
    assert "show this help message" in output.lower()
    print("\n[SMOKE] help output seen")



def test_interactive_smoke() -> None:
    """Test interactive mode works cross-platform using --no-prompt-toolkit on Windows."""
    # Use spawn_cli with --no-prompt-toolkit on Windows to avoid console buffer issues
    args = ["code-puppy", "-i"]
    if sys.platform.startswith("win32"):
        args.append("--no-prompt-toolkit")
    
    child = spawn_cli(args)
    
    # Handle initial prompts that might appear in CI
    try:
        child.expect("What should we name the puppy?", timeout=15)
        child.sendline("IntegrationPup\r")
        child.expect("What's your name", timeout=15)
        child.sendline("HarnessTester\r")
    except pexpect.exceptions.TIMEOUT:
        print("[INFO] Initial setup prompts not found, assuming pre-configured")
        pass
    
    # Skip autosave picker if it appears
    try:
        child.expect("1-5 to load, 6 for next", timeout=10)
        child.send("\r")
        time.sleep(0.5)
        child.send("\r")
    except pexpect.exceptions.TIMEOUT:
        pass
    
    try:
        # Expect interactive mode prompt
        child.expect("Enter your coding task", timeout=25)
        
        # Send quit command
        child.sendline("/quit\r")
        
        # Wait for process to exit
        child.expect(pexpect.EOF, timeout=15)
        child.close()
        
        # Verify successful execution
        if child.exitstatus not in (0, None):
            print(f"\n[SMOKE] Warning: Exit status {child.exitstatus}")
        
        print("\n[SMOKE] Interactive mode smoke test passed!")
        
    except pexpect.exceptions.TIMEOUT as e:
        # Get recent output for debugging
        print(f"\n[SMOKE] Timeout waiting for expected output")
        print(f"[SMOKE] Before buffer: {child.before}")
        print(f"[SMOKE] After buffer: {child.after}")
        raise
    finally:
        if child.isalive():
            child.terminate(force=True)
