# Security Monitoring & Privacy System

A Linux-based security monitoring and attack detection system that monitors access activity, detects suspicious behaviour, and protects synthetic personal data through data generalisation.

## Project Overview

This project combines security monitoring, attack detection, and privacy-aware data storage in an isolated virtual lab environment.

The Ubuntu VM operates as the main application and monitoring server, while the Kali Linux VM is used to generate controlled security-testing traffic.


## Network Configuration

Each virtual machine uses two network adapters:

* NAT provides outbound Internet access.
* Host-only provides isolated communication between Windows, Ubuntu, and Kali.

| System        | Interface            | IP address         | Purpose           |
| ------------- | -------------------- | ------------------ | ----------------- |
| Windows host  | VirtualBox Host-only | `192.168.56.1/24`  | VM administration |
| Ubuntu Server | `enp0s8`             | `192.168.56.10/24` | Monitoring server |
| Kali Linux    | `eth1`               | `192.168.56.20/24` | Security testing  |
| Ubuntu/Kali   | NAT adapter          | DHCP               | Internet access   |

Ubuntu was configured using Netplan, while Kali was configured using NetworkManager.

## Remote Administration

OpenSSH is enabled on both virtual machines and starts automatically during boot.

Example connections from Windows PowerShell:

```powershell
ssh <ubuntu-user>@192.168.56.10
ssh <kali-user>@192.168.56.20
```



All testing is performed in a controlled virtual lab using synthetic data. Attack simulations must only be conducted against systems owned by or explicitly authorised for this project.


## Synthetic Data
The project uses a synthetically generated dataset containing 5,000 records. 
No real personal information is used.

Each raw record contains the following attributes:
- `record_id`
- `age`
- `postcode`
- `income`
- `occupation`

Income is generated using occupation-specific salary ranges with a weak age dependency to introduce realistic variation while maintaining fully synthetic data. 
