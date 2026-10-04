#!/usr/bin/env python3
# EP02 launcher shim for markitdown-mcp under `grok --sandbox strict` (CTO 10-03 18:25).
# Why: strict seccomp blocks writes on the asyncio self-pipe socket; asyncio swallows that OSError in
# _write_to_self, so cross-thread wakeups are lost and the stdio server never answers the MCP handshake
# (diagnosed 10-03 18:24, faulthandler dump in selftest/B-smoke-4/mcp.stderr). This shim only caps each
# selector wait at 50 ms so queued callbacks still run. It does not change markitdown or markitdown-mcp code.
# usage (inside the run dir venv): .venv/bin/python tools/mcp_launch_shim.py   (copied as .venv/bin/mdmcp_shim.py)
import asyncio, selectors, sys
class _CappedSelector(selectors.DefaultSelector):
    def select(self, timeout=None):
        if timeout is None or timeout > 0.05: timeout = 0.05
        return super().select(timeout)
class _Policy(asyncio.DefaultEventLoopPolicy):
    def new_event_loop(self):
        return asyncio.SelectorEventLoop(_CappedSelector())
asyncio.set_event_loop_policy(_Policy())
from markitdown_mcp.__main__ import main
sys.argv = ["markitdown-mcp"]
main()
