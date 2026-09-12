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

The raw dataset is generated using `src/privacy/generate_data.py` and saved in `data/raw/synthetic_users.csv`.

## Data Generalisation

Four attributes were selected as quasi-identifiers: age, postcode, income, and occupation.

These attributes are generalised to reduce the amount of specific information stored in the dataset.

| Attribute | Generalisation | Example |
| --- | --- | --- |
| Age | 10-year age groups | `37` → `30-39` |
| Postcode | Keep the first two digits | `2122` → `21**` |
| Income | $10,000 ranges | `87,000` → `80k-90k` |
| Occupation | Group similar occupations | `Data Analyst` → `Technology` |


## Privacy Analysis

Privacy was evaluated by checking how many records share the same combination of the four generalised quasi-identifiers.


### Record Uniqueness

| Metric | Current | Stronger |
| --- | ---: | ---: |
| Unique records | 25 | 5 |
| Uniqueness rate | 0.50% | 0.10% |
| Records in groups of 5 or more | 4,764 | 4,941 |
| Percentage in groups of 5 or more | 95.28% | 98.82% |

The stronger generalisation reduced the number of unique records from 25 to 5. It also increased the number of records that share their quasi-identifier combination with at least four other records.

### Privacy and Data Utility

Data utility was compared using the number of different categories remaining after generalisation.

| Attribute | Current | Stronger |
| --- | ---: | ---: |
| Age categories | 6 | 3 |
| Postcode categories | 3 | 3 |
| Income categories | 10 | 6 |
| Occupation categories | 6 | 6 |

The stronger generalisation reduced record uniqueness, but it also reduced some of the detail available for analysis.

Age categories decreased from 6 to 3 and income categories decreased from 10 to 6. Postcode and occupation categories remained the same.

This shows the trade-off between privacy and data utility: stronger generalisation can make records harder to distinguish, but it can also reduce the amount of detail available for analysis.
