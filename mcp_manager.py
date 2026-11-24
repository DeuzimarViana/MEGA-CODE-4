#!/usr/bin/env python3
"""Safe local MCP lifecycle manager for MEGA-CODE-4.

This manager is intentionally defensive: it only manages local, verified MCP-like
services that are part of the repository or explicitly declared as safe. It does not
start dangerous tools like HexStrike or unverified network scanning services.
"""
from __future__ import annotations

import argparse
import json
import os
import signal
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

try:
    import psutil  # type: ignore
except Exception:  # pragma: no cover
    psutil = None

try:
    import requests  # type: ignore
except Exception:  # pragma: no cover
    requests = None

ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data"
PREFS_PATH = DATA_DIR / "mcp_prefs.json"
PIDS_PATH = DATA_DIR / "mcp_pids.json"

DEFAULT_PREFS = {
    "dummy_mcp": False,
    "coarena_tambor": False,
    "hexstrike": False,
    "cyberstrike_cve": False,
}


def ensure_data_dir() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def load_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default


def save_json(path: Path, payload: Any) -> None:
    ensure_data_dir()
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    tmp.replace(path)


def bootstrap_prefs() -> Dict[str, bool]:
    ensure_data_dir()
    prefs = load_json(PREFS_PATH, DEFAULT_PREFS)
    merged = DEFAULT_PREFS.copy()
    if isinstance(prefs, dict):
        for key, value in prefs.items():
            if key in merged:
                merged[key] = bool(value)
    save_json(PREFS_PATH, merged)
    return merged


def bootstrap_pids() -> Dict[str, int]:
    ensure_data_dir()
    pids = load_json(PIDS_PATH, {})
    cleaned = {}
    for key, value in pids.items():
        try:
            cleaned[key] = int(value)
        except Exception:
            continue
    save_json(PIDS_PATH, cleaned)
    return cleaned


def is_process_alive(pid: int) -> bool:
    if psutil is None:
        try:
            os.kill(pid, 0)
            return True
        except OSError:
            return False
    try:
        proc = psutil.Process(pid)
        return proc.is_running()
    except Exception:
        return False


def find_port_pid(port: int) -> Optional[int]:
    if psutil is None:
        return None
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            cmdline = proc.info.get('cmdline') or []
        except Exception:
            continue
        if not cmdline:
            continue
        combined = " ".join(cmdline)
        if f"--port {port}" in combined or f"--port={port}" in combined:
            return int(proc.info.get('pid') or 0)
    return None


def http_healthcheck(url: str, timeout: float = 2.0) -> bool:
    if requests is None:
        return False
    try:
        response = requests.get(url, timeout=timeout)
        return response.ok
    except Exception:
        return False


def get_status_for_service(service_name: str, port: int) -> str:
    prefs = bootstrap_prefs()
    pids = bootstrap_pids()
    pid = pids.get(service_name)
    if not prefs.get(service_name, False):
        return "OFF"
    if pid is not None and is_process_alive(pid):
        if port and http_healthcheck(f"http://127.0.0.1:{port}/", timeout=1.5):
            return "ON"
        return "UNKNOWN"
    if port:
        if http_healthcheck(f"http://127.0.0.1:{port}/", timeout=1.5):
            return "ON"
    return "OFF"


def start_service(service_name: str, command: List[str], port: int, cwd: Optional[str] = None) -> Dict[str, Any]:
    """Start a local MCP-like service safely. Dangerous services must be blocked."""
    allowlist = {"dummy_mcp", "coarena_tambor"}
    if service_name not in allowlist:
        raise RuntimeError(f"Service '{service_name}' is not allowed by the safe local MCP policy.")

    prefs = bootstrap_prefs()
    pids = bootstrap_pids()
    if not prefs.get(service_name, False):
        raise RuntimeError(f"Service '{service_name}' is disabled in data/mcp_prefs.json")

    # refuse dangerous endpoints / host bindings outside localhost
    for arg in command:
        if arg in {"0.0.0.0", "::", "*"}:
            raise RuntimeError("Refusing to bind a safe local MCP service to a public interface.")

    record = {
        "service": service_name,
        "pid": None,
        "status": "starting",
        "port": port,
        "started_at": time.time(),
    }

    proc = subprocess.Popen(
        command,
        cwd=str(cwd) if cwd else str(ROOT),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        start_new_session=True,
    )
    pid = proc.pid
    pids[service_name] = pid
    save_json(PIDS_PATH, pids)
    record["pid"] = pid

    for _ in range(30):
        if is_process_alive(pid):
            if http_healthcheck(f"http://127.0.0.1:{port}/", timeout=1.5):
                record["status"] = "ON"
                return record
        time.sleep(0.1)

    os.kill(pid, signal.SIGKILL)
    pids.pop(service_name, None)
    save_json(PIDS_PATH, pids)
    raise RuntimeError(f"Health check failed for '{service_name}' on 127.0.0.1:{port}. Process terminated.")


def stop_service(service_name: str) -> Dict[str, Any]:
    pids = bootstrap_pids()
    pid = pids.get(service_name)
    result = {"service": service_name, "pid": pid, "status": "OFF"}

    if pid is None or not is_process_alive(pid):
        pids.pop(service_name, None)
        save_json(PIDS_PATH, pids)
        return result

    try:
        os.kill(pid, signal.SIGTERM)
    except OSError:
        pass
    deadline = time.time() + 2.0
    while time.time() < deadline:
        if not is_process_alive(pid):
            break
        time.sleep(0.1)
    if is_process_alive(pid):
        try:
            os.kill(pid, signal.SIGKILL)
        except OSError:
            pass

    if not is_process_alive(pid):
        pids.pop(service_name, None)
        save_json(PIDS_PATH, pids)
        result["status"] = "OFF"
        return result

    result["status"] = "UNKNOWN"
    return result


def render_status_table() -> None:
    print("Safe local MCP status")
    print("-" * 58)
    print(f"{'Service':<22} {'Preference':<10} {'State':<8} {'Port':<6}")
    print("-" * 58)
    for name, port in (
        ("dummy_mcp", 8889),
        ("coarena_tambor", 8892),
        ("hexstrike", 8889),
        ("cyberstrike_cve", 8891),
    ):
        prefs = bootstrap_prefs()
        status = get_status_for_service(name, port)
        pref = "ON" if prefs.get(name, False) else "OFF"
        print(f"{name:<22} {pref:<10} {status:<8} {port:<6}")
    print("-" * 58)
    print("Note: HexStrike and other dangerous integrations are intentionally disabled by policy.")


def interactive_prompt() -> None:
    prefs = bootstrap_prefs()
    print("Safe local MCP manager")
    print("1) Toggle dummy_mcp")
    print("2) Toggle coarena_tambor")
    print("3) Show status")
    print("4) Exit")
    choice = input("Select option [1-4]: ").strip()
    if choice == "1":
        service = "dummy_mcp"
        enabled = not prefs.get(service, False)
        prefs[service] = enabled
        save_json(PREFS_PATH, prefs)
        print(f"dummy_mcp set to {enabled}")
        if enabled:
            command = [sys.executable, str(ROOT / "dummy_mcp.py"), "--port", "8889"]
            try:
                start_service(service, command, 8889, cwd=str(ROOT))
                print("dummy_mcp launched successfully")
            except Exception as exc:
                print(f"dummy_mcp launch failed: {exc}")
                prefs[service] = False
                save_json(PREFS_PATH, prefs)
        else:
            stop_service(service)
    elif choice == "2":
        service = "coarena_tambor"
        enabled = not prefs.get(service, False)
        prefs[service] = enabled
        save_json(PREFS_PATH, prefs)
        print(f"coarena_tambor set to {enabled}")
    elif choice == "3":
        render_status_table()
    elif choice == "4":
        return
    else:
        print("Invalid option")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Safe local MCP lifecycle manager")
    parser.add_argument("--status", action="store_true", help="Show current local MCP status")
    parser.add_argument("--toggle", choices=["dummy_mcp", "coarena_tambor"], help="Toggle a local service on/off")
    parser.add_argument("--on", choices=["dummy_mcp", "coarena_tambor"], help="Turn a safe local service on")
    parser.add_argument("--off", choices=["dummy_mcp", "coarena_tambor"], help="Turn a safe local service off")
    parser.add_argument("--port", type=int, default=8889, help="Port used by a safe local service")
    parser.add_argument("--interactive", action="store_true", help="Run interactive TUI")
    return parser.parse_args()


def main() -> int:
    ensure_data_dir()
    args = parse_args()
    bootstrap_prefs()
    bootstrap_pids()

    if args.status:
        render_status_table()
        return 0

    if args.toggle:
        prefs = bootstrap_prefs()
        enabled = not prefs.get(args.toggle, False)
        prefs[args.toggle] = enabled
        save_json(PREFS_PATH, prefs)
        print(f"{args.toggle} -> {'ON' if enabled else 'OFF'}")
        return 0

    if args.on:
        prefs = bootstrap_prefs()
        prefs[args.on] = True
        save_json(PREFS_PATH, prefs)
        if args.on == "dummy_mcp":
            try:
                start_service(args.on, [sys.executable, str(ROOT / "dummy_mcp.py"), "--port", str(args.port)], args.port, cwd=str(ROOT))
                print(f"{args.on} started successfully on 127.0.0.1:{args.port}")
            except Exception as exc:
                print(f"Failed to start {args.on}: {exc}")
                return 1
        return 0

    if args.off:
        prefs = bootstrap_prefs()
        prefs[args.off] = False
        save_json(PREFS_PATH, prefs)
        stop_service(args.off)
        print(f"{args.off} -> OFF")
        return 0

    if args.interactive:
        while True:
            interactive_prompt()
            if input("Run again? [y/N]: ").strip().lower() not in {"y", "yes"}:
                break
        return 0

    render_status_table()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
