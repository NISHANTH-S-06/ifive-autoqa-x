"""
Fail-closed compatibility wrapper.

This script previously created persistent VIEWER/TESTER/APPROVER operators
with hard-coded passwords and printed a full plaintext credential table to
stdout. That behaviour violated project rules 8, 9, and 10 (no default
credentials, no automatic account creation with known credentials, never
display passwords) and has been permanently removed as a P0 security fix.

This script performs NO database connection, NO schema migration, NO
operator creation, and prints NO credential material of any kind. It does
not touch the configured persistent database in any way.

Video demonstrations and automated UI validation use the existing Playwright
mocked-auth fixture instead, which fabricates an in-memory ADMIN identity
for the browser session only and never creates, stores, or displays a real
password or a real database row:

    qa/fixtures/authenticated.fixture.ts

For an interactive, human-recorded demo that needs a real logged-in
operator, an authorized person must create operators one at a time with
private, off-screen password entry:

    scripts\\create_local_operator.ps1
"""
import sys


def main() -> int:
    print("=" * 60)
    print("iFive AutoQA Demo Setup")
    print("=" * 60)
    print("This script no longer creates operators or touches the database.")
    print("Hard-coded demo credentials and credential printing have been removed.")
    print()
    print("For scripted/automated demo validation, use the Playwright mocked-auth")
    print("fixture, which never creates a real operator or a real password:")
    print("    qa/fixtures/authenticated.fixture.ts")
    print()
    print("For an interactive human-recorded demo, create each operator privately:")
    print("    scripts\\create_local_operator.ps1")
    print()
    print("No account in this project is created with a known or default password.")
    return 1


if __name__ == "__main__":
    sys.exit(main())