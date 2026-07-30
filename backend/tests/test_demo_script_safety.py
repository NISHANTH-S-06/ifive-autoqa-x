"""
P0 security regression test.

Confirms scripts/bootstrap_demo_admin.py and scripts/setup_demo_accounts.py:
  1. contain no hard-coded demo password or credential literal,
  2. never import the database engine/session or an Operator model
     (so they structurally cannot create a persistent operator),
  3. print no credential-shaped material when executed,
  4. leave the configured persistent database file completely untouched.

These two scripts previously created real operators with hard-coded
passwords and printed those passwords to stdout. That behaviour has been
removed as a P0 fix; this test locks the fix in place.
"""
import importlib.util
import io
import re
import sqlite3
from contextlib import redirect_stdout
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SCRIPTS_DIR = PROJECT_ROOT / "scripts"

TARGET_SCRIPTS = [
    SCRIPTS_DIR / "bootstrap_demo_admin.py",
    SCRIPTS_DIR / "setup_demo_accounts.py",
]

FORBIDDEN_LITERALS = [
    "Secure@Work2024",
    "ViewOnly#2025",
    "Testing#Work25",
    "Approve#Work25",
    "demoadmin",
    "demo.viewer",
    "demo.tester",
    "demo.approver",
]

# Matches an actual variable ASSIGNMENT such as PASSWORD = "Something123!" or
# password: str = "Something123!". Deliberately does NOT match plain prose
# like "...never display a real password: it is never stored." because that
# is documentation, not a credential leak.
PASSWORD_LITERAL_PATTERN = re.compile(
    r'(?im)^[ \t]*\w*password\w*[ \t]*(:[ \t]*\w+[ \t]*)?=[ \t]*("[^"]{6,}"|\'[^\']{6,}\')'
)

FORBIDDEN_IMPORT_TOKENS = [
    "SessionLocal",
    "app.database",
    "app.models.operator",
    "Operator(",
    "engine",
    "hash_password",
]


@pytest.mark.parametrize("script_path", TARGET_SCRIPTS, ids=lambda p: p.name)
def test_no_hardcoded_password_literal(script_path):
    assert script_path.exists(), f"expected fail-closed wrapper at {script_path}"
    source = script_path.read_text(encoding="utf-8")

    for literal in FORBIDDEN_LITERALS:
        assert literal not in source, f"{script_path.name} still contains forbidden literal {literal!r}"

    assert not PASSWORD_LITERAL_PATTERN.search(source), (
        f"{script_path.name} appears to assign a password-shaped string literal"
    )


@pytest.mark.parametrize("script_path", TARGET_SCRIPTS, ids=lambda p: p.name)
def test_script_cannot_touch_database(script_path):
    source = script_path.read_text(encoding="utf-8")
    for token in FORBIDDEN_IMPORT_TOKENS:
        assert token not in source, (
            f"{script_path.name} references {token!r}; it must not be able to reach the database "
            "or construct an Operator record"
        )


def _load_and_run(script_path: Path):
    spec = importlib.util.spec_from_file_location(script_path.stem, script_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    buffer = io.StringIO()
    with redirect_stdout(buffer):
        exit_code = module.main()
    return exit_code, buffer.getvalue()


@pytest.mark.parametrize("script_path", TARGET_SCRIPTS, ids=lambda p: p.name)
def test_script_fails_closed_and_prints_no_credentials(script_path):
    exit_code, output = _load_and_run(script_path)

    assert exit_code != 0
    lowered = output.lower()
    for banned in ["created successfully", "login credentials:"]:
        assert banned not in lowered, f"{script_path.name} printed credential-shaped output: {banned!r}"

    for literal in FORBIDDEN_LITERALS:
        assert literal not in output

    assert not PASSWORD_LITERAL_PATTERN.search(output)


@pytest.mark.parametrize("script_path", TARGET_SCRIPTS, ids=lambda p: p.name)
def test_script_does_not_modify_persistent_database(script_path, tmp_path, monkeypatch):
    db_path = PROJECT_ROOT / "backend" / "data" / "autoqa.db"
    if not db_path.exists():
        pytest.skip("no persistent database present in this environment")

    before = sqlite3.connect(str(db_path))
    before_count = before.execute("SELECT COUNT(*) FROM operators").fetchone()[0]
    before.close()

    monkeypatch.chdir(tmp_path)
    _load_and_run(script_path)

    after = sqlite3.connect(str(db_path))
    after_count = after.execute("SELECT COUNT(*) FROM operators").fetchone()[0]
    after.close()

    assert after_count == before_count, f"{script_path.name} changed the persistent operator count"