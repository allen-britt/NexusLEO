"""Utility script to exercise the /analysis/run endpoint for debugging."""

import json
import sys
import urllib.error
import urllib.request

PAYLOAD = {
    "mission_id": 1,
    "document_ids": [1, 2, 3, 4],
    "profile": "humint",
}

URL = "http://localhost:8000/analysis/run"
HEADERS = {"Content-Type": "application/json"}


def main() -> int:
    data = json.dumps(PAYLOAD).encode("utf-8")
    req = urllib.request.Request(URL, data=data, headers=HEADERS)
    try:
        with urllib.request.urlopen(req) as resp:
            body = resp.read().decode("utf-8")
            print("STATUS", resp.status)
            print(body)
            return 0
    except urllib.error.HTTPError as exc:  # noqa: PERF203 - simple script
        print("STATUS", exc.code)
        print(exc.read().decode("utf-8"))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
