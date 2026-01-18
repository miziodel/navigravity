
import sys
import os
from pathlib import Path

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '../src'))

try:
    from navidrome_mcp_server import mcp
    print("Successfully imported mcp object.")
except ImportError as e:
    print(f"Failed to import mcp: {e}")
    sys.exit(1)



import asyncio
from typing import Any

def verify_registration():
    print("Verifying MCP Registration (Inspection Mode)...")
    
    # 1. Tools
    print("\n--- Checking Tools ---")
    if hasattr(mcp, "_tool_manager") and hasattr(mcp._tool_manager, "_tools"):
        tools = mcp._tool_manager._tools
        print(f"Found {len(tools)} tools.")
        if "check_connection" in tools:
            print("✅ Tool 'check_connection' FOUND.")
        else:
            print("❌ Tool 'check_connection' MISSING.")
        # Optional: List all
        # print(list(tools.keys()))
    else:
        print("⚠️  Cannot inspect _tool_manager._tools")

    # 2. Resources
    print("\n--- Checking Resources ---")
    # Resources are bit trickier as they can be templates.
    # Check _resource_manager attributes
    if hasattr(mcp, "_resource_manager"):
        rm = mcp._resource_manager
        # Usually it has _resources or _templates
        # Let's inspect what it has
        if hasattr(rm, "_resources"):
             # It might be a list of patterns or dict
             resources = rm._resources
             found = False
             target = "navidrome://info"
             
             # If it's a dict
             if isinstance(resources, dict):
                 if target in resources: found = True
             # If it's a list (patterns)
             elif isinstance(resources, list):
                 # Resources wrappers might be objects with .uri property or just strings
                 for r in resources:
                     # Check if r is an object with uri or path
                     if hasattr(r, "uri") and r.uri == target: found = True
                     elif hasattr(r, "path") and r.path == target: found = True
                     elif str(r) == target: found = True
             
             if found:
                 print(f"✅ Resource '{target}' FOUND.")
             else:
                 print(f"❌ Resource '{target}' MISSING in {resources}")
        else:
             print(f"⚠️  _resource_manager has no _resources. Dir: {dir(rm)}")
    else:
        print("⚠️  Cannot inspect _resource_manager")

    # 3. Prompts
    print("\n--- Checking Prompts ---")
    if hasattr(mcp, "_prompt_manager") and hasattr(mcp._prompt_manager, "_prompts"):
        prompts = mcp._prompt_manager._prompts
        print(f"Found {len(prompts)} prompts.")
        target = "usage_guide"
        if target in prompts:
            print(f"✅ Prompt '{target}' FOUND.")
        else:
            print(f"❌ Prompt '{target}' MISSING. Available: {list(prompts.keys())}")
    else:
        print("⚠️  Cannot inspect _prompt_manager._prompts")



if __name__ == "__main__":
    verify_registration()
