"""
Question 1: Star Topology Generator and Cable Connection Verifier
Course: Computer Networks (CSA07) - Assessment Tool 1 (CO4)

This script generates a Star Topology network for a given number of hosts connected 
to a central switch. It produces both ASCII art and high-resolution graphical 
visualizations, reports Cat6 UTP cable segment lengths, performs automated 
topology verification, and provides technical explanation on star topology reliability.
"""

import sys
import os
import math
import random
import matplotlib.pyplot as plt
import networkx as nx

class StarTopologyGenerator:
    """
    Class to model, visualize, and verify an Ethernet Star Topology.
    """
    def __init__(self, num_hosts: int, switch_name: str = "Switch_Central_SW1", max_switch_ports: int = 48):
        self.num_hosts = num_hosts
        self.switch_name = switch_name
        self.max_switch_ports = max_switch_ports
        self.hosts = []
        self.cable_lengths = {}
        self.graph = nx.Graph()
        
        self._validate_and_build()

    def _validate_and_build(self):
        """Validates host count and constructs the network graph."""
        if not isinstance(self.num_hosts, int):
            raise TypeError(f"Host count must be an integer, got {type(self.num_hosts).__name__}.")
        if self.num_hosts <= 0:
            raise ValueError(f"Host count must be a positive integer (> 0). Provided: {self.num_hosts}")
        if self.num_hosts > self.max_switch_ports:
            raise ValueError(f"Host count {self.num_hosts} exceeds maximum switch port capacity of {self.max_switch_ports}.")

        # Add central switch node
        self.graph.add_node(self.switch_name, type="switch", label=self.switch_name)

        # Generate hosts and assigned random compliant Cat6 UTP cable lengths (5.0m to 85.0m)
        random.seed(42) # Deterministic for reproducible test results
        for i in range(1, self.num_hosts + 1):
            host_label = f"Host_{i:02d}"
            self.hosts.append(host_label)
            # Cat6 UTP cable length between 5m and 85m
            cable_len = round(random.uniform(8.5, 75.0), 2)
            self.cable_lengths[host_label] = cable_len
            
            # Add host node and edge to switch
            self.graph.add_node(host_label, type="host", label=host_label)
            self.graph.add_edge(self.switch_name, host_label, length=cable_len, cable_type="Cat6 UTP")

    def display_ascii_topology(self) -> str:
        """Generates and returns a clean ASCII representation of the Star Topology."""
        lines = []
        lines.append("=" * 75)
        lines.append(f"          STAR TOPOLOGY ASCII REPRESENTATION ({self.switch_name})")
        lines.append("=" * 75)
        lines.append("")
        
        if self.num_hosts == 1:
            lines.append(f"  [ Host_01 ] <====== Cat6 UTP ({self.cable_lengths['Host_01']}m) ======> [ {self.switch_name} ]")
        else:
            mid = (self.num_hosts + 1) // 2
            top_hosts = self.hosts[:mid]
            bot_hosts = self.hosts[mid:]
            
            lines.append("  Top Hosts:")
            for idx, h in enumerate(top_hosts):
                lines.append(f"    Port {idx+1:02d} | [{h}] ---- Cat6 ({self.cable_lengths[h]}m) ----\\")
            
            lines.append(f"                                                    +---> [[ {self.switch_name} ]]")
            
            lines.append("  Bottom Hosts:")
            for idx, h in enumerate(bot_hosts, start=mid+1):
                lines.append(f"    Port {idx:02d} | [{h}] ---- Cat6 ({self.cable_lengths[h]}m) ----/")
                
        lines.append("")
        lines.append("-" * 75)
        lines.append(f"Host Connection Table:")
        lines.append(f"{'Host Label':<15} | {'Central Switch':<22} | {'Media Type':<12} | {'Cable Length (m)':<15}")
        lines.append("-" * 75)
        for h in self.hosts:
            lines.append(f"{h:<15} | {self.switch_name:<22} | {'Cat6 UTP':<12} | {self.cable_lengths[h]:<15.2f}")
        lines.append("=" * 75)
        
        output_str = "\n".join(lines)
        return output_str

    def generate_graphical_topology(self, output_path: str = "Q1/star_topology_graph.png"):
        """Generates a high-resolution graphical layout using NetworkX and Matplotlib."""
        plt.figure(figsize=(10, 8), dpi=300)
        ax = plt.gca()
        
        # Position nodes in a star formation around central switch
        pos = {}
        pos[self.switch_name] = (0, 0)
        
        radius = 5.0
        angle_step = 2 * math.pi / self.num_hosts
        for idx, h in enumerate(self.hosts):
            angle = idx * angle_step
            pos[h] = (radius * math.cos(angle), radius * math.sin(angle))
            
        # Draw central switch node
        nx.draw_networkx_nodes(
            self.graph, pos,
            nodelist=[self.switch_name],
            node_color="#003366",
            node_shape="s",
            node_size=3500,
            ax=ax,
            label="Central Switch"
        )
        
        # Draw host nodes
        nx.draw_networkx_nodes(
            self.graph, pos,
            nodelist=self.hosts,
            node_color="#008080",
            node_shape="o",
            node_size=2200,
            ax=ax,
            label="LAN Hosts"
        )
        
        # Draw edges (Cat6 UTP cabling)
        nx.draw_networkx_edges(
            self.graph, pos,
            width=2.5,
            edge_color="#555555",
            style="solid",
            ax=ax
        )
        
        # Node labels
        nx.draw_networkx_labels(
            self.graph, pos,
            labels={self.switch_name: f"{self.switch_name}\n(Central Switch)"},
            font_size=10,
            font_color="white",
            font_weight="bold",
            ax=ax
        )
        
        nx.draw_networkx_labels(
            self.graph, pos,
            labels={h: h for h in self.hosts},
            font_size=9,
            font_color="white",
            font_weight="bold",
            ax=ax
        )
        
        # Edge labels showing Cat6 UTP cable length
        edge_labels = {(self.switch_name, h): f"{self.cable_lengths[h]} m\n(Cat6)" for h in self.hosts}
        nx.draw_networkx_edge_labels(
            self.graph, pos,
            edge_labels=edge_labels,
            font_size=8,
            font_color="#880000",
            bbox=dict(boxstyle="round,pad=0.3", fc="#F0F4F8", ec="#003366", lw=1),
            ax=ax
        )
        
        plt.title(f"Ethernet Star Topology ({self.num_hosts} Hosts connected to {self.switch_name})\nCable Standard: Cat6 UTP (IEEE 802.3 Max 100m)",
                  fontsize=12, fontweight="bold", pad=15, color="#003366")
        plt.axis("off")
        plt.tight_layout()
        plt.savefig(output_path, bbox_inches="tight", dpi=300)
        plt.close()
        print(f"[SUCCESS] Graphical star topology saved to: {output_path}")

    def verify_topology(self) -> dict:
        """
        Verifies that:
        1. All hosts are connected exclusively to the central switch.
        2. Central switch degree equals number of hosts.
        3. No host-to-host direct link exists.
        4. Cable lengths are within IEEE 802.3 standards (<= 100m).
        """
        verification = {
            "is_valid_star": True,
            "total_hosts": len(self.hosts),
            "central_switch": self.switch_name,
            "switch_degree": self.graph.degree(self.switch_name),
            "direct_inter_host_links": 0,
            "compliant_cable_segments": 0,
            "non_compliant_segments": 0,
            "details": []
        }

        # Check switch connections
        if verification["switch_degree"] != self.num_hosts:
            verification["is_valid_star"] = False
            verification["details"].append(f"Switch degree mismatch: Expected {self.num_hosts}, got {verification['switch_degree']}.")

        # Check host links and cable lengths
        for h in self.hosts:
            neighbors = list(self.graph.neighbors(h))
            if len(neighbors) != 1 or neighbors[0] != self.switch_name:
                verification["is_valid_star"] = False
                verification["details"].append(f"{h} has invalid neighbor connections: {neighbors}")

            length = self.cable_lengths[h]
            if length <= 100.0:
                verification["compliant_cable_segments"] += 1
            else:
                verification["non_compliant_segments"] += 1
                verification["is_valid_star"] = False
                verification["details"].append(f"{h} cable length ({length}m) exceeds IEEE 802.3 100m limit.")

        if verification["is_valid_star"]:
            verification["details"].append("All verification checks PASSED! Valid Star Topology connected through Central Switch.")

        return verification

def get_star_topology_explanation() -> str:
    return """================================================================================
TECHNICAL EXPLANATION: STAR TOPOLOGY AND RELIABLE COMMUNICATION IN LANS
================================================================================
1. Centralized Switch Architecture:
   In a star topology, each end host (PC, server, printer) connects directly to 
   a central Ethernet switch via a dedicated point-to-point Cat6 UTP cable link. 
   All data frames transmitted between hosts must travel through the central switch.

2. Fault Isolation & High Reliability:
   If a Cat6 cable segment breaks or a host network card fails, only that specific 
   connection is interrupted. The remaining hosts and network segments continue 
   operating without downtime. This contrasts sharply with legacy Bus topologies, 
   where a single cable fault brings down the entire network.

3. Micro-segmentation & Dedicated Bandwidth:
   Modern Ethernet star networks use intelligent switches rather than passive hubs. 
   Each switch port represents an isolated collision domain. With Full-Duplex 
   Cat6 cabling, hosts can send and receive data simultaneously at speeds up to 10 Gbps 
   without transmission collisions.

4. Ease of Troubleshooting & Maintenance:
   Centralized layout simplifies diagnostics. Network administrators can monitor 
   and manage all connections from a single central switch, disabling broken ports 
   or upgrading cabling (e.g., Cat6 UTP) without altering overall network topology.
================================================================================
"""

def main():
    print("=== CO4 AT1: QUESTION 1 - STAR TOPOLOGY GENERATOR & VERIFIER ===")
    
    # Test Case 1: Standard 6-Host Network
    print("\n--- TEST CASE 1: Standard 6-Host Star Topology ---")
    topology = StarTopologyGenerator(num_hosts=6, switch_name="Switch_Central_SW1")
    
    # Print ASCII Topology
    ascii_out = topology.display_ascii_topology()
    print(ascii_out)
    
    # Ensure Q1 directory exists
    os.makedirs("Q1", exist_ok=True)

    # Save ASCII topology to text file in Q1 directory
    with open("Q1/ascii_topology.txt", "w") as f:
        f.write(ascii_out)
        
    # Generate Graphical PNG
    topology.generate_graphical_topology("Q1/star_topology_graph.png")
    
    # Run Verification
    res = topology.verify_topology()
    print("\nVerification Results:")
    for k, v in res.items():
        print(f"  {k}: {v}")

    # Output Technical Explanation
    explanation = get_star_topology_explanation()
    print(explanation)
    with open("Q1/star_topology_explanation.txt", "w") as f:
        f.write(explanation)

    # Edge Case Testing
    print("\n--- TEST CASE 2: Edge Case & Error Handling Demonstration ---")
    invalid_cases = [0, -4, 64, "invalid_num"]
    for val in invalid_cases:
        try:
            print(f"Attempting to create Star Topology with hosts={val}...")
            StarTopologyGenerator(num_hosts=val)
        except Exception as e:
            print(f"  [CAUGHT EXPECTED ERROR]: {type(e).__name__} -> {e}")

if __name__ == "__main__":
    main()
