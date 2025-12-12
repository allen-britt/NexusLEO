"""Doctrine surface enforcement tests."""
from __future__ import annotations

from pathlib import Path

from fastapi.routing import APIRoute

from app.main import app

FORBIDDEN_ROUTE_SUBSTRINGS = [
    "/recommend",
    "/actions",
    "/rank",
    "/probable",
    "/risk",
    "/predict",
    "/next_steps",
]

FORBIDDEN_CODE_TOKENS = [
    "recommend",
    "rank_suspects",
    "risk_score",
    "probable_cause",
    "predict",
    "next steps",
]


def test_required_routes_exist() -> None:
    required = [
        ("POST", "/cases"),
        ("POST", "/cases/{case_id}/documents"),
        ("POST", "/cases/{case_id}/ingest"),
        ("GET", "/cases/{case_id}/claims"),
    ]

    for method, path in required:
        assert any(
            isinstance(route, APIRoute) and route.path == path and method in route.methods
            for route in app.routes
        ), f"Missing required route {method} {path}"


def test_docs_endpoints_accessible(client) -> None:
    for path in ("/docs", "/redoc", "/openapi.json"):
        response = client.get(path)
        assert response.status_code == 200, f"{path} did not respond with 200"


def test_no_forbidden_route_paths() -> None:
    violations: list[str] = []
    for route in app.routes:
        if not isinstance(route, APIRoute):
            continue
        lower_path = route.path.lower()
        for fragment in FORBIDDEN_ROUTE_SUBSTRINGS:
            if fragment in lower_path:
                violations.append(f"{route.path} contains forbidden fragment '{fragment}'")
    assert not violations, "Forbidden route fragments detected:\n" + "\n".join(violations)


def test_runtime_code_has_no_forbidden_tokens() -> None:
    backend_root = Path(__file__).resolve().parents[1]
    targets = [
        backend_root / "app" / "services",
        backend_root / "app" / "api" / "routes",
    ]

    hits: list[str] = []
    for directory in targets:
        for file_path in directory.rglob("*.py"):
            contents = file_path.read_text(encoding="utf-8").splitlines()
            for line_no, line in enumerate(contents, start=1):
                lower_line = line.lower()
                for token in FORBIDDEN_CODE_TOKENS:
                    if token in lower_line:
                        relative_path = file_path.relative_to(backend_root)
                        hits.append(f"{relative_path}:{line_no} contains '{token}'")
    assert not hits, "Forbidden doctrine tokens detected:\n" + "\n".join(hits)
