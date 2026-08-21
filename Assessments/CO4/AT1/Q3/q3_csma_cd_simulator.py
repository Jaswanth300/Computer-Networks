"""
Question 3: CSMA/CD Protocol Simulator in Ethernet Star Topology
Course: Computer Networks (CSA07) - Assessment Tool 1 (CO4)

This script simulates the Carrier Sense Multiple Access with Collision Detection (CSMA/CD)
protocol for 4 hosts connected through a shared central star switch/hub topology.
It logs all attempts, collisions, and Binary Exponential Back-off intervals to `csma_log.txt`,
generates a graphical timeline plot, and provides technical analysis on conflict minimization.
"""

import os
import random
import time
import matplotlib.pyplot as plt

class CSMACDHost:
    """
    Represents a host operating under the CSMA/CD protocol.
    """
    def __init__(self, host_id: str, slot_time_ms: float = 51.2):
        self.host_id = host_id
        self.slot_time_ms = slot_time_ms  # IEEE 802.3 standard slot time (51.2 us scaled to ms for sim)
        self.collision_count = 0
        self.max_retries = 16
        self.frames_to_send = []
        self.backoff_until = 0.0
        self.state = "IDLE"  # IDLE, WAITING_BACKOFF, SENSING, TRANSMITTING, SUCCESS, FAILED
        self.current_frame = None

    def add_frame(self, frame_id: str, dest_id: str):
        self.frames_to_send.append({"frame_id": frame_id, "dest": dest_id, "attempt": 0})

    def calculate_backoff(self) -> tuple[int, float]:
        """
        Calculates Binary Exponential Backoff:
        k chosen uniformly from [0, 2^i - 1] where i = min(collision_count, 10).
        Returns (k, backoff_duration_ms).
        """
        i = min(self.collision_count, 10)
        max_k = (2 ** i) - 1
        k = random.randint(0, max_k)
        backoff_time = k * self.slot_time_ms
        return k, backoff_time


class CSMACDNetworkSimulator:
    """
    Simulates shared medium communication among 4 hosts using CSMA/CD protocol.
    """
    def __init__(self, host_ids: list[str], log_filepath: str = "Q3/csma_log.txt"):
        self.host_ids = host_ids
        self.log_filepath = log_filepath
        self.hosts = {h_id: CSMACDHost(h_id) for h_id in host_ids}
        self.channel_busy_until = 0.0
        self.current_time = 0.0
        self.time_step = 10.0  # 10 ms time step
        self.log_entries = []
        self.events_history = []  # For timeline plotting

    def log(self, message: str):
        timestamp_str = f"[{self.current_time:07.1f} ms]"
        entry = f"{timestamp_str} {message}"
        self.log_entries.append(entry)
        print(entry)

    def run_simulation(self, total_frames_per_host: int = 2, max_sim_time: float = 2000.0):
        """Executes the CSMA/CD event simulation loop."""
        random.seed(101)  # Fixed seed for deterministic, repeatable test results
        
        # Populate initial frame queues for 4 hosts
        destinations = {
            "Host_A": "Host_B",
            "Host_B": "Host_A",
            "Host_C": "Host_D",
            "Host_D": "Host_C"
        }
        for h_id in self.host_ids:
            for f_idx in range(1, total_frames_per_host + 1):
                self.hosts[h_id].add_frame(f"FRAME_{h_id}_{f_idx}", destinations[h_id])

        self.log("=" * 80)
        self.log("          CSMA/CD ETHERNET STAR TOPOLOGY SIMULATION STARTED")
        self.log("=" * 80)
        self.log(f"Active Hosts: {', '.join(self.host_ids)}")
        self.log("Medium Parameters: IEEE 802.3 Half-Duplex Star, Slot Time = 51.2 ms")
        self.log("-" * 80)

        completed_frames = 0
        total_expected_frames = len(self.host_ids) * total_frames_per_host

        while self.current_time < max_sim_time and completed_frames < total_expected_frames:
            # 1. Update host states based on backoff timer
            for h_id, host in self.hosts.items():
                if host.state == "WAITING_BACKOFF":
                    if self.current_time >= host.backoff_until:
                        host.state = "READY"
                        self.log(f"[STATE CHANGE] {h_id} completed back-off delay. Status: READY to transmit.")
                        self.events_history.append((self.current_time, h_id, "BACKOFF_END", "Ready"))

            # 2. Check which hosts are ready to attempt transmission at this time step
            attempting_hosts = []
            for h_id, host in self.hosts.items():
                if host.frames_to_send and host.state in ["IDLE", "READY"]:
                    attempting_hosts.append(h_id)

            # 3. Carrier Sense & Collision Handling
            if attempting_hosts:
                # Carrier Sense: Check if channel is busy
                if self.current_time < self.channel_busy_until:
                    # Channel is BUSY
                    for h_id in attempting_hosts:
                        self.log(f"[CARRIER SENSE] {h_id} sensed channel BUSY. Deferring transmission attempt.")
                        self.events_history.append((self.current_time, h_id, "CARRIER_BUSY", "Deferred"))
                else:
                    # Channel is IDLE
                    if len(attempting_hosts) == 1:
                        # Successful Transmission (Single host transmitting)
                        transmitting_host = self.hosts[attempting_hosts[0]]
                        frame = transmitting_host.frames_to_send[0]
                        tx_duration = 150.0  # Frame transmission time = 150 ms
                        
                        self.channel_busy_until = self.current_time + tx_duration
                        transmitting_host.state = "TRANSMITTING"
                        transmitting_host.collision_count = 0  # Reset collision counter on success
                        
                        self.log(f"[TRANSMISSION ATTEMPT] {transmitting_host.host_id} sensed channel IDLE. Transmitting {frame['frame_id']} to {frame['dest']} (Duration: {tx_duration} ms).")
                        self.events_history.append((self.current_time, transmitting_host.host_id, "TX_START", frame['frame_id']))
                        
                        # Remove frame from queue
                        transmitting_host.frames_to_send.pop(0)
                        transmitting_host.state = "IDLE"
                        completed_frames += 1
                        
                        self.log(f"[SUCCESS] {transmitting_host.host_id} successfully delivered {frame['frame_id']} without collision.")
                        self.events_history.append((self.current_time + tx_duration, transmitting_host.host_id, "TX_SUCCESS", frame['frame_id']))

                    else:
                        # COLLISION EVENT (Multiple hosts attempt transmission simultaneously)
                        colliding_ids = attempting_hosts
                        collision_duration = 30.0  # Collision detection + Jamming signal time = 30 ms
                        self.channel_busy_until = self.current_time + collision_duration
                        
                        self.log("!" * 80)
                        self.log(f"[COLLISION DETECTED] Multiple hosts {colliding_ids} attempted simultaneous transmission!")
                        self.log(f"[JAMMING SIGNAL] Broadcasting 32-bit Jamming signal to enforce collision state across star hub.")
                        self.log("!" * 80)

                        for h_id in colliding_ids:
                            host = self.hosts[h_id]
                            host.collision_count += 1
                            
                            if host.collision_count > host.max_retries:
                                self.log(f"[FRAME ABORT] {h_id} exceeded max retry limit ({host.max_retries}). Dropping frame.")
                                host.frames_to_send.pop(0)
                                host.collision_count = 0
                                host.state = "IDLE"
                            else:
                                k, backoff_ms = host.calculate_backoff()
                                host.backoff_until = self.current_time + collision_duration + backoff_ms
                                host.state = "WAITING_BACKOFF"
                                
                                self.log(f"[BACK-OFF CALCULATED] {h_id} | Collision #{host.collision_count} | BEB multiplier k={k} | Wait Time: {backoff_ms:.1f} ms | Resume at: {host.backoff_until:.1f} ms.")
                                self.events_history.append((self.current_time, h_id, "COLLISION", f"Collision #{host.collision_count}"))
                                self.events_history.append((self.current_time + collision_duration, h_id, "BACKOFF_START", f"k={k}, {backoff_ms:.1f}ms"))

            self.current_time += self.time_step

        self.log("=" * 80)
        self.log(f"CSMA/CD SIMULATION COMPLETED: {completed_frames}/{total_expected_frames} Frames Delivered.")
        self.log("=" * 80)

        # Save log file
        os.makedirs(os.path.dirname(self.log_filepath), exist_ok=True)
        with open(self.log_filepath, "w") as f:
            f.write("\n".join(self.log_entries))
        print(f"\n[SUCCESS] CSMA/CD log file written to: {self.log_filepath}")

    def plot_timeline(self, output_path: str = "Q3/csma_cd_timeline.png"):
        """Plots event timeline showing transmission attempts, collisions, and backoffs."""
        plt.figure(figsize=(12, 6), dpi=300)
        ax = plt.gca()

        y_positions = {h_id: idx for idx, h_id in enumerate(reversed(self.host_ids))}
        
        event_colors = {
            "TX_START": "#2E7D32",     # Green
            "TX_SUCCESS": "#4CAF50",   # Light Green
            "COLLISION": "#D32F2F",    # Red
            "BACKOFF_START": "#FF9800", # Orange
            "CARRIER_BUSY": "#9E9E9E"   # Grey
        }
        
        event_markers = {
            "TX_START": "^",
            "TX_SUCCESS": "o",
            "COLLISION": "X",
            "BACKOFF_START": "s",
            "CARRIER_BUSY": "v"
        }

        for timestamp, h_id, evt_type, label in self.events_history:
            if evt_type in event_colors:
                y = y_positions[h_id]
                color = event_colors[evt_type]
                marker = event_markers[evt_type]
                
                plt.scatter(timestamp, y, color=color, marker=marker, s=120, zorder=5, edgecolors="black")
                if evt_type in ["COLLISION", "TX_START"]:
                    plt.annotate(f"{label}", (timestamp, y), textcoords="offset points", 
                                 xytext=(0, 10), ha='center', fontsize=8, fontweight='bold', color=color)

        # Draw horizontal lines for host tracks
        for h_id, y in y_positions.items():
            plt.axhline(y=y, color="#E0E0E0", linestyle="--", linewidth=1.5, zorder=1)

        plt.yticks(list(y_positions.values()), list(y_positions.keys()), fontsize=10, fontweight="bold")
        plt.xlabel("Simulation Time (Milliseconds)", fontsize=10, fontweight="bold", labelpad=10)
        plt.title("CSMA/CD Transmission, Collision, and Binary Exponential Back-Off Timeline", 
                  fontsize=12, fontweight="bold", pad=15, color="#003366")
        plt.grid(axis="x", linestyle=":", alpha=0.6)
        
        # Legend
        custom_lines = [
            plt.Line2D([0], [0], color="#2E7D32", marker="^", linestyle="None", markersize=8, label="Tx Start"),
            plt.Line2D([0], [0], color="#4CAF50", marker="o", linestyle="None", markersize=8, label="Tx Success"),
            plt.Line2D([0], [0], color="#D32F2F", marker="X", linestyle="None", markersize=8, label="Collision Event"),
            plt.Line2D([0], [0], color="#FF9800", marker="s", linestyle="None", markersize=8, label="Back-off Start"),
            plt.Line2D([0], [0], color="#9E9E9E", marker="v", linestyle="None", markersize=8, label="Sensed Busy")
        ]
        plt.legend(handles=custom_lines, loc="upper right", frameon=True, facecolor="#F0F4F8")

        plt.tight_layout()
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        plt.savefig(output_path, bbox_inches="tight", dpi=300)
        plt.close()
        print(f"[SUCCESS] CSMA/CD timeline plot saved to: {output_path}")


def get_csma_cd_technical_analysis() -> str:
    return """================================================================================
TECHNICAL ANALYSIS: HOW CSMA/CD MINIMIZES DATA TRANSMISSION CONFLICTS
================================================================================
1. Carrier Sense (Listen Before Talk):
   Before initiating frame transmission, a host listens to the physical channel 
   (Carrier Sense). If the medium is sensed busy (voltage presence detected), the host 
   defers transmission until the channel becomes idle. This significantly reduces 
   collisions compared to uncoordinated protocols like Pure ALOHA.

2. Immediate Collision Detection & Jamming Signal:
   Despite carrier sensing, collisions can occur due to propagation delay (the time 
   it takes a signal to travel down the physical wire). When two hosts transmit 
   nearly simultaneously, their signals overlap and collide. Under CSMA/CD, hosts 
   actively monitor signal voltage while transmitting. Upon detecting a collision:
   - Hosts IMMEDIATELY abort transmission (saving channel bandwidth).
   - Hosts transmit a 32-bit Jamming Signal to ensure all network nodes recognize 
     the collision event and discard corrupted frame fragments.

3. Binary Exponential Back-Off (BEB) Algorithm:
   To prevent hosts from repeatedly colliding upon retransmission, CSMA/CD employs BEB:
   - For collision count 'i' (where i = min(n, 10)), the host chooses a random integer 
     'k' from the range [0, 2^i - 1].
   - The host waits for k * SlotTime (51.2 microseconds) before sensing the channel again.
   - As collision frequency increases, the backoff window expands exponentially (1, 3, 7, 
     15, 31... 1023 slots). This dynamically disperses retransmission attempts across time, 
     effectively resolving heavy channel congestion and minimizing future conflicts.
================================================================================
"""

def main():
    print("=== CO4 AT1: QUESTION 3 - CSMA/CD PROTOCOL SIMULATOR ===")
    
    hosts = ["Host_A", "Host_B", "Host_C", "Host_D"]
    sim = CSMACDNetworkSimulator(host_ids=hosts, log_filepath="Q3/csma_log.txt")
    
    # Run simulation
    sim.run_simulation(total_frames_per_host=2, max_sim_time=1500.0)
    
    # Also write a copy to Q3/csma_log.txt if needed (already written)
    
    # Plot timeline
    sim.plot_timeline("Q3/csma_cd_timeline.png")
    
    # Technical analysis
    analysis = get_csma_cd_technical_analysis()
    print(analysis)
    with open("Q3/csma_cd_analysis.txt", "w") as f:
        f.write(analysis)

if __name__ == "__main__":
    main()
