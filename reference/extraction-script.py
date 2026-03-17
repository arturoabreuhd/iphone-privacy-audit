#!/usr/bin/env python3
"""
iPhone Privacy Audit — Device Connection & Database Extraction
Handles pymobiledevice3 connection, device info, and Photos.sqlite extraction.
"""

import sys
import os
import json
import tempfile
import shutil
from pathlib import Path


def check_dependencies():
    """Check if pymobiledevice3 is installed."""
    try:
        import pymobiledevice3
        return True, pymobiledevice3.__version__ if hasattr(pymobiledevice3, '__version__') else 'unknown'
    except ImportError:
        return False, None


def install_pymobiledevice3():
    """Install pymobiledevice3 via pip."""
    import subprocess
    result = subprocess.run(
        [sys.executable, '-m', 'pip', 'install', 'pymobiledevice3'],
        capture_output=True, text=True
    )
    return result.returncode == 0, result.stdout + result.stderr


def list_devices():
    """List connected iOS devices."""
    try:
        from pymobiledevice3.usbmux import list_devices
        devices = list_devices()
        return [{'udid': d.serial, 'connection_type': str(d.connection_type)} for d in devices]
    except Exception as e:
        return {'error': str(e)}


def get_device_info():
    """Get comprehensive device information."""
    try:
        from pymobiledevice3.lockdown import create_using_usbmux
        lockdown = create_using_usbmux()
        all_values = lockdown.all_values

        info = {
            'device_name': all_values.get('DeviceName', 'Unknown'),
            'product_type': all_values.get('ProductType', 'Unknown'),
            'product_name': all_values.get('ProductName', 'Unknown'),
            'ios_version': all_values.get('ProductVersion', 'Unknown'),
            'build_version': all_values.get('BuildVersion', 'Unknown'),
            'serial_number': all_values.get('SerialNumber', 'Unknown'),
            'udid': all_values.get('UniqueDeviceID', 'Unknown'),
            'wifi_mac': all_values.get('WiFiAddress', 'Unknown'),
            'bluetooth_mac': all_values.get('BluetoothAddress', 'Unknown'),
            'model_number': all_values.get('ModelNumber', 'Unknown'),
            'hardware_model': all_values.get('HardwareModel', 'Unknown'),
            'chip_id': all_values.get('ChipID', 'Unknown'),
            'disk_usage': {
                'total': all_values.get('TotalDiskCapacity', 0),
                'available': all_values.get('AmountDataAvailable', 0),
            },
        }
        return info
    except Exception as e:
        return {'error': str(e)}


def get_battery_info():
    """Get battery diagnostics."""
    try:
        from pymobiledevice3.lockdown import create_using_usbmux
        from pymobiledevice3.services.diagnostics import DiagnosticsService
        lockdown = create_using_usbmux()
        diag = DiagnosticsService(lockdown)

        battery = diag.get_battery()
        return battery
    except Exception as e:
        return {'error': str(e)}


def extract_photos_db(output_dir=None):
    """Extract Photos.sqlite from the connected iPhone via AFC."""
    if output_dir is None:
        output_dir = tempfile.mkdtemp(prefix='iphone-audit-')

    output_path = os.path.join(output_dir, 'Photos.sqlite')

    try:
        from pymobiledevice3.lockdown import create_using_usbmux
        from pymobiledevice3.services.afc import AfcService
        lockdown = create_using_usbmux()
        afc = AfcService(lockdown)

        # Try common paths for Photos.sqlite
        paths_to_try = [
            '/PhotoData/Photos.sqlite',
            '/MediaAnalysis/mediaanalysis.db',
        ]

        extracted = {}

        for remote_path in paths_to_try:
            local_name = os.path.basename(remote_path)
            local_path = os.path.join(output_dir, local_name)
            try:
                data = afc.get_file_contents(remote_path)
                with open(local_path, 'wb') as f:
                    f.write(data)
                extracted[local_name] = {
                    'path': local_path,
                    'size': len(data),
                    'remote_path': remote_path,
                }
            except Exception as e:
                extracted[local_name] = {'error': str(e), 'remote_path': remote_path}

        # Also try to list what's in PhotoData
        try:
            photo_data_contents = afc.listdir('/PhotoData/')
            extracted['_photodata_listing'] = photo_data_contents
        except Exception:
            pass

        return {
            'output_dir': output_dir,
            'extracted': extracted,
        }

    except Exception as e:
        return {'error': str(e), 'output_dir': output_dir}


def list_dcim_files(limit=50):
    """List files in DCIM to check for 'deleted' files still on disk."""
    try:
        from pymobiledevice3.lockdown import create_using_usbmux
        from pymobiledevice3.services.afc import AfcService
        lockdown = create_using_usbmux()
        afc = AfcService(lockdown)

        # List DCIM subdirectories
        dcim_dirs = afc.listdir('/DCIM/')
        all_files = []

        for subdir in sorted(dcim_dirs):
            if subdir.startswith('.'):
                continue
            try:
                files = afc.listdir(f'/DCIM/{subdir}/')
                for f in files:
                    if f.startswith('.'):
                        continue
                    all_files.append(f'/DCIM/{subdir}/{f}')
                    if len(all_files) >= limit:
                        break
            except Exception:
                continue
            if len(all_files) >= limit:
                break

        return {
            'dcim_directories': [d for d in dcim_dirs if not d.startswith('.')],
            'sample_files': all_files,
            'total_dirs': len([d for d in dcim_dirs if not d.startswith('.')]),
        }

    except Exception as e:
        return {'error': str(e)}


def cleanup(output_dir):
    """Remove all extracted data."""
    try:
        shutil.rmtree(output_dir)
        return {'cleaned': True, 'path': output_dir}
    except Exception as e:
        return {'error': str(e)}


# CLI interface
if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python extraction-script.py <command> [args]")
        print("Commands: check, install, devices, info, battery, extract [output_dir], dcim [limit], cleanup <dir>")
        sys.exit(1)

    command = sys.argv[1]

    if command == 'check':
        installed, version = check_dependencies()
        print(json.dumps({'installed': installed, 'version': version}))

    elif command == 'install':
        success, output = install_pymobiledevice3()
        print(json.dumps({'success': success, 'output': output[:2000]}))

    elif command == 'devices':
        print(json.dumps(list_devices(), default=str))

    elif command == 'info':
        print(json.dumps(get_device_info(), default=str))

    elif command == 'battery':
        print(json.dumps(get_battery_info(), default=str))

    elif command == 'extract':
        output_dir = sys.argv[2] if len(sys.argv) > 2 else None
        print(json.dumps(extract_photos_db(output_dir), default=str))

    elif command == 'dcim':
        limit = int(sys.argv[2]) if len(sys.argv) > 2 else 50
        print(json.dumps(list_dcim_files(limit), default=str))

    elif command == 'cleanup':
        if len(sys.argv) < 3:
            print(json.dumps({'error': 'Specify directory to clean'}))
        else:
            print(json.dumps(cleanup(sys.argv[2])))

    else:
        print(json.dumps({'error': f'Unknown command: {command}'}))
