# Question 3: CSMA/CD Protocol Simulator in Star Topology

## Overview
This module simulates the Carrier Sense Multiple Access with Collision Detection (CSMA/CD) protocol operating across a 4-host Ethernet star topology (half-duplex hub/shared medium model).

## Key Features
- **4-Host Simulation Environment**: Models `Host_A`, `Host_B`, `Host_C`, and `Host_D` competing for physical channel access.
- **Carrier Sensing (Listen Before Talk)**: Monitors physical channel state and defers transmission if busy.
- **Collision Detection & Jamming Signal**: Detects simultaneous transmission attempts and broadcasts a 32-bit Jamming signal.
- **Binary Exponential Back-Off (BEB) Algorithm**: Calculates back-off multipliers $k \in [0, 2^i - 1]$ based on collision count $i$, scaling wait intervals ($k \times 51.2\,\mu\text{s}$ standard slot time).
- **Comprehensive Event Logging**: Records every carrier sense check, transmission attempt, collision event, back-off interval calculation, and frame completion in `csma_log.txt`.
- **Graphical Event Timeline**: Renders a multi-track Gantt timeline visualization (`csma_cd_timeline.png`).

## Files Generated
- `q3_csma_cd_simulator.py`: Python simulator implementation and plotting module.
- `csma_log.txt`: Recorded event log documenting all CSMA/CD operations.
- `csma_cd_timeline.png`: High-resolution graphical timeline displaying transmission starts, collisions, backoff periods, and successful frame deliveries.
- `csma_cd_analysis.txt`: Comprehensive technical analysis explaining how CSMA/CD minimizes data transmission conflicts in Ethernet networks.

## Execution
To run the CSMA/CD simulation:
```bash
python Q3/q3_csma_cd_simulator.py
```
