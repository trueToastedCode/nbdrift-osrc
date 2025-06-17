#!/usr/bin/env python3
import hashlib
from enum import StrEnum
import random
import argparse
import json
import sys
from pathlib import Path

IOT_VCU_LIGHT_URL = "http://localhost:5000/images/bright/ic_fw_vcu.png"
IOT_VCU_DARK_URL = "http://localhost:5000/images/dark/ic_fw_vcu.png"
IOT_VCU_DOWN_URL = "http://localhost:5000/fw/zt3pro/vcu.bin.enc"

class PartType(StrEnum):
    VCU = 'vcu'

class UpdateEndpoint(StrEnum):
    IOT = 'iot'

def get_md5(data):
    """Calculate MD5 hash of binary data."""
    return hashlib.md5(data).hexdigest()

def calc_nb_verify_code(data):
    """Calculate verification code from binary data."""
    total = sum(data)
    return abs((~total) * 17) % 100000000

def get_random_task_code():
    """Generate random task code."""
    return str(random.randint(10**11, 10**12 - 1))

def read_firmware_file(filepath):
    """Read firmware file and return binary data."""
    try:
        with open(filepath, 'rb') as f:
            return f.read()
    except FileNotFoundError:
        print(f"Error: Firmware file '{filepath}' not found.", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error reading firmware file: {e}", file=sys.stderr)
        sys.exit(1)

def make_payload(update_endpoint, parts):
    """Generate payload for firmware update."""
    parts_payload = []
    if update_endpoint == UpdateEndpoint.IOT:
        for part in parts:
            part_type = PartType(part['part_type'])
            if part_type == PartType.VCU:
                part_payload = {
                    "part_type": "VCU",
                    "last_version": part['version_code'],
                    "version_content": f'{part["description"]}\n',
                    "pn": part['cpu_id'],
                    "part_name": "Vehicle controller",
                    "light_url": IOT_VCU_LIGHT_URL,
                    "dark_url": IOT_VCU_DARK_URL,
                    "blue_down_url": IOT_VCU_DOWN_URL,
                    "md5": get_md5(part['data']),
                    "verify_code": calc_nb_verify_code(part['data']),
                    "cpuid": part['cpu_id'],
                    "random_code": part['rand'],
                    "has_secret": 1,
                    "task_code": get_random_task_code(),
                    "source": 1,
                    "firmware_type": 1
                }
                parts_payload.append(part_payload)
    else:
        raise ValueError('Unexpected update endpoint')
    
    return {
        "code": 1,
        "data": {
            "parts_version": parts_payload,
            "show_kart_tip": False,
            "special_version_status": False,
            "forced_status": False,
            "forced_content": "",
            "sub_wnumber": "",
            "source": 1
        },
        "desc": "Successfully"
    }

def create_part_from_args(args):
    """Create part dictionary from command line arguments."""
    # Read firmware data
    firmware_data = read_firmware_file(args.firmware)
    
    return {
        'part_type': args.part_type,
        'version_code': args.version_code,
        'description': args.description,
        'cpu_id': args.cpu_id,
        'data': firmware_data,
        'rand': args.random_code if args.random_code else str(random.randint(1000, 9999))
    }

def load_config_file(config_path):
    """Load configuration from JSON file."""
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        # Validate required fields
        required_fields = ['parts']
        for field in required_fields:
            if field not in config:
                print(f"Error: Missing required field '{field}' in config file.", file=sys.stderr)
                sys.exit(1)
        
        # Load firmware data for each part
        for part in config['parts']:
            if 'firmware_file' in part:
                part['data'] = read_firmware_file(part['firmware_file'])
                # Remove the file path from the part data
                del part['firmware_file']
            
            # Set default random code if not provided
            if 'rand' not in part:
                part['rand'] = str(random.randint(1000, 9999))
        
        return config
    except FileNotFoundError:
        print(f"Error: Config file '{config_path}' not found.", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error parsing config file: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error loading config file: {e}", file=sys.stderr)
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(
        description='Generate firmware update payloads',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate payload from command line arguments
  python firmware_cli.py --firmware vcu.bin --version-code "331" --cpu-id "ABC123" --description "Bug fixes"
  
  # Generate payload from config file
  python firmware_cli.py --config config.json
  
  # Save output to file
  python firmware_cli.py --firmware vcu.bin --version-code "331" --cpu-id "ABC123" --output payload.json
  
Config file format (JSON):
{
  "endpoint": "iot",
  "parts": [
    {
      "part_type": "vcu",
      "version_code": "331",
      "description": "Bug fixes and improvements",
      "cpu_id": "ABC123",
      "firmware_file": "path/to/vcu.bin",
      "rand": "1234"
    }
  ]
}
        """
    )
    
    # Main operation mode
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--config', '-c', help='Load configuration from JSON file')
    group.add_argument('--firmware', '-f', help='Path to firmware file')
    
    # Arguments for direct mode
    parser.add_argument('--part-type', '-t', choices=['vcu'], default='vcu',
                       help='Part type (default: vcu)')
    parser.add_argument('--version-code', '-v', help='Firmware version code')
    parser.add_argument('--description', '-d', help='Version description')
    parser.add_argument('--cpu-id', help='CPU ID')
    parser.add_argument('--random-code', help='Random code (auto-generated if not provided)')
    
    # Common arguments
    parser.add_argument('--endpoint', '-e', choices=['iot'], default='iot',
                       help='Update endpoint (default: iot)')
    parser.add_argument('--output', '-o', help='Output file (default: stdout)')
    parser.add_argument('--pretty', '-p', action='store_true',
                       help='Pretty print JSON output')
    parser.add_argument('--quiet', '-q', action='store_true',
                       help='Suppress informational messages')
    
    args = parser.parse_args()
    
    try:
        # Determine operation mode
        if args.config:
            # Load from config file
            config = load_config_file(args.config)
            parts = config['parts']
            endpoint = UpdateEndpoint(config.get('endpoint', args.endpoint))
            if not args.quiet:
                print(f"Loaded {len(parts)} part(s) from config file", file=sys.stderr)
        else:
            # Create from command line arguments
            if not all([args.version_code, args.cpu_id]):
                parser.error("When using --firmware, --version-code and --cpu-id are required")
            
            if not args.description:
                args.description = f"Firmware version code {args.version_code}"
            
            part = create_part_from_args(args)
            parts = [part]
            endpoint = UpdateEndpoint(args.endpoint)
            if not args.quiet:
                print(f"Generated part from firmware file: {args.firmware}", file=sys.stderr)
        
        # Generate payload
        payload = make_payload(endpoint, parts)
        
        # Format output
        if args.pretty:
            json_output = json.dumps(payload, indent=2, ensure_ascii=False)
        else:
            json_output = json.dumps(payload, ensure_ascii=False)
        
        # Write output
        if args.output:
            with open(args.output, 'w') as f:
                f.write(json_output)
            if not args.quiet:
                print(f"Payload written to: {args.output}", file=sys.stderr)
        else:
            print(json_output)
            
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()
