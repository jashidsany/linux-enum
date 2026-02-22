#!/bin/bash

# Linux-Enum Installation Script
# Installs all required tools for the Linux Auto-Enumerator

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}"
echo "╦  ╦╔╗╔╦ ╦═╗ ╦  ╔═╗╔╗╔╦ ╦╔╦╗"
echo "║  ║║║║║ ║╔╩╦╝  ║╣ ║║║║ ║║║║"
echo "╩═╝╩╝╚╝╚═╝╩ ╚═  ╚═╝╝╚╝╚═╝╩ ╩"
echo "Installation Script"
echo -e "${NC}"

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo -e "${YELLOW}[!] Some installations may require sudo${NC}"
fi

echo -e "\n${GREEN}[*] Checking and installing required tools...${NC}\n"

# Function to check if tool exists
check_tool() {
    if command -v $1 &> /dev/null; then
        echo -e "${GREEN}[+] $1 is installed${NC}"
        return 0
    else
        echo -e "${RED}[-] $1 is NOT installed${NC}"
        return 1
    fi
}

# Function to install tool
install_tool() {
    echo -e "${YELLOW}[*] Installing $1...${NC}"
    sudo apt install -y $1 > /dev/null 2>&1
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}[+] $1 installed successfully${NC}"
    else
        echo -e "${RED}[-] Failed to install $1${NC}"
    fi
}

echo "================================"
echo "Required Tools"
echo "================================"

# Nmap
check_tool nmap || install_tool nmap

# Gobuster
check_tool gobuster || install_tool gobuster

# Nikto
check_tool nikto || install_tool nikto

# Smbclient
check_tool smbclient || install_tool smbclient

# Netcat
check_tool nc || install_tool netcat-openbsd

# Curl
check_tool curl || install_tool curl

echo ""
echo "================================"
echo "Optional Tools (Recommended)"
echo "================================"

# Dirsearch
if ! check_tool dirsearch; then
    echo -e "${YELLOW}[*] Installing dirsearch...${NC}"
    sudo apt install -y dirsearch > /dev/null 2>&1
    if [ $? -ne 0 ]; then
        # Try pip install
        pip3 install dirsearch > /dev/null 2>&1
    fi
fi

# Ffuf
if ! check_tool ffuf; then
    echo -e "${YELLOW}[*] Installing ffuf...${NC}"
    sudo apt install -y ffuf > /dev/null 2>&1
    if [ $? -ne 0 ]; then
        # Try go install
        go install github.com/ffuf/ffuf@latest > /dev/null 2>&1
    fi
fi

# enum4linux-ng
if ! check_tool enum4linux-ng; then
    echo -e "${YELLOW}[*] Installing enum4linux-ng...${NC}"
    sudo apt install -y enum4linux-ng > /dev/null 2>&1
    if [ $? -ne 0 ]; then
        pip3 install enum4linux-ng > /dev/null 2>&1
    fi
fi

# smbmap
check_tool smbmap || install_tool smbmap

# snmpwalk
check_tool snmpwalk || install_tool snmp

# snmp-check
check_tool snmp-check || install_tool snmp-check

# showmount (nfs-common)
if ! check_tool showmount; then
    install_tool nfs-common
fi

# rpcinfo
check_tool rpcinfo || install_tool rpcbind

# smtp-user-enum
if ! check_tool smtp-user-enum; then
    echo -e "${YELLOW}[*] Installing smtp-user-enum...${NC}"
    sudo apt install -y smtp-user-enum > /dev/null 2>&1
fi

echo ""
echo "================================"
echo "Wordlists"
echo "================================"

# SecLists
if [ -d "/usr/share/seclists" ]; then
    echo -e "${GREEN}[+] SecLists is installed${NC}"
else
    echo -e "${YELLOW}[*] Installing SecLists...${NC}"
    sudo apt install -y seclists > /dev/null 2>&1
fi

# Dirb wordlists
if [ -d "/usr/share/wordlists/dirb" ]; then
    echo -e "${GREEN}[+] Dirb wordlists available${NC}"
else
    echo -e "${YELLOW}[*] Installing dirb (for wordlists)...${NC}"
    sudo apt install -y dirb > /dev/null 2>&1
fi

# Rockyou
if [ -f "/usr/share/wordlists/rockyou.txt" ]; then
    echo -e "${GREEN}[+] rockyou.txt is available${NC}"
elif [ -f "/usr/share/wordlists/rockyou.txt.gz" ]; then
    echo -e "${YELLOW}[*] Extracting rockyou.txt...${NC}"
    sudo gunzip /usr/share/wordlists/rockyou.txt.gz
    echo -e "${GREEN}[+] rockyou.txt extracted${NC}"
else
    echo -e "${RED}[-] rockyou.txt not found${NC}"
fi

echo ""
echo "================================"
echo "Python Dependencies"
echo "================================"

# Check Python3
check_tool python3

echo ""
echo "================================"
echo -e "${GREEN}Installation Complete!${NC}"
echo "================================"
echo ""
echo "Usage:"
echo "  python3 linux-enum.py <target-ip>"
echo "  python3 linux-enum.py <target-ip> --quick"
echo "  python3 linux-enum.py <target-ip> --skip-nikto"
echo ""
