#!/usr/bin/env python3
"""
Linux Auto-Enumerator
OSCP Helper Tool
"""

import subprocess
import sys
import os
import argparse
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

# Colors for output
class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def banner():
    print(f"""{Colors.CYAN}
    ╦  ╦╔╗╔╦ ╦═╗ ╦  ╔═╗╔╗╔╦ ╦╔╦╗
    ║  ║║║║║ ║╔╩╦╝  ║╣ ║║║║ ║║║║
    ╩═╝╩╝╚╝╚═╝╩ ╚═  ╚═╝╝╚╝╚═╝╩ ╩
    Linux Auto-Enumerator
    {Colors.RESET}""")

def print_status(msg, status="info"):
    symbols = {
        "info": f"{Colors.BLUE}[*]{Colors.RESET}",
        "success": f"{Colors.GREEN}[+]{Colors.RESET}",
        "error": f"{Colors.RED}[-]{Colors.RESET}",
        "warning": f"{Colors.YELLOW}[!]{Colors.RESET}",
        "running": f"{Colors.PURPLE}[~]{Colors.RESET}"
    }
    print(f"{symbols.get(status, symbols['info'])} {msg}")

def run_command(cmd, output_file=None, timeout=300):
    """Run a command and optionally save output to file"""
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        output = result.stdout + result.stderr
        
        if output_file:
            with open(output_file, 'w') as f:
                f.write(f"Command: {cmd}\n")
                f.write(f"Time: {datetime.now()}\n")
                f.write("="*50 + "\n\n")
                f.write(output)
        
        return output
    except subprocess.TimeoutExpired:
        return f"[!] Command timed out after {timeout} seconds"
    except Exception as e:
        return f"[!] Error: {str(e)}"

def create_directories(base_path):
    """Create output directory structure"""
    dirs = ['nmap', 'web', 'smb', 'nfs', 'snmp', 'ftp', 'rpc']
    for d in dirs:
        os.makedirs(os.path.join(base_path, d), exist_ok=True)
    return base_path

def check_tool(tool):
    """Check if a tool is installed"""
    result = subprocess.run(f"which {tool}", shell=True, capture_output=True)
    return result.returncode == 0

def check_dependencies():
    """Check if required tools are installed"""
    tools = ['nmap', 'gobuster', 'nikto']
    missing = []
    for tool in tools:
        if not check_tool(tool):
            missing.append(tool)
    
    if missing:
        print_status(f"Missing tools: {', '.join(missing)}", "warning")
        print_status("Run install.sh to install dependencies", "info")
    return len(missing) == 0

def check_port_open(target, port):
    """Quick check if a port is open"""
    result = subprocess.run(
        f"nc -zv -w 2 {target} {port}",
        shell=True,
        capture_output=True
    )
    return result.returncode == 0

def parse_nmap_ports(nmap_output):
    """Parse nmap output for open ports"""
    ports = {
        'web': [],
        'smb': False,
        'nfs': False,
        'snmp': False,
        'ftp': False,
        'ssh': False,
        'smtp': False
    }
    
    for line in nmap_output.split('\n'):
        if '/tcp' in line and 'open' in line:
            if '80/' in line or '443/' in line or '8080/' in line or '8443/' in line or '8000/' in line or '8888/' in line:
                port = line.split('/')[0].strip()
                ports['web'].append(port)
            if '445/' in line or '139/' in line:
                ports['smb'] = True
            if '2049/' in line or '111/' in line:
                ports['nfs'] = True
            if '21/' in line:
                ports['ftp'] = True
            if '22/' in line:
                ports['ssh'] = True
            if '25/' in line:
                ports['smtp'] = True
        if '/udp' in line and 'open' in line:
            if '161/' in line:
                ports['snmp'] = True
    
    return ports

# ============== SCAN FUNCTIONS ==============

def nmap_scan(target, output_dir):
    """Run nmap scans"""
    print_status("Running Nmap quick scan...", "running")
    
    # Quick scan
    quick_cmd = f"nmap -sC -sV -oN {output_dir}/nmap/quick.txt {target}"
    quick_output = run_command(quick_cmd, f"{output_dir}/nmap/quick.txt", timeout=300)
    print_status("Quick scan complete", "success")
    
    # Full port scan
    print_status("Running Nmap full port scan...", "running")
    full_cmd = f"nmap -p- -sC -sV -oN {output_dir}/nmap/full.txt {target}"
    run_command(full_cmd, f"{output_dir}/nmap/full.txt", timeout=900)
    print_status("Full scan complete", "success")
    
    # UDP scan (top ports only)
    print_status("Running Nmap UDP scan (top 20)...", "running")
    udp_cmd = f"sudo nmap -sU --top-ports 20 -oN {output_dir}/nmap/udp.txt {target}"
    run_command(udp_cmd, f"{output_dir}/nmap/udp.txt", timeout=300)
    print_status("UDP scan complete", "success")
    
    return quick_output

def web_enum(target, output_dir, ports):
    """Enumerate web services"""
    if not ports:
        print_status("No web ports found", "info")
        return
    
    for port in ports:
        protocol = "https" if port in ['443', '8443'] else "http"
        url = f"{protocol}://{target}:{port}"
        
        print_status(f"Enumerating web on port {port}...", "running")
        
        # Curl - grab headers, robots.txt, sitemap
        print_status(f"Grabbing headers and common files...", "running")
        run_command(f"curl -s -I {url}", f"{output_dir}/web/headers_{port}.txt")
        run_command(f"curl -s {url}/robots.txt", f"{output_dir}/web/robots_{port}.txt")
        run_command(f"curl -s {url}/sitemap.xml", f"{output_dir}/web/sitemap_{port}.txt")
        
        # Gobuster
        if check_tool('gobuster'):
            print_status(f"Running Gobuster on port {port}...", "running")
            gobuster_cmd = f"gobuster dir -u {url} -w /usr/share/wordlists/dirb/common.txt -o {output_dir}/web/gobuster_{port}.txt -t 30 --timeout 20s -q"
            run_command(gobuster_cmd, timeout=300)
            print_status(f"Gobuster on port {port} complete", "success")
        
        # Dirsearch
        if check_tool('dirsearch'):
            print_status(f"Running Dirsearch on port {port}...", "running")
            dirsearch_cmd = f"dirsearch -u {url} -o {output_dir}/web/dirsearch_{port}.txt -q -t 30 -e php,html,txt,asp,aspx,jsp"
            run_command(dirsearch_cmd, timeout=300)
            print_status(f"Dirsearch on port {port} complete", "success")
        
        # Ffuf
        if check_tool('ffuf'):
            print_status(f"Running Ffuf on port {port}...", "running")
            ffuf_cmd = f"ffuf -u {url}/FUZZ -w /usr/share/wordlists/dirb/common.txt -o {output_dir}/web/ffuf_{port}.json -of json -t 30 -mc 200,204,301,302,307,401,403 -s"
            run_command(ffuf_cmd, timeout=300)
            print_status(f"Ffuf on port {port} complete", "success")
        
        # Nikto
        if check_tool('nikto'):
            print_status(f"Running Nikto on port {port} (this takes a while)...", "running")
            nikto_cmd = f"nikto -h {url} -o {output_dir}/web/nikto_{port}.txt -Format txt -timeout 5 -maxtime 300s"
            run_command(nikto_cmd, timeout=360)
            print_status(f"Nikto on port {port} complete", "success")

def smb_enum(target, output_dir):
    """Enumerate SMB shares"""
    print_status("Enumerating SMB...", "running")
    
    # smbclient list shares
    print_status("Listing SMB shares...", "running")
    smb_cmd = f"smbclient -L //{target} -N"
    run_command(smb_cmd, f"{output_dir}/smb/shares.txt")
    
    # enum4linux-ng
    if check_tool('enum4linux-ng'):
        print_status("Running enum4linux-ng...", "running")
        enum_cmd = f"enum4linux-ng -A {target} -oA {output_dir}/smb/enum4linux"
        run_command(enum_cmd, timeout=300)
        print_status("enum4linux-ng complete", "success")
    elif check_tool('enum4linux'):
        print_status("Running enum4linux...", "running")
        enum_cmd = f"enum4linux -a {target} > {output_dir}/smb/enum4linux.txt"
        run_command(enum_cmd, timeout=300)
        print_status("enum4linux complete", "success")
    
    # smbmap
    if check_tool('smbmap'):
        print_status("Running smbmap...", "running")
        smbmap_cmd = f"smbmap -H {target}"
        run_command(smbmap_cmd, f"{output_dir}/smb/smbmap.txt")
        print_status("smbmap complete", "success")
    
    print_status("SMB enumeration complete", "success")

def nfs_enum(target, output_dir):
    """Enumerate NFS shares"""
    print_status("Enumerating NFS...", "running")
    
    # showmount
    showmount_cmd = f"showmount -e {target}"
    output = run_command(showmount_cmd, f"{output_dir}/nfs/showmount.txt")
    
    if "Export list" in output:
        print_status("NFS exports found! Check nfs/showmount.txt", "success")
    else:
        print_status("No NFS exports found", "info")
    
    # rpcinfo
    rpcinfo_cmd = f"rpcinfo -p {target}"
    run_command(rpcinfo_cmd, f"{output_dir}/rpc/rpcinfo.txt")
    
    print_status("NFS enumeration complete", "success")

def snmp_enum(target, output_dir):
    """Enumerate SNMP"""
    print_status("Enumerating SNMP...", "running")
    
    # snmpwalk with common community strings
    communities = ['public', 'private', 'manager']
    
    for community in communities:
        print_status(f"Trying SNMP community string: {community}", "running")
        snmp_cmd = f"snmpwalk -v2c -c {community} {target} > {output_dir}/snmp/snmpwalk_{community}.txt 2>&1"
        output = run_command(snmp_cmd, timeout=60)
        
        # Check if successful
        with open(f"{output_dir}/snmp/snmpwalk_{community}.txt", 'r') as f:
            content = f.read()
            if "Timeout" not in content and len(content) > 100:
                print_status(f"SNMP community '{community}' works!", "success")
    
    # snmp-check
    if check_tool('snmp-check'):
        print_status("Running snmp-check...", "running")
        snmpcheck_cmd = f"snmp-check {target} > {output_dir}/snmp/snmp-check.txt"
        run_command(snmpcheck_cmd, timeout=120)
    
    print_status("SNMP enumeration complete", "success")

def ftp_enum(target, output_dir):
    """Check FTP for anonymous access"""
    print_status("Checking FTP anonymous access...", "running")
    
    # Try anonymous login
    ftp_cmd = f"curl -s ftp://{target}/ --user anonymous:anonymous --connect-timeout 10"
    output = run_command(ftp_cmd, f"{output_dir}/ftp/anonymous.txt", timeout=30)
    
    if "drw" in output or "-rw" in output:
        print_status("FTP anonymous access allowed!", "success")
    else:
        print_status("FTP anonymous access denied", "info")
    
    # Nmap FTP scripts
    nmap_ftp = f"nmap -p 21 --script ftp-anon,ftp-bounce,ftp-syst,ftp-vsftpd-backdoor -oN {output_dir}/ftp/nmap_ftp.txt {target}"
    run_command(nmap_ftp, timeout=60)
    
    print_status("FTP enumeration complete", "success")

def smtp_enum(target, output_dir):
    """Enumerate SMTP"""
    print_status("Enumerating SMTP...", "running")
    
    # smtp-user-enum
    if check_tool('smtp-user-enum'):
        print_status("Running smtp-user-enum...", "running")
        smtp_cmd = f"smtp-user-enum -M VRFY -U /usr/share/seclists/Usernames/Names/names.txt -t {target} > {output_dir}/smtp/users.txt"
        run_command(smtp_cmd, timeout=300)
    
    # Nmap SMTP scripts
    nmap_smtp = f"nmap -p 25 --script smtp-commands,smtp-enum-users,smtp-vuln-cve2010-4344 -oN {output_dir}/smtp/nmap_smtp.txt {target}"
    run_command(nmap_smtp, timeout=120)
    
    print_status("SMTP enumeration complete", "success")

# ============== SUMMARY ==============

def generate_summary(target, output_dir, ports_found):
    """Generate a summary of findings"""
    summary = f"""
# Enumeration Summary
Target: {target}
Time: {datetime.now()}

## Open Services
"""
    
    # Add found services
    if ports_found['web']:
        summary += f"- Web: ports {', '.join(ports_found['web'])}\n"
    if ports_found['smb']:
        summary += "- SMB: ports 139/445\n"
    if ports_found['nfs']:
        summary += "- NFS: port 2049\n"
    if ports_found['ftp']:
        summary += "- FTP: port 21\n"
    if ports_found['ssh']:
        summary += "- SSH: port 22\n"
    if ports_found['snmp']:
        summary += "- SNMP: port 161/udp\n"
    if ports_found['smtp']:
        summary += "- SMTP: port 25\n"
    
    summary += """
## Quick Findings
"""
    
    findings = []
    
    # Check for interesting findings
    # FTP anonymous
    ftp_file = f"{output_dir}/ftp/anonymous.txt"
    if os.path.exists(ftp_file):
        with open(ftp_file, 'r') as f:
            content = f.read()
            if "drw" in content or "-rw" in content:
                findings.append("- [!] FTP anonymous access allowed")
    
    # SMB null session
    smb_file = f"{output_dir}/smb/shares.txt"
    if os.path.exists(smb_file):
        with open(smb_file, 'r') as f:
            if "Sharename" in f.read():
                findings.append("- [!] SMB null session allowed")
    
    # NFS exports
    nfs_file = f"{output_dir}/nfs/showmount.txt"
    if os.path.exists(nfs_file):
        with open(nfs_file, 'r') as f:
            if "Export list" in f.read():
                findings.append("- [!] NFS exports found")
    
    # SNMP community strings
    snmp_file = f"{output_dir}/snmp/snmpwalk_public.txt"
    if os.path.exists(snmp_file):
        with open(snmp_file, 'r') as f:
            content = f.read()
            if "Timeout" not in content and len(content) > 100:
                findings.append("- [!] SNMP public community string works")
    
    if findings:
        summary += '\n'.join(findings)
    else:
        summary += "- No quick wins found, manual enumeration needed"
    
    summary += """

## Next Steps
1. Review nmap output for all versions
2. Check web directories for interesting files
3. Look for default credentials
4. Search for exploits based on versions
5. Check for config files with credentials
"""
    
    # Save summary
    with open(f"{output_dir}/notes.md", 'w') as f:
        f.write(summary)
    
    print(f"\n{Colors.CYAN}{'='*50}{Colors.RESET}")
    print(summary)
    print(f"{Colors.CYAN}{'='*50}{Colors.RESET}")
    
    return summary

# ============== MAIN ==============

def main():
    banner()
    
    parser = argparse.ArgumentParser(description="Linux Auto-Enumerator")
    parser.add_argument("target", help="Target IP address")
    parser.add_argument("-o", "--output", help="Output directory", default=None)
    parser.add_argument("--skip-web", action="store_true", help="Skip web enumeration")
    parser.add_argument("--skip-nikto", action="store_true", help="Skip Nikto (faster)")
    parser.add_argument("--quick", action="store_true", help="Quick scan only (skip full port scan)")
    
    args = parser.parse_args()
    
    target = args.target
    
    # Check dependencies
    check_dependencies()
    
    # Setup output directory
    output_dir = args.output or f"./{target}"
    create_directories(output_dir)
    print_status(f"Output directory: {output_dir}", "info")
    
    print(f"\n{Colors.CYAN}{'='*50}{Colors.RESET}")
    print(f"{Colors.BOLD}Starting enumeration on {target}{Colors.RESET}")
    print(f"{Colors.CYAN}{'='*50}{Colors.RESET}\n")
    
    # ===== NMAP SCAN =====
    print(f"\n{Colors.GREEN}[PORT SCANNING]{Colors.RESET}\n")
    nmap_output = nmap_scan(target, output_dir)
    
    # Parse open ports
    ports_found = parse_nmap_ports(nmap_output)
    
    # ===== SERVICE ENUMERATION =====
    print(f"\n{Colors.GREEN}[SERVICE ENUMERATION]{Colors.RESET}\n")
    
    # Web enumeration
    if ports_found['web'] and not args.skip_web:
        web_enum(target, output_dir, ports_found['web'])
    
    # SMB enumeration
    if ports_found['smb']:
        smb_enum(target, output_dir)
    
    # NFS enumeration
    if ports_found['nfs']:
        nfs_enum(target, output_dir)
    
    # SNMP enumeration
    if ports_found['snmp']:
        snmp_enum(target, output_dir)
    
    # FTP enumeration
    if ports_found['ftp']:
        ftp_enum(target, output_dir)
    
    # SMTP enumeration
    if ports_found['smtp']:
        smtp_enum(target, output_dir)
    
    # Generate summary
    generate_summary(target, output_dir, ports_found)
    
    print_status(f"Enumeration complete! Check {output_dir}/ for results", "success")

if __name__ == "__main__":
    main()
