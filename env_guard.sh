#!/bin/bash

# --- env_guard.sh ---
# A simple script to scan a .env file for potentially hardcoded secrets.

# --- Colors for output ---
COLOR_RED='\033[0;31m'
COLOR_YELLOW='\033[1;33m'
COLOR_GREEN='\033[0;32m'
COLOR_BLUE='\033[0;34m'
NC='\033[0m' # No Color

# --- Configuration ---
ENV_FILE=".env"
# Regex to find common secret patterns with non-empty values.
# It looks for lines that start with specific keywords followed by an '=' and at least one character.
SECRET_PATTERN='^(API_KEY|.*_TOKEN|.*_SECRET|PASSWORD|PRIVATE_KEY)=.+'

echo -e "${COLOR_BLUE}[*] Starting .env security scan...${NC}"

# Check if the .env file exists
if [ ! -f "$ENV_FILE" ]; then
    echo -e "${COLOR_GREEN}[+] .env file not found. Nothing to scan.${NC}"
    exit 0
fi

echo -e "[*] Scanning file: ${ENV_FILE}"

# Use grep to find matches
# -E: Use extended regular expressions
# -i: Case-insensitive search
# --color=never: Disable color output from grep itself
matches=$(grep -E -i --color=never "$SECRET_PATTERN" "$ENV_FILE")

if [ -n "$matches" ]; then
    echo -e "\n${COLOR_RED}[!] WARNING: Found potential hardcoded secrets in your .env file!${NC}"
    echo -e "${COLOR_YELLOW}The following lines may contain sensitive information that should be managed securely (e.g., using a secrets manager or encrypted files):${NC}"

    # Print each matched line with a prefix
    while IFS= read -r line; do
        echo -e "  - ${line}"
    done <<< "$matches"

    echo -e "\n${COLOR_YELLOW}[*] Recommendation: For production, use a service like AWS Secrets Manager, HashiCorp Vault, or environment variables provided by your hosting platform.${NC}"
    exit 1
else
    echo -e "\n${COLOR_GREEN}[+] Scan complete. No obvious hardcoded secrets found based on common patterns.${NC}"
    exit 0
fi