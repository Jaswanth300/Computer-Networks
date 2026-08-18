# Question 1: Star Topology Generator & Connection Verifier

## Overview
This module implements an Ethernet Star Topology generator and verification engine in Python. It models end hosts connected to a central switch via Cat6 UTP cabling, produces ASCII art and graphical network diagrams, performs automated topology validation against IEEE 802.3 standards, and explains the reliable communication mechanics of star topologies.

## Key Features
- **Flexible Host Configuration**: Accepts any number of hosts up to maximum switch port capacity (default 48).
- **ASCII & Graphical Rendering**: Outputs formatted text layout and saves high-resolution PNG graph (`star_topology_graph.png`).
- **Cat6 UTP Cable Tracking**: Assigns and verifies individual segment lengths.
- **Automated Verification Engine**: Checks for single point of attachment to central switch, switch degree compliance, absence of illegal direct host-to-host links, and cable length compliance ($\le 100\text{m}$).
- **Comprehensive Error Handling**: Validates input types, bounds ($>0$ and $\le 48$), and invalid types.

## Files Generated
- `q1_star_topology.py`: Primary Python implementation and test script.
- `ascii_topology.txt`: Text file containing generated ASCII topology diagram and host connection table.
- `star_topology_graph.png`: High-DPI graphical topology visualization with labelled hosts, switch, and Cat6 cable segment lengths.
- `star_topology_explanation.txt`: Technical explanation of star topology reliability in LAN environments.

## Execution & Test Results
To execute Question 1:
```bash
python Q1/q1_star_topology.py
```
All verification checks passed for standard 6-host configuration, and edge cases (0 hosts, negative hosts, exceeding 48 ports, string inputs) were successfully trapped and handled without crashing.
