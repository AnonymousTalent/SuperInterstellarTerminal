import os
import argparse
import sys
from pathlib import Path

# --- Configuration ---
SENSITIVE_PATTERNS = [
    'credentials.json', 'service_account.json', '.env',
    '*.pem', '*.key', '*.p12', '*.pfx',
    'secrets.yml', 'secrets.json', 'settings.local.py'
]

# --- Colors for output ---
class Colors:
    YELLOW = '\033[93m'
    GREEN = '\033[92m'
    RED = '\033[91m'
    BLUE = '\033[0;34m'
    ENDC = '\033[0m'

def read_gitignore(root_path):
    """Reads the .gitignore file from the project root."""
    gitignore_path = root_path / '.gitignore'
    if not gitignore_path.is_file():
        return set()
    with open(gitignore_path, 'r', encoding='utf-8') as f:
        return {line.strip() for line in f if line.strip() and not line.strip().startswith('#')}

def is_ignored(file_path, gitignore_patterns, root_path):
    """A simple check to see if a file path matches any gitignore pattern."""
    relative_path = file_path.relative_to(root_path)
    for pattern in gitignore_patterns:
        if relative_path.match(pattern):
            return True
        if pattern.endswith('/') and str(relative_path).startswith(pattern.rstrip('/')):
            return True
    return False

def scan_directory(directory_path):
    """Scans the directory for sensitive files not in .gitignore."""
    root_path = Path(directory_path)
    print(f"{Colors.BLUE}[*] Starting scan in: {root_path}{Colors.ENDC}")

    gitignore_patterns = read_gitignore(root_path)
    print(f"[*] Loaded {len(gitignore_patterns)} patterns from .gitignore")

    found_issues = []

    for root, _, files in os.walk(root_path):
        if '.git' in root:
            continue

        for file in files:
            file_path = Path(root) / file

            is_sensitive = any(file_path.match(pattern) for pattern in SENSITIVE_PATTERNS)

            if is_sensitive:
                if not is_ignored(file_path, gitignore_patterns, root_path):
                    found_issues.append(file_path)

    if not found_issues:
        print(f"\n{Colors.GREEN}[+] Scan complete. No un-ignored sensitive files found.{Colors.ENDC}")
    else:
        print(f"\n{Colors.YELLOW}[!] Scan complete. Found {len(found_issues)} potential issues:{Colors.ENDC}")
        for issue_path in found_issues:
            print(f"  - {Colors.RED}WARNING:{Colors.ENDC} Sensitive file found but not in .gitignore: {issue_path}")

        auto_add = input(f"\n{Colors.BLUE}[?] Add these files to .gitignore? (y/n): {Colors.ENDC}").lower()
        if auto_add == 'y':
            with open(root_path / '.gitignore', 'a', encoding='utf-8') as f:
                f.write('\n\n# Added by security_ignore.py\n')
                for issue_path in found_issues:
                    f.write(f"{issue_path.relative_to(root_path)}\n")
            print(f"{Colors.GREEN}[+] .gitignore has been updated.{Colors.ENDC}")
        else:
            print(f"{Colors.YELLOW}[*] No changes made. Please update .gitignore manually.{Colors.ENDC}")

def main():
    parser = argparse.ArgumentParser(description="Scans for sensitive files not listed in .gitignore.")
    parser.add_argument("directory", nargs='?', default='.', help="The project directory to scan (defaults to current directory).")
    args = parser.parse_args()

    if not os.path.isdir(args.directory):
        print(f"{Colors.RED}[-] Error: Directory not found at '{args.directory}'{Colors.ENDC}")
        sys.exit(1)

    scan_directory(args.directory)

if __name__ == "__main__":
    main()