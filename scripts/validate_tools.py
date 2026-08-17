#!/usr/bin/env python3
"""
Validation script for Agent Tools & MCP Hub.
Verifies tool structure, metadata schemas, and naming conventions.
"""
import os
import sys
import json
from pathlib import Path

REQUIRED_METADATA_FIELDS = [
    "name",
    "display_name",
    "description",
    "category",
    "language",
    "mcp_compatible",
    "parameters"
]

def validate_tool_dir(tool_path: Path) -> list[str]:
    errors = []
    tool_name = tool_path.name
    
    if tool_name.startswith(("_", ".")):
        return [] # skip templates/hidden dirs
        
    metadata_file = tool_path / "metadata.json"
    readme_file = tool_path / "README.md"
    
    if not metadata_file.exists():
        errors.append(f"[{tool_name}] Missing metadata.json")
    else:
        try:
            with open(metadata_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                
            for field in REQUIRED_METADATA_FIELDS:
                if field not in data:
                    errors.append(f"[{tool_name}] metadata.json missing required field: '{field}'")
                    
            if data.get("name") != tool_name:
                errors.append(f"[{tool_name}] 'name' in metadata.json ('{data.get('name')}') must match folder name ('{tool_name}')")
                
        except json.JSONDecodeError as e:
            errors.append(f"[{tool_name}] Invalid JSON in metadata.json: {str(e)}")

    if not readme_file.exists():
        errors.append(f"[{tool_name}] Missing README.md")

    # Check that at least one code file exists
    code_files = list(tool_path.glob("tool.*")) + list(tool_path.glob("index.*")) + list(tool_path.glob("main.*"))
    if not code_files:
        errors.append(f"[{tool_name}] Missing implementation file (tool.py / index.ts / main.go)")

    return errors

def main():
    root_dir = Path(__file__).parent.parent
    tools_dir = root_dir / "tools"
    
    if not tools_dir.exists():
        print("❌ 'tools' directory not found!")
        sys.exit(1)
        
    total_tools = 0
    all_errors = []
    
    for item in sorted(tools_dir.iterdir()):
        if item.is_dir() and not item.name.startswith(("_", ".")):
            total_tools += 1
            errs = validate_tool_dir(item)
            all_errors.extend(errs)
            
    print(f"🔍 Validated {total_tools} tool(s)...")
    if all_errors:
        print("\n❌ Validation Failed with errors:")
        for err in all_errors:
            print(f"  - {err}")
        sys.exit(1)
    else:
        print("✅ All tools passed validation successfully!")
        sys.exit(0)

if __name__ == "__main__":
    main()
