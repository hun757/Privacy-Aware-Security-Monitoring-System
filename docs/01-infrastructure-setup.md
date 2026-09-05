# Infrastructure Setup

> Initial virtual security lab environment for the Privacy-Aware Security Monitoring System.

---

## 📌 Objective

This document records the initial infrastructure setup for a controlled security monitoring lab.

The environment separates the monitoring server from the attack simulation machine while allowing secure remote administration from the Windows host. The lab will later be used to collect access logs, simulate authorised attacks, evaluate detection rules, and investigate privacy-aware storage of synthetic personal data.

---

## 🖥️ Virtual Lab Environment

| Component               | Technology        | Purpose                                       |
| ----------------------- | ----------------- | --------------------------------------------- |
| Host machine            | Windows           | Virtual machine administration and SSH client |
| Virtualisation platform | Oracle VirtualBox | Isolated lab environment                      |
| Server VM               | Ubuntu Server     | Security monitoring and application server    |
| Testing VM              | Kali Linux        | Controlled attack simulation machine          |
| Remote access           | OpenSSH           | Secure command-line administration            |

---

## 🌐 Network Design

Each virtual machine uses two network adapters.

```text
Adapter 1: NAT
    └── Provides outbound Internet access for updates and GitHub access

Adapter 2: Host-only Adapter
    └── Provides an isolated private network between Windows, Ubuntu, and Kali
```

The Host-only network is separated from the physical Wi-Fi network. This allows security testing to be performed inside the virtual lab without exposing the testing environment to other devices on the local network.

### Host-only Network Addressing

| System        | Interface                    | Static IP Address  | Role                      |
| ------------- | ---------------------------- | ------------------ | ------------------------- |
| Windows Host  | VirtualBox Host-only Adapter | `192.168.56.1/24`  | Administration machine    |
| Ubuntu Server | `enp0s8`                     | `192.168.56.10/24` | Monitoring server         |
| Kali Linux    | `eth1`                       | `192.168.56.20/24` | Attack simulation machine |

The NAT interfaces continue to use DHCP and are responsible for Internet connectivity.

---

## ⚙️ Ubuntu Server Configuration

Ubuntu Server was configured as the main server for the project.

### Static IP Configuration

Ubuntu uses Netplan to configure the Host-only interface.

Configuration file:

```text
/etc/netplan/99-host-only.yaml
```

```yaml
network:
  version: 2
  ethernets:
    enp0s8:
      dhcp4: false
      addresses:
        - 192.168.56.10/24
      optional: true
```

The configuration was validated and applied with:

```bash
sudo netplan generate
sudo netplan apply
ip -br address
```

### SSH Configuration

OpenSSH was enabled to allow remote administration from the Windows host.

```bash
sudo systemctl enable --now ssh
sudo systemctl status ssh
```

The SSH service is configured to start automatically whenever the Ubuntu VM boots.

---

## ⚙️ Kali Linux Configuration

Kali Linux was configured as the controlled attack simulation machine.

### Static IP Configuration

Kali uses NetworkManager to configure the Host-only interface.

```text
Interface: eth1
Static IP: 192.168.56.20/24
```

The connection was configured to automatically reconnect after boot.

### SSH Configuration

OpenSSH was enabled for remote administration from Windows.

```bash
sudo systemctl enable --now ssh
sudo systemctl status ssh
```

---

## 🔐 Remote Administration

The following SSH connections were successfully verified from Windows PowerShell.

```powershell
ssh jeonghun@192.168.56.10
ssh kali@192.168.56.20
```

| Connection              | Result     |
| ----------------------- | ---------- |
| Windows → Ubuntu Server | Successful |
| Windows → Kali Linux    | Successful |

---
## 🔎 Verification and Test Evidence

The infrastructure was validated through interface checks, ICMP connectivity tests, SSH connection tests, and packet capture.

### 1. Verify Interface Addresses

Ubuntu Server:

```bash
ip -br address
```

Expected Host-only interface:

```text
enp0s8    UP    192.168.56.10/24
```

Kali Linux:

```bash
ip -br address
```

Expected Host-only interface:

```text
eth1      UP    192.168.56.20/24
```

### 2. Verify VM-to-VM Connectivity

With both virtual machines running, test the isolated Host-only network.

From Kali Linux:

```bash
ping -c 4 192.168.56.10
```

From Ubuntu Server:

```bash
ping -c 4 192.168.56.20
```

A successful response confirms that Kali and Ubuntu can communicate through the isolated Host-only network.

### 3. Verify SSH Connectivity from Windows

Windows PowerShell was used to verify remote administration access.

```powershell
ssh jeonghun@192.168.56.10
ssh kali@192.168.56.20
```

| Test                 | Result     |
| -------------------- | ---------- |
| Windows → Ubuntu SSH | Successful |
| Windows → Kali SSH   | Successful |

### 4. Verify SSH Port Availability

The SSH port on Kali was tested from Windows.

```powershell
Test-NetConnection 192.168.56.20 -Port 22
```

The test confirmed that TCP port `22` was reachable from the Windows Host-only adapter.

### 5. Packet-Level Verification

A packet capture was performed on Kali to verify ARP resolution and the SSH TCP handshake.

```bash
sudo tcpdump -eni eth1 'arp or tcp port 22'
```

The capture confirmed:

* Windows successfully resolved Kali's MAC address using ARP.
* The TCP three-way handshake to port `22` completed.
* Kali responded with an OpenSSH server banner.

This provided evidence that the Host-only network and Kali SSH service were operating correctly.
---

## 🧪 Troubleshooting and Findings

During the setup process, the Kali Host-only interface initially did not receive a stable DHCP IPv4 address.

To resolve this issue, static IP addresses were configured manually:

* Ubuntu Server: `192.168.56.10`
* Kali Linux: `192.168.56.20`

Packet capture was also used to verify that the Windows host and Kali VM could complete ARP resolution and the TCP SSH handshake.

This confirmed that the Host-only network and SSH service were working correctly.

---

## 🔒 Security Considerations

* The lab uses a Host-only network to isolate testing traffic from the physical network.
* NAT is retained only for outbound Internet access.
* SSH is used instead of direct VirtualBox console access for server administration.
* Passwords, SSH private keys, API keys, and TryHackMe VPN configuration files must never be committed to this repository.
* Future attack simulations will be performed only against the authorised Ubuntu VM inside this controlled lab.

---

