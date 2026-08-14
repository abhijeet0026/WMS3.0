#!/usr/bin/env python3
"""
GenAI Chatbot CLI Launcher
--------------------------
Shortcut launcher for the GenAI chatbot component.
Runs the root model CLI pre-configured with the Thanos or Hospital persona.
"""

import sys
from pathlib import Path

# Add root directory to sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from cli import main

if __name__ == "__main__":
    # Default to Thanos persona if no persona specified
    if "-p" not in sys.argv and "--persona" not in sys.argv:
        sys.argv.extend(["-p", "thanos"])
    main()
