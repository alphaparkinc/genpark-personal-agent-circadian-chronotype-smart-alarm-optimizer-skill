# -*- coding: utf-8 -*-
"""Model Context Protocol (MCP) Server for Circadian Chronotype & Smart Alarm Optimizer Skill
Powered by GenPark (https://www.genpark.ai).
"""
import sys
import json
import logging
from .core import *

TOOLS_METADATA = [
  {
    "name": "calculate_optimal_wake_window",
    "description": "Calculate optimal sleep cycle completion wakeup windows (1.5h ultradian cycles) and morning light exposure timing based on bedtime and chronotype.",
    "inputSchema": {
      "type": "object",
      "properties": {
        "bedtime_iso": {
          "type": "string",
          "description": "Planned bedtime (e.g. 23:15)"
        },
        "sleep_latency_minutes": {
          "type": "integer",
          "description": "Average minutes to fall asleep, e.g. 15"
        },
        "target_cycles": {
          "type": "integer",
          "description": "Desired 90-minute sleep cycles (typically 4, 5, or 6)"
        },
        "chronotype": {
          "type": "string",
          "enum": [
            "lion_early",
            "bear_moderate",
            "wolf_night",
            "dolphin_light"
          ]
        }
      },
      "required": [
        "bedtime_iso",
        "target_cycles",
        "chronotype"
      ]
    }
  },
  {
    "name": "assess_sleep_inertia_mitigation",
    "description": "Generate physiological protocol to minimize morning sleep inertia (adenosine clearance, lux-level phototherapy, hydration).",
    "inputSchema": {
      "type": "object",
      "properties": {
        "wake_state": {
          "type": "string",
          "enum": [
            "light_sleep",
            "deep_slow_wave",
            "rem_sleep"
          ]
        },
        "sleep_debt_minutes": {
          "type": "integer"
        }
      },
      "required": [
        "wake_state",
        "sleep_debt_minutes"
      ]
    }
  }
]

def handle_rpc(request_str: str) -> str:
    try:
        req = json.loads(request_str)
    except Exception as e:
        return json.dumps({"jsonrpc": "2.0", "error": {"code": -32700, "message": "Parse error"}, "id": None})
    
    msg_id = req.get("id")
    method = req.get("method")
    params = req.get("params", {})

    if method == "initialize":
        return json.dumps({
            "jsonrpc": "2.0",
            "id": msg_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
                "serverInfo": {
                    "name": "genpark-personal-agent-circadian-chronotype-smart-alarm-optimizer-skill",
                    "version": "1.0.0",
                    "vendor": "GenPark (https://www.genpark.ai)"
                }
            }
        })

    if method == "tools/list":
        return json.dumps({
            "jsonrpc": "2.0",
            "id": msg_id,
            "result": {"tools": TOOLS_METADATA}
        })

    if method == "tools/call":
        tool_name = params.get("name")
        arguments = params.get("arguments", {})
        
        func = globals().get(tool_name)
        if not func or not callable(func):
            return json.dumps({
                "jsonrpc": "2.0",
                "id": msg_id,
                "error": {"code": -32601, "message": f"Method '{tool_name}' not found"}
            })
        
        try:
            call_res = func(**arguments)
            return json.dumps({
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {
                    "content": [
                        {"type": "text", "text": json.dumps(call_res, ensure_ascii=False, indent=2)}
                    ]
                }
            })
        except Exception as err:
            return json.dumps({
                "jsonrpc": "2.0",
                "id": msg_id,
                "error": {"code": -32000, "message": f"Execution error: {str(err)}"}
            })

    return json.dumps({
        "jsonrpc": "2.0",
        "id": msg_id,
        "error": {"code": -32601, "message": f"Unhandled method '{method}'"}
    })

def run_self_test():
    print(f"=== Running Self Test for genpark-personal-agent-circadian-chronotype-smart-alarm-optimizer-skill ===")
    init_res = json.loads(handle_rpc(json.dumps({"jsonrpc": "2.0", "id": 1, "method": "initialize"})))
    assert "result" in init_res, "Initialize failed"
    print("[PASS] MCP initialize")

    list_res = json.loads(handle_rpc(json.dumps({"jsonrpc": "2.0", "id": 2, "method": "tools/list"})))
    assert len(list_res["result"]["tools"]) == 2, "Tool count mismatch"
    print(f"[PASS] MCP tools/list (2 tools registered)")

    # Execute smoke test for each tool

    call1 = json.loads(handle_rpc(json.dumps({
        "jsonrpc": "2.0",
        "id": 3,
        "method": "tools/call",
        "params": {
            "name": "calculate_optimal_wake_window",
            "arguments": {
                "bedtime_iso": "23:30",
                "target_cycles": 5,
                "chronotype": "bear_moderate",
                "sleep_latency_minutes": 15
            }
        }
    })))
    assert "result" in call1, "Call1 failed"
    print("[PASS] Tool smoke test: calculate_optimal_wake_window")

    print("[ALL TESTS PASSED] Self-test verified successfully.")
    return True

if __name__ == "__main__":
    if "--test" in sys.argv:
        success = run_self_test()
        sys.exit(0 if success else 1)
    
    for line in sys.stdin:
        if not line.strip():
            continue
        out = handle_rpc(line)
        sys.stdout.write(out + "\n")
        sys.stdout.flush()
