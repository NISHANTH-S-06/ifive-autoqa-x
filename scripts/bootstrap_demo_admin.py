"""
Fail-closed compatibility wrapper.

This script previously created a hard-coded ADMIN operator and printed its
plaintext password to stdout. That behaviour violated project rules 8, 9,
and 10 (no default credentials, no automatic persistent ADMIN, never
display passwords) and has been permanently removed as a P0 security fix.

This script performs NO database connection, NO schema migration, NO
operator creation, and prints NO credential material of any kind. It exists
only to redirect anyone who runs it to the authorized, interactive bootstrap
path.
"""
import sys


def main() -> int:
    print("=== iFive AutoQA Operator Bootstrap ===")
    print("This script no longer creates an operator or touches the database.")
    print("Hard-coded demo credentials and credential printing have been removed.")
    print()
    print("To create the first ADMIN operator, an authorized person must run the")
    print("interactive bootstrap script and enter a username, display name, and")
    print("password privately at the prompts. No default or example password is")
    print("provided by this project.")
    print()
    print("    scripts\\create_local_operator.ps1")
    print()
    print("Run it from the project root in PowerShell. The operator must change")
    print("the password at first login. Persistent ADMIN creation is intentionally")
    print("a manual, private action and is never automated by this project.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
