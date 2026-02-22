# linux-enum
Automated Linux enumeration tool for penetration testing and OSCP preparation

## Installation

```bash
# Make install script executable
chmod +x install.sh

# Run installer (checks and installs all dependencies)
./install.sh

# Make main script executable
chmod +x linux-enum.py
```

## Required Tools

The install script will check and install these automatically:

| Tool | Purpose |
|------|---------|
| nmap | Port scanning |
| gobuster | Directory brute forcing |
| dirsearch | Directory brute forcing |
| ffuf | Fast web fuzzing |
| nikto | Web vulnerability scanning |
| smbclient | SMB enumeration |
| enum4linux-ng | SMB/RPC enumeration |
| smbmap | SMB share mapping |
| showmount | NFS enumeration |
| snmpwalk | SNMP enumeration |
| snmp-check | SNMP enumeration |

## Usage

### Basic Usage
```bash
python3 linux-enum.py 192.168.1.100
```

### Quick Scan (Skip Full Port Scan)
```bash
python3 linux-enum.py 192.168.1.100 --quick
```

### Skip Nikto (Faster)
```bash
python3 linux-enum.py 192.168.1.100 --skip-nikto
```

### Skip Web Enumeration
```bash
python3 linux-enum.py 192.168.1.100 --skip-web
```

### Custom Output Directory
```bash
python3 linux-enum.py 192.168.1.100 -o ./my-target
```

## Output Structure

```bash
target-ip/
├── nmap/
│   ├── quick.txt       # Top ports scan
│   ├── full.txt        # All ports scan
│   └── udp.txt         # UDP top 20
├── web/
│   ├── headers_80.txt  # HTTP headers
│   ├── robots_80.txt   # robots.txt
│   ├── gobuster_80.txt # Gobuster results
│   ├── dirsearch_80.txt # Dirsearch results
│   ├── ffuf_80.json    # Ffuf results
│   └── nikto_80.txt    # Nikto scan
├── smb/
│   ├── shares.txt      # SMB shares
│   ├── enum4linux.*    # enum4linux-ng output
│   └── smbmap.txt      # smbmap output
├── nfs/
│   └── showmount.txt   # NFS exports
├── snmp/
│   ├── snmpwalk_public.txt
│   └── snmp-check.txt
├── ftp/
│   ├── anonymous.txt   # Anonymous access check
│   └── nmap_ftp.txt    # FTP scripts
├── rpc/
│   └── rpcinfo.txt     # RPC services
└── notes.md            # Summary of findings
```

## What It Does

### Port Scanning
- Quick scan (top ports with version detection)
- Full TCP port scan
- UDP top 20 ports

### Web Enumeration (if ports 80, 443, 8080, etc. open)
- Grab HTTP headers
- Check robots.txt and sitemap.xml
- Gobuster directory brute force
- Dirsearch directory brute force
- Ffuf fuzzing
- Nikto vulnerability scan

### SMB Enumeration (if ports 139/445 open)
- List shares with null session
- enum4linux-ng full enumeration
- smbmap share permissions

### NFS Enumeration (if port 2049 open)
- showmount exports
- rpcinfo services

### SNMP Enumeration (if port 161/udp open)
- snmpwalk with common community strings
- snmp-check enumeration

### FTP Enumeration (if port 21 open)
- Anonymous login check
- Nmap FTP scripts

### SMTP Enumeration (if port 25 open)
- User enumeration
- Nmap SMTP scripts

## Example Workflow

```bash
# 1. Run enumeration
python3 linux-enum.py 192.168.235.71

# 2. Check summary
cat 192.168.235.71/notes.md

# 3. Review web directories
cat 192.168.235.71/web/gobuster_80.txt

# 4. Check SMB shares
cat 192.168.235.71/smb/shares.txt

# 5. Look for NFS exports
cat 192.168.235.71/nfs/showmount.txt
```

## Tips

- Always review the `notes.md` summary first
- Check nmap output for exact service versions
- Look for outdated software versions to exploit
- Check web directories for sensitive files
- SMB null sessions can leak valuable info
- NFS exports may be mountable
- SNMP can reveal system information

## Adding to PATH

```bash
# Option 1: Symlink
sudo ln -s $(pwd)/linux-enum.py /usr/local/bin/linux-enum

# Option 2: Copy
sudo cp linux-enum.py /usr/local/bin/linux-enum

# Then use from anywhere
linux-enum 192.168.1.100
```
