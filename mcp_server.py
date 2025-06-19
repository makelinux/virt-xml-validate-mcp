#!/usr/bin/env python3

import os
import tempfile
import subprocess

from fastmcp import FastMCP

mcp = FastMCP("virt-xml-validate")


@mcp.tool()
def virt_xml_validate(session_id, xml_string: str) -> dict:
    """
    Validates a libvirt XML string using virt-xml-validate.
    Returns the result of the validation.
    """
    result = subprocess.run(
        ["virt-xml-validate", "-"],
        input=xml_string,
        capture_output=True,
        text=True,
        check=False
    )
    return {
        "returncode": result.returncode,
        "stdout": result.stdout,
        "stderr": result.stderr.replace('Relax-NG validity error :', '')
    }


if __name__ == "__main__":
    mcp.run(transport="sse", port=3002)
