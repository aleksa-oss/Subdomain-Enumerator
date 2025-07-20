# Simple Subdomain Enumerator

A straightforward Python script to find subdomains for any domain using DNS queries.

---

## What It Does

This tool takes a domain name and tries a list of common subdomain names (like `www`, `mail`, `api`, etc.) to see which ones actually exist. It does this by asking DNS servers if these subdomains have IP addresses.

---

## How It Works

- Loads a list of potential subdomains from a wordlist file.
- Uses multiple threads to speed up DNS queries.
- Prints out every subdomain that resolves successfully.
- Shows some basic stats at the end, like how many subdomains it checked and how many were found.

---

## Requirements

- Python 3
- `dnspython` library
- `colorama` library (for colorful output)

You can install the dependencies with:

```bash
pip install dnspython colorama
