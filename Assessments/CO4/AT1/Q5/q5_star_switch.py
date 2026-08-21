"""
Question 5: StarSwitch Class Implementation and Ethernet Broadcast Simulator
Course: Computer Networks (CSA07) - Assessment Tool 1 (CO4)

This script defines the `StarSwitch` class modeling an Ethernet switch with core methods:
`add_port(host_id)`, `remove_port(host_id)`, and `broadcast(frame)`.
It tracks active ports, logs all broadcast operations indicating source and successful 
recipient hosts, demonstrates multi-host dynamic scenarios, generates visual graphics, 
and provides a technical explanation on the significance of Ethernet broadcasting.
"""

import os
import time
import matplotlib.pyplot as plt
import networkx as nx

class StarSwitch:
    """
    Models an Ethernet Switch in a Star Topology with dynamic port management
    and frame broadcasting capabilities.
    """
    def __init__(self, switch_name: str = "StarSwitch_Core1", total_ports: int = 24, log_file: str = "Q5/switch_broadcast_log.txt"):
        self.switch_name = switch_name
        self.total_ports = total_ports
        self.log_file = log_file
        
        # Internal Port State: port_number (1..total_ports) -> host_id
        self.ports = {}  # { port_num: host_id }
        self.host_to_port = {}  # { host_id: port_num }
        
        self.log_history = []
        self._log(f"[INITIALIZED] {self.switch_name} created with {self.total_ports} Ethernet ports.")

    def _log(self, message: str):
        timestamp = time.strftime("[%H:%M:%S]")
        entry = f"{timestamp} {message}"
        self.log_history.append(entry)
        print(entry)

    def get_active_ports(self) -> dict:
        """Returns a copy of the current active port mappings."""
        return dict(self.ports)

    def add_port(self, host_id: str) -> int:
        """
        Connects a host to the first available switch port.
        
        Parameters:
            host_id (str): Identifier for the host.
            
        Returns:
            int: Assigned port number.
        """
        if not isinstance(host_id, str) or not host_id.strip():
            raise ValueError(f"Invalid host_id '{host_id}'. Must be a non-empty string.")
            
        host_id = host_id.strip()
        
        if host_id in self.host_to_port:
            raise ValueError(f"Host '{host_id}' is already connected on Port-{self.host_to_port[host_id]}. Duplicate connection denied.")

        # Find lowest available port number
        assigned_port = None
        for p in range(1, self.total_ports + 1):
            if p not in self.ports:
                assigned_port = p
                break
                
        if assigned_port is None:
            raise RuntimeError(f"Switch '{self.switch_name}' port capacity full ({self.total_ports}/{self.total_ports} ports occupied).")

        self.ports[assigned_port] = host_id
        self.host_to_port[host_id] = assigned_port
        self._log(f"[PORT CONNECTED] Host '{host_id}' successfully attached to Port-{assigned_port}.")
        return assigned_port

    def remove_port(self, host_id: str) -> int:
        """
        Disconnects a host and frees its associated switch port.
        
        Parameters:
            host_id (str): Identifier for the host to disconnect.
            
        Returns:
            int: The port number that was freed.
        """
        if host_id not in self.host_to_port:
            raise KeyError(f"Cannot remove host '{host_id}': Host is not connected to any switch port.")
            
        freed_port = self.host_to_port[host_id]
        del self.host_to_port[host_id]
        del self.ports[freed_port]
        
        self._log(f"[PORT DISCONNECTED] Host '{host_id}' removed from Port-{freed_port}. Port-{freed_port} is now FREE.")
        return freed_port

    def broadcast(self, frame: dict) -> dict:
        """
        Transmits a broadcast frame to all active connected ports EXCEPT the source port.
        
        Parameters:
            frame (dict): Must contain 'src_host', 'frame_type', and 'payload'.
            
        Returns:
            dict: Summary of broadcast operation including successful recipients and excluded source.
        """
        if not isinstance(frame, dict):
            raise TypeError("Broadcast frame must be a dictionary object.")
            
        src_host = frame.get("src_host")
        frame_type = frame.get("frame_type", "GENERIC_BROADCAST")
        payload = frame.get("payload", "")

        if src_host not in self.host_to_port:
            raise ValueError(f"Broadcast failed: Source host '{src_host}' is not connected to any active switch port.")

        src_port = self.host_to_port[src_host]
        
        successful_recipients = []
        excluded_ports = [src_port]
        
        # Deliver frame to all active ports except source port
        for p_num, h_id in self.ports.items():
            if p_num != src_port:
                successful_recipients.append({"host_id": h_id, "port": p_num})

        recipient_names = [r["host_id"] for r in successful_recipients]
        
        log_msg = (
            f"[BROADCAST EVENT] Src: {src_host} (Port-{src_port}) | Type: {frame_type} | Payload: '{payload}'\n"
            f"  --> Egress Ports Delivered ({len(successful_recipients)} hosts): {recipient_names}\n"
            f"  --> Ingress Source Port Excluded: Port-{src_port} ({src_host})"
        )
        self._log(log_msg)

        broadcast_summary = {
            "src_host": src_host,
            "src_port": src_port,
            "frame_type": frame_type,
            "payload": payload,
            "recipients": recipient_names,
            "recipient_count": len(recipient_names),
            "status": "SUCCESS"
        }
        return broadcast_summary

    def display_active_ports_table(self) -> str:
        """Generates formatted string showing current active port status."""
        lines = []
        lines.append("=" * 65)
        lines.append(f"            {self.switch_name} ACTIVE PORT STATUS TABLE")
        lines.append("=" * 65)
        lines.append(f"{'Port Number':<15} | {'Connected Host ID':<25} | {'Port Link State':<15}")
        lines.append("-" * 65)
        
        for p in range(1, min(12, self.total_ports) + 1):
            if p in self.ports:
                lines.append(f"Port-{p:<10} | {self.ports[p]:<25} | LINK_UP (Active)")
            else:
                lines.append(f"Port-{p:<10} | {'-- EMPTY --':<25} | LINK_DOWN (Idle)")
                
        lines.append("=" * 65)
        output_str = "\n".join(lines)
        return output_str

    def save_logs(self):
        """Saves execution history to log file."""
        os.makedirs(os.path.dirname(self.log_file), exist_ok=True)
        with open(self.log_file, "w") as f:
            f.write(f"=== {self.switch_name} BROADCAST & PORT OPERATION LOG ===\n\n")
            f.write("\n".join(self.log_history))
        print(f"[SUCCESS] Switch broadcast log saved to: {self.log_file}")


def plot_broadcast_demonstration(active_hosts: list, src_host: str, recipients: list, output_path: str = "Q5/star_switch_broadcast_chart.png"):
    """Generates visual graphic showing StarSwitch broadcast frame propagation."""
    plt.figure(figsize=(10, 8), dpi=300)
    ax = plt.gca()

    G = nx.Graph()
    switch_node = "StarSwitch_Core1"
    G.add_node(switch_node)

    for h in active_hosts:
        G.add_node(h)
        G.add_edge(switch_node, h)

    # Position in star layout
    pos = {switch_node: (0, 0)}
    import math
    radius = 4.0
    angle_step = 2 * math.pi / len(active_hosts)
    for idx, h in enumerate(active_hosts):
        angle = idx * angle_step
        pos[h] = (radius * math.cos(angle), radius * math.sin(angle))

    # Node Colors: Switch = Deep Blue, Source = Orange, Recipients = Green
    node_colors = []
    for node in G.nodes():
        if node == switch_node:
            node_colors.append("#003366")
        elif node == src_host:
            node_colors.append("#FF9800") # Source host
        else:
            node_colors.append("#2E7D32") # Recipient host

    nx.draw_networkx_nodes(G, pos, node_size=2500, node_color=node_colors, ax=ax)
    
    # Draw edges: Ingress edge (Source -> Switch) dashed blue, Egress edges (Switch -> Recipients) solid green
    for h in active_hosts:
        if h == src_host:
            nx.draw_networkx_edges(G, pos, edgelist=[(switch_node, h)], width=3.0, edge_color="#FF9800", style="dashed", ax=ax)
        else:
            nx.draw_networkx_edges(G, pos, edgelist=[(switch_node, h)], width=3.0, edge_color="#2E7D32", style="solid", ax=ax)

    nx.draw_networkx_labels(G, pos, font_color="white", font_weight="bold", font_size=9, ax=ax)

    plt.title(f"StarSwitch Broadcast Operation Demonstration\nSource: {src_host} (Ingress Port) ---> Flooded to all Recipients: {recipients}",
              fontsize=11, fontweight="bold", pad=15, color="#003366")
    
    # Custom Legend
    custom_lines = [
        plt.Line2D([0], [0], color="#003366", marker="o", linestyle="None", markersize=10, label="StarSwitch Core"),
        plt.Line2D([0], [0], color="#FF9800", marker="o", linestyle="None", markersize=10, label=f"Source Host ({src_host})"),
        plt.Line2D([0], [0], color="#2E7D32", marker="o", linestyle="None", markersize=10, label="Recipient Hosts (Flooded)"),
    ]
    plt.legend(handles=custom_lines, loc="lower right", facecolor="#F0F4F8")
    
    plt.axis("off")
    plt.tight_layout()
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.savefig(output_path, bbox_inches="tight", dpi=300)
    plt.close()
    print(f"[SUCCESS] Broadcast chart saved to: {output_path}")


def get_broadcasting_technical_explanation() -> str:
    return """================================================================================
TECHNICAL EXPLANATION: SIGNIFICANCE OF BROADCASTING IN ETHERNET COMMUNICATION
================================================================================
1. What is Ethernet Broadcasting?
   Broadcasting is a one-to-all transmission mechanism where a single Ethernet frame 
   sent to the MAC broadcast address (FF:FF:FF:FF:FF:FF) is delivered by the switch to 
   every active host in the Local Area Network (LAN) / Broadcast Domain, except the source port.

2. Essential Network Protocols Relying on Broadcasting:
   a) Address Resolution Protocol (ARP):
      When a host knows a target IP address (e.g. 192.168.1.50) but lacks its physical MAC 
      address, it broadcasts an "ARP Request" ("Who has 192.168.1.50? Tell 192.168.1.10"). 
      All hosts receive the request, but only the owner responds with a unicast ARP reply.
   b) Dynamic Host Configuration Protocol (DHCP):
      A newly connected host without an IP address broadcasts a DHCPDISCOVER message to 
      locate available DHCP servers on the local segment.
   c) Network Service & Topology Discovery:
      Protocols such as LLDP (Link Layer Discovery Protocol), NetBIOS, and router discovery 
      use broadcasts to advertise services and maintain network state.

3. Architectural Significance & Boundary Control:
   - Efficiency: Allows a host to discover network resources without prior knowledge of topology.
   - Isolation: Broadcast frames stay contained within Layer-2 boundaries (VLANs). Routers 
     (Layer 3) block Ethernet broadcast frames by default, preventing global network flooding.
================================================================================
"""

def main():
    print("=== CO4 AT1: QUESTION 5 - StarSwitch CLASS IMPLEMENTATION & DEMONSTRATION ===")
    
    # Instantiate StarSwitch
    switch = StarSwitch(switch_name="StarSwitch_Core1", total_ports=16, log_file="Q5/switch_broadcast_log.txt")
    
    # 1. Connect 5 Hosts
    print("\n--- STEP 1: Connecting Initial 5 Hosts ---")
    initial_hosts = ["Host_A", "Host_B", "Host_C", "Host_D", "Host_E"]
    for h in initial_hosts:
        switch.add_port(h)
        
    print("\n" + switch.display_active_ports_table())

    # 2. Perform Broadcast Operation 1 (ARP Request from Host_A)
    print("\n--- STEP 2: Executing Broadcast Frame 1 (ARP Request from Host_A) ---")
    frame1 = {
        "src_host": "Host_A",
        "frame_type": "ARP_REQUEST",
        "payload": "Who has IP 192.168.1.50? Tell Host_A"
    }
    b1_result = switch.broadcast(frame1)

    # 3. Disconnect Host_C
    print("\n--- STEP 3: Disconnecting Host_C from Switch ---")
    switch.remove_port("Host_C")
    print("\n" + switch.display_active_ports_table())

    # 4. Perform Broadcast Operation 2 (DHCP Discover from Host_B)
    print("\n--- STEP 4: Executing Broadcast Frame 2 (DHCP Discover from Host_B) ---")
    frame2 = {
        "src_host": "Host_B",
        "frame_type": "DHCP_DISCOVER",
        "payload": "DHCPDISCOVER: Requesting IP Lease"
    }
    b2_result = switch.broadcast(frame2)

    # 5. Add New Host Host_F
    print("\n--- STEP 5: Connecting New Host Host_F ---")
    switch.add_port("Host_F")
    print("\n" + switch.display_active_ports_table())

    # 6. Error Handling & Edge Cases Demonstration
    print("\n--- STEP 6: Edge Cases & Exception Handling Demonstration ---")
    
    # Edge Case A: Duplicate Host Add
    try:
        print("Attempting to add duplicate 'Host_A'...")
        switch.add_port("Host_A")
    except ValueError as e:
        print(f"  [EXPECTED ERROR trapped]: {e}")

    # Edge Case B: Remove Non-Existent Host
    try:
        print("Attempting to remove non-existent 'Host_Z'...")
        switch.remove_port("Host_Z")
    except KeyError as e:
        print(f"  [EXPECTED ERROR trapped]: {e}")

    # Edge Case C: Broadcast from Disconnected Host
    try:
        print("Attempting broadcast from disconnected 'Host_C'...")
        switch.broadcast({"src_host": "Host_C", "payload": "Orphan broadcast"})
    except ValueError as e:
        print(f"  [EXPECTED ERROR trapped]: {e}")

    # Save log file
    switch.save_logs()

    # Generate Chart plot
    active_now = list(switch.host_to_port.keys())
    plot_broadcast_demonstration(active_now, src_host="Host_B", recipients=b2_result["recipients"], output_path="Q5/star_switch_broadcast_chart.png")

    # Output Technical Explanation
    explanation = get_broadcasting_technical_explanation()
    print(explanation)
    with open("Q5/broadcasting_explanation.txt", "w") as f:
        f.write(explanation)

if __name__ == "__main__":
    main()
