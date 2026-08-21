# Question 5: StarSwitch Class Implementation & Broadcast Simulator

## Overview
This module implements the `StarSwitch` Python class to model Ethernet switch behavior in a star topology. It provides methods for connecting hosts (`add_port`), disconnecting hosts (`remove_port`), broadcasting frames (`broadcast`), tracking active port states, and logging broadcast operations.

## Key Features
- **Class `StarSwitch`**:
  - `add_port(host_id)`: Binds a host to the lowest available switch port.
  - `remove_port(host_id)`: Frees the assigned port when a host disconnects.
  - `broadcast(frame)`: Delivers frames to all active connected ports except the source port.
- **Port Management & State Tracking**: Maintains dynamic mappings of port numbers to host IDs and vice versa.
- **Comprehensive Broadcast Logging**: Records timestamps, source host, ingress port, frame payload, list of successful destination recipient hosts, and excluded source port.
- **Robust Exception Handling**: Traps duplicate host additions, removal of non-existent hosts, broadcasts from disconnected hosts, and port overflow.
- **Graphical Visualization**: Renders high-resolution diagram (`star_switch_broadcast_chart.png`) showing StarSwitch layout and broadcast propagation.

## Files Generated
- `q5_star_switch.py`: Primary Python class implementation and test suite.
- `switch_broadcast_log.txt`: Recorded event log documenting port attachments/detachments and broadcast operations.
- `star_switch_broadcast_chart.png`: Visual graph rendering StarSwitch ports, source ingress, and flooded egress host nodes.
- `broadcasting_explanation.txt`: Technical document detailing the role of broadcasting in ARP resolution, DHCP discovery, and VLAN boundary limits.

## Execution
To run Question 5:
```bash
python Q5/q5_star_switch.py
```
