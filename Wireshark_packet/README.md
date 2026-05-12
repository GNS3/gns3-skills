# Wireshark Packet Capture Files

## Overview

This directory contains network protocol packet capture files for learning and practicing Wireshark packet analysis.

## Source

These packet capture files were obtained from:
- **Repository**: [open-source-toolkit/480f78](https://gitcode.com/open-source-toolkit/480f78)
- **Platform**: GitCode

## Directory Structure

```
Wireshark_packet/
├── protocol_browse/      # Browse captures by network protocol
├── category_browse/      # Browse captures by functional category
└── README.md            # This file
```

### Category Browse

The `category_browse/` directory organizes captures by functional area:

- **Authentication** - Authentication protocols (CHAP, EAP, etc.)
- **Cisco_Proprietary** - Cisco proprietary protocols (CDP, DTP, etc.)
- **Encryption** - Encryption protocols (AH, ESP, IPsec)
- **Management** - Network management protocols
- **MPLS** - Multiprotocol Label Switching
- **Multicast** - Multicast protocols (PIM, IGMP, etc.)
- **Redundancy** - High availability protocols (HSRP, GLBP, VRRP)
- **Routing_Protocols** - Routing protocols (BGP, OSPF, EIGRP, etc.)
- **Switching** - LAN switching protocols (STP, VLAN, etc.)
- **Tunneling** - Tunneling protocols (GRE, IPsec, etc.)
- **Web** - Web-related protocols (HTTP, DNS, etc.)

### Protocol Browse

The `protocol_browse/` directory contains individual protocol captures including:

- ARP, BGP, BOOTP, CDP, DNS, EIGRP, GRE, HSRP, HTTP, ICMP, IGMP, IP, OSPF, and many more.

## Usage

These capture files can be opened with Wireshark or compatible network analysis tools for:
- Protocol study and learning
- Packet analysis practice
- Network troubleshooting reference
- Certification exam preparation (CCNA, CCNP, etc.)

## License

Please refer to the original source repository for licensing information.
