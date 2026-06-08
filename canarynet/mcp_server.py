"""CANARYNET MCP server — exposes scan as an MCP tool for Cognis.Studio."""
from cognis_core.mcp import build_mcp_server
from canarynet.core import scan, TOOL_NAME

run_mcp_server = build_mcp_server(
    tool_name=TOOL_NAME,
    description="Self-hosted canary token network — AWS keys, DNS, docs, web URLs",
    scan_fn=scan,
)

if __name__ == "__main__":
    run_mcp_server()
