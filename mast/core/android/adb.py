"""ADB (Android Debug Bridge) helper functions."""

from __future__ import annotations

import subprocess
from dataclasses import dataclass
from typing import Any


ADB_TIMEOUT = 60


@dataclass(slots=True)
class DeviceInfo:
    serial: str
    name: str
    model: str
    manufacturer: str
    android_version: str
    api_level: str
    status: str


@dataclass(slots=True)
class PackageInfo:
    package_name: str
    app_name: str
    version_name: str
    version_code: str
    is_system: bool
    is_disabled: bool


def _adb_command(serial: str | None, args: list[str]) -> list[str]:
    cmd = ["adb"]
    if serial:
        cmd.extend(["-s", serial])
    cmd.extend(args)
    return cmd


def _run_adb_command(serial: str | None, args: list[str]) -> str:
    cmd = _adb_command(serial, args)
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=ADB_TIMEOUT,
    )
    return result.stdout.strip()


def list_devices() -> list[DeviceInfo]:
    output = _run_adb_command(None, ["devices", "-l"])
    devices: list[DeviceInfo] = []
    
    for line in output.splitlines():
        line = line.strip()
        if not line or line.startswith("List of devices"):
            continue
        
        parts = line.split()
        if len(parts) < 2:
            continue
        
        serial = parts[0]
        status = parts[1]
        
        if status != "device":
            devices.append(DeviceInfo(
                serial=serial,
                name="",
                model="",
                manufacturer="",
                android_version="",
                api_level="",
                status=status,
            ))
            continue
        
        model = ""
        device = ""
        for part in parts[2:]:
            if part.startswith("model:"):
                model = part[6:]
            elif part.startswith("device:"):
                device = part[7:]
        
        name = device or model
        
        try:
            props = get_device_properties(serial)
            devices.append(DeviceInfo(
                serial=serial,
                name=name,
                model=props.get("ro.product.model", model),
                manufacturer=props.get("ro.product.manufacturer", ""),
                android_version=props.get("ro.build.version.release", ""),
                api_level=props.get("ro.build.version.sdk", ""),
                status=status,
            ))
        except Exception:
            devices.append(DeviceInfo(
                serial=serial,
                name=name,
                model=model,
                manufacturer="",
                android_version="",
                api_level="",
                status=status,
            ))
    
    return devices


def get_device_properties(serial: str) -> dict[str, str]:
    output = _run_adb_command(serial, ["shell", "getprop"])
    props: dict[str, str] = {}
    
    for line in output.splitlines():
        line = line.strip()
        if not line or "[" not in line:
            continue
        
        try:
            key_part, value_part = line.split("]: [", 1)
            key = key_part[1:]
            value = value_part.rstrip("]")
            props[key] = value
        except ValueError:
            continue
    
    return props


def get_device_info(serial: str) -> DeviceInfo:
    props = get_device_properties(serial)
    
    output = _run_adb_command(serial, ["devices", "-l"])
    model = ""
    device = ""
    for line in output.splitlines():
        if serial in line:
            parts = line.split()
            for part in parts:
                if part.startswith("model:"):
                    model = part[6:]
                elif part.startswith("device:"):
                    device = part[7:]
            break
    
    return DeviceInfo(
        serial=serial,
        name=device or model or props.get("ro.product.device", ""),
        model=props.get("ro.product.model", model),
        manufacturer=props.get("ro.product.manufacturer", ""),
        android_version=props.get("ro.build.version.release", ""),
        api_level=props.get("ro.build.version.sdk", ""),
        status="device",
    )


def list_packages(serial: str) -> list[PackageInfo]:
    disabled_output = _run_adb_command(serial, ["shell", "pm", "list", "packages", "-f", "-d"])
    disabled_pkgs: set[str] = set()
    
    for line in disabled_output.splitlines():
        line = line.strip()
        if line.startswith("package:") and "=" in line:
            pkg_name = line.split("=")[1].strip()
            disabled_pkgs.add(pkg_name)
    
    pm_output = _run_adb_command(serial, ["shell", "pm", "list", "packages", "-f"])
    path_by_pkg: dict[str, str] = {}
    is_system_by_pkg: dict[str, bool] = {}
    
    for line in pm_output.splitlines():
        line = line.strip()
        if not line.startswith("package:") or "=" not in line:
            continue
        
        try:
            path_part, pkg_name = line.split("=", 1)
            path = path_part[8:]
            path_by_pkg[pkg_name] = path
            is_system_by_pkg[pkg_name] = path.startswith("/system/") or path.startswith("/product/")
        except ValueError:
            continue
    
    dumpsys_output = _run_adb_command(serial, ["shell", "dumpsys", "package"])
    
    packages: list[PackageInfo] = []
    current_pkg = None
    app_name = ""
    version_name = ""
    version_code = ""
    
    for line in dumpsys_output.splitlines():
        line = line.strip()
        
        if line.startswith("Package [") and line.endswith("]"):
            if current_pkg and current_pkg in path_by_pkg:
                packages.append(PackageInfo(
                    package_name=current_pkg,
                    app_name=app_name or current_pkg,
                    version_name=version_name,
                    version_code=version_code,
                    is_system=is_system_by_pkg.get(current_pkg, False),
                    is_disabled=current_pkg in disabled_pkgs,
                ))
            
            current_pkg = line[9:-1].strip()
            app_name = ""
            version_name = ""
            version_code = ""
            continue
        
        if current_pkg is None:
            continue
        
        if line.startswith("versionName="):
            version_name = line.split("=", 1)[1]
        elif line.startswith("versionCode="):
            version_code = line.split("=", 1)[1]
        elif "label=" in line and not app_name:
            if "label=" in line:
                label_part = line.split("label=", 1)[1]
                if "=" in label_part:
                    label_part = label_part.split("=", 1)[1]
                app_name = label_part.strip().strip('"')
    
    if current_pkg and current_pkg in path_by_pkg:
        packages.append(PackageInfo(
            package_name=current_pkg,
            app_name=app_name or current_pkg,
            version_name=version_name,
            version_code=version_code,
            is_system=is_system_by_pkg.get(current_pkg, False),
            is_disabled=current_pkg in disabled_pkgs,
        ))
    
    return packages


def uninstall_package(serial: str, package_name: str, keep_data: bool = False) -> bool:
    args = ["shell", "pm", "uninstall"]
    if keep_data:
        args.append("-k")
    args.append(package_name)
    
    result = subprocess.run(
        _adb_command(serial, args),
        capture_output=True,
        text=True,
        timeout=ADB_TIMEOUT,
    )
    
    return result.returncode == 0 and "Success" in result.stdout


def install_apk(serial: str, apk_path: str) -> bool:
    result = subprocess.run(
        _adb_command(serial, ["install", "-r", apk_path]),
        capture_output=True,
        text=True,
        timeout=ADB_TIMEOUT,
    )
    
    return result.returncode == 0 and "Success" in result.stdout


def is_adb_available() -> bool:
    try:
        result = subprocess.run(
            ["adb", "--version"],
            capture_output=True,
            text=True,
            timeout=ADB_TIMEOUT,
        )
        return result.returncode == 0
    except FileNotFoundError:
        return False