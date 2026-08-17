#!/usr/bin/env python3
"""
Generates the tool catalog table in README.md and outputs registry.json.
"""
import os
import json
from pathlib import Path

def generate():
    root_dir = Path(__file__).parent.parent
    tools_dir = root_dir / "tools"
    readme_path = root_dir / "README.md"
    registry_path = root_dir / "registry.json"
    
    tools = []
    
    for item in sorted(tools_dir.iterdir()):
        if item.is_dir() and not item.name.startswith(("_", ".")):
            meta_file = item / "metadata.json"
            if meta_file.exists():
                try:
                    with open(meta_file, "r", encoding="utf-8") as f:
                        meta = json.load(f)
                        tools.append(meta)
                except Exception as e:
                    print(f"Error reading {meta_file}: {e}")

    # Write registry.json
    with open(registry_path, "w", encoding="utf-8") as f:
        json.dump({"total_tools": len(tools), "tools": tools}, f, indent=2)
    print(f"✅ Generated {registry_path} with {len(tools)} tools.")

if __name__ == "__main__":
    generate()
