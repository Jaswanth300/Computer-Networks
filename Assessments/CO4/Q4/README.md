# Question 4: Client-Server Socket Ethernet Switch MAC Learning Simulator

## Overview
This module implements a multithreaded client-server application using Python's standard `socket` library to simulate an Ethernet switch operating in a star topology. The switch server listens on TCP sockets, receives structured Ethernet frames, performs source MAC address self-learning, updates its MAC Address Table, executes forwarding decisions (Unicast vs Broadcast/Flood), and logs table states.

## Key Features
- **Multithreaded Socket Server**: Accepts concurrent TCP host connections on individual switch ports.
- **Ethernet Frame Processing**: Decodes JSON frame objects containing `src_mac`, `dst_mac`, and `payload`.
- **Source MAC Self-Learning**: Dynamically binds source MAC addresses to ingress port numbers.
- **Intelligent Frame Forwarding**:
  - *Known Unicast*: Forwards directly to target egress port.
  - *Unknown Unicast*: Floods frame to all active ports except ingress port.
  - *Broadcast (`FF:FF:FF:FF:FF:FF`)*: Floods frame across broadcast domain.
- **Formatted Table Output & Logging**: Prints formatted MAC table to stdout after every transmission and writes `mac_table_log.txt`.
- **Graphical MAC Summary**: Generates `mac_learning_table_chart.png`.

## Files Generated
- `q4_mac_switch_sockets.py`: Primary Python implementation with switch server, host client, and plot generator.
- `mac_table_log.txt`: Execution log recording frame receptions, learning events, MAC table updates, and forwarding decisions.
- `mac_learning_table_chart.png`: Visual summary graphic of learned MAC address table entries.
- `mac_learning_explanation.txt`: Technical document explaining CAM tables, self-learning, aging, and micro-segmentation.

## Execution
To run Question 4:
```bash
python Q4/q4_mac_switch_sockets.py
```
