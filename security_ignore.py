import os
import argparse
import sys
from pathlib import Path

# --- Configuration ---
# List of sensitive filenames and extensions to check for.
SENSITIVE_PATTERNS = [
    # Filenames
    'credentials.json',
    'service_account.json',
    '.env',
    'config.py',

    # Extensions
    '*.pem',
    '*.key',
    '*.p12',
    '*.pfx',

    # Common secret-containing files
    'secrets.yml',
    'secrets.json',
    'settings.local.py'
]

# --- Colors for output ---
class Colors:
    YELLOW = '\033[93m'
    GREEN = '\033[92m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    ENDC = '\033[0m'

def read_gitignore(path):
    """Reads the .gitignore file and returns a set of patterns."""
    gitignore_path = Path(path) / '.gitignore'
    if not gitignore_path.is_file():
        return set()
    with open(gitignore_path, 'r', encoding='utf-8') as f:
        # Ignore comments and empty lines
        return {line.strip() for line in f if line.strip() and not line.strip().startswith('#')}

def is_ignored(file_path, gitignore_patterns):
    """
    A simple check to see if a file path matches any gitignore pattern.
    Note: This is a simplified implementation and does not handle all gitignore syntax.
    """
    file_path = Path(file_path)
    for pattern in gitignore_patterns:
        # Simple glob matching
        if file_path.match(pattern):
            return True
        # Check for directory ignores
        if pattern.endswith('/') and str(file_path).startswith(pattern.rstrip('/')):
            return True
    return False

def scan_directory(directory_path):
    """Scans the directory for sensitive files not in .gitignore."""
    print(f"{Colors.BLUE}[*] Starting scan in: {directory_path}{Colors.ENDC}")

    gitignore_patterns = read_gitignore(directory_path)
    print(f"[*] Loaded {len(gitignore_patterns)} patterns from .gitignore")

    found_issues = []

    for root, _, files in os.walk(directory_path):
        # Skip .git directory
        if '.git' in root:
            continue

        for file in files:
            file_path = Path(root) / file

            # Check if the file itself or its extension is in our sensitive list
            is_sensitive = False
            for pattern in SENSITIVE_PATTERNS:
                if file_path.match(pattern):
                    is_sensitive = True
                    break

            if is_sensitive:
                # Now check if this sensitive file is actually ignored
                if not is_ignored(file_path.relative_to(directory_path), gitignore_patterns):
                    found_issues.append(file_path)

    if not found_issues:
        print(f"\n{Colors.GREEN}[+] Scan complete. No un-ignored sensitive files found.{Colors.ENDC}")
    else:
        print(f"\n{Colors.YELLOW}[!] Scan complete. Found {len(found_issues)} potential issues:{Colors.ENDC}")
        for issue_path in found_issues:
            print(f"  - {Colors.RED}WARNING:{Colors.ENDC} Sensitive file found but not in .gitignore: {issue_path}")

        # Offer to fix the issues
        auto_add = input(f"\n{Colors.BLUE}[?] Do you want to automatically add these files to .gitignore? (y/n): {Colors.ENDC}").lower()
        if auto_add == 'y':
            with open(Path(directory_path) / '.gitignore', 'a', encoding='utf-8') as f:
                f.write('\n\n# Added by security_ignore.py\n')
                for issue_path in found_issues:
                    f.write(f"{issue_path.relative_to(directory_path)}\n")
            print(f"{Colors.GREEN}[+] .gitignore has been updated.{Colors.ENDC}")
        else:
            print(f"{Colors.YELLOW}[*] No changes made. Please update .gitignore manually.{Colors.ENDC}")


def main():
    parser = argparse.ArgumentParser(
        description="Scans a project directory for sensitive files that are not listed in .gitignore.",
    )
    parser.add_argument("directory", nargs='?', default='.', help="The project directory to scan (defaults to current directory).")
    args = parser.parse_args()

    if not os.path.isdir(args.directory):
        print(f"{Colors.RED}[-] Error: Directory not found at '{args.directory}'{Colors.ENDC}")
        sys.exit(1)

    scan_directory(args.directory)

if __name__ == "__main__":
    main()