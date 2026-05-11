from pathlib import Path
import sys

from mcp.server.fastmcp import FastMCP

SRC_ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = Path(__file__).resolve().parents[2]
for path in (SRC_ROOT, PROJECT_ROOT):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from financial_mcp.tools import register_tools


mcp = FastMCP("financial-analytics")
register_tools(mcp)


if __name__ == "__main__":
    mcp.run()
