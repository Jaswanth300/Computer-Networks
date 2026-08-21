"""
Question 4: Client-Server Socket Simulation of Ethernet Switch MAC Learning & Frame Forwarding
Course: Computer Networks (CSA07) - Assessment Tool 1 (CO4)

This script uses Python's standard `socket` library to implement a central switch server
and host clients. The switch server receives Ethernet frames over TCP sockets, learns
source MAC addresses, updates a simulated MAC Address Table, forwards frames appropriately
(Unicast vs Flood), logs MAC table state to file, and generates a visual summary.
"""

import socket
import json
import threading
import time
import os
import matplotlib.pyplot as plt

class SwitchServer:
    """
    Simulates a Layer-2 Ethernet Central Switch running a TCP Socket Server.
    Learns MAC addresses and forwards frames based on MAC Table lookups.
    """
    def __init__(self, host: str = "127.0.0.1", port: int = 8888, log_file: str = "Q4/mac_table_log.txt"):
        self.host = host
        self.port = port
        self.log_file = log_file
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        self.mac_table = {}  # { mac_address: {"port": port_num, "learned_time": timestamp, "socket": client_sock} }
        self.port_sockets = {}  # { port_num: (client_sock, addr) }
        self.socket_ports = {}  # { client_sock: port_num }
        self.port_counter = 1
        
        self.is_running = False
        self.log_entries = []
        self.lock = threading.Lock()

    def log(self, message: str):
        timestamp_str = time.strftime("[%H:%M:%S]")
        entry = f"{timestamp_str} {message}"
        self.log_entries.append(entry)
        print(entry)

    def display_and_log_mac_table(self):
        """Displays and logs the current MAC Address Table state."""
        lines = []
        lines.append("=" * 70)
        lines.append("                UPDATED ETHERNET SWITCH MAC ADDRESS TABLE")
        lines.append("=" * 70)
        lines.append(f"{'Port Number':<12} | {'MAC Address':<20} | {'Learned Time':<12} | {'Status':<12}")
        lines.append("-" * 70)
        
        if not self.mac_table:
            lines.append("  [EMPTY] No MAC addresses learned yet.")
        else:
            for mac, info in self.mac_table.items():
                lines.append(f"Port-{info['port']:<7} | {mac:<20} | {info['learned_time']:<12} | DYNAMIC")
                
        lines.append("=" * 70)
        output_str = "\n".join(lines)
        print("\n" + output_str + "\n")
        self.log_entries.append(output_str)

    def start_server(self):
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)
        self.is_running = True
        self.log(f"[SWITCH SERVER INITIALIZED] Listening on {self.host}:{self.port}")
        
        server_thread = threading.Thread(target=self._accept_clients, daemon=True)
        server_thread.start()

    def _accept_clients(self):
        while self.is_running:
            try:
                client_sock, addr = self.server_socket.accept()
                with self.lock:
                    port_num = self.port_counter
                    self.port_counter += 1
                    self.port_sockets[port_num] = (client_sock, addr)
                    self.socket_ports[client_sock] = port_num
                    
                self.log(f"[PORT CONNECTED] Host connected on Switch Port-{port_num} from IP/Port {addr}")
                
                client_handler = threading.Thread(target=self._handle_client_frame, args=(client_sock, port_num), daemon=True)
                client_handler.start()
            except Exception:
                break

    def _handle_client_frame(self, client_sock: socket.socket, port_num: int):
        while self.is_running:
            try:
                data = client_sock.recv(4096)
                if not data:
                    break
                
                frame = json.loads(data.decode('utf-8'))
                src_mac = frame.get("src_mac")
                dst_mac = frame.get("dst_mac")
                payload = frame.get("payload")

                self.log(f"[FRAME RECEIVED] Port-{port_num} | Src: {src_mac} -> Dst: {dst_mac} | Payload: '{payload}'")

                # Step 1: MAC Address Self-Learning
                with self.lock:
                    current_time_str = time.strftime("%H:%M:%S")
                    if src_mac not in self.mac_table or self.mac_table[src_mac]["port"] != port_num:
                        self.mac_table[src_mac] = {
                            "port": port_num,
                            "learned_time": current_time_str,
                            "socket": client_sock
                        }
                        self.log(f"[MAC LEARNED] Port-{port_num} updated with MAC: {src_mac}")
                
                # Display updated MAC table after learning
                self.display_and_log_mac_table()

                # Step 2: Frame Forwarding Decision
                with self.lock:
                    if dst_mac == "FF:FF:FF:FF:FF:FF":
                        # Broadcast Frame
                        self.log(f"[FORWARDING DECISION] Broadcast Frame (FF:FF:FF:FF:FF:FF). Flooding to all ports except Port-{port_num}.")
                        self._flood_frame(frame, egress_skip_port=port_num)
                    elif dst_mac in self.mac_table:
                        # Known Unicast Forwarding
                        dst_port = self.mac_table[dst_mac]["port"]
                        dst_sock = self.mac_table[dst_mac]["socket"]
                        self.log(f"[FORWARDING DECISION] Known Unicast. Forwarding frame directly out Port-{dst_port} to {dst_mac}.")
                        try:
                            dst_sock.sendall(json.dumps(frame).encode('utf-8'))
                        except Exception as e:
                            self.log(f"[ERROR] Failed to forward to Port-{dst_port}: {e}")
                    else:
                        # Unknown Unicast Flooding
                        self.log(f"[FORWARDING DECISION] Unknown Unicast ({dst_mac} not in MAC table). Flooding frame out all active ports except Port-{port_num}.")
                        self._flood_frame(frame, egress_skip_port=port_num)

            except (ConnectionResetError, json.JSONDecodeError):
                break

        # Handle disconnect
        with self.lock:
            self.log(f"[PORT DISCONNECTED] Host on Port-{port_num} disconnected.")

    def _flood_frame(self, frame: dict, egress_skip_port: int):
        data = json.dumps(frame).encode('utf-8')
        for p_num, (sock, _) in self.port_sockets.items():
            if p_num != egress_skip_port:
                try:
                    sock.sendall(data)
                except Exception:
                    pass

    def stop_server(self):
        self.is_running = False
        self.server_socket.close()
        # Write log file
        os.makedirs(os.path.dirname(self.log_file), exist_ok=True)
        with open(self.log_file, "w") as f:
            f.write("\n".join(self.log_entries))
        print(f"[SUCCESS] Switch MAC log written to: {self.log_file}")


class HostClient:
    """
    Simulates a network host connected to the Ethernet Switch server via socket.
    """
    def __init__(self, mac_address: str, host_name: str, server_host: str = "127.0.0.1", server_port: int = 8888):
        self.mac_address = mac_address
        self.host_name = host_name
        self.server_host = server_host
        self.server_port = server_port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.received_frames = []
        self.is_listening = False

    def connect(self):
        self.sock.connect((self.server_host, self.server_port))
        self.is_listening = True
        listen_thread = threading.Thread(target=self._listen_for_frames, daemon=True)
        listen_thread.start()

    def _listen_for_frames(self):
        while self.is_listening:
            try:
                data = self.sock.recv(4096)
                if not data:
                    break
                frame = json.loads(data.decode('utf-8'))
                self.received_frames.append(frame)
                print(f"  --> [{self.host_name} ({self.mac_address})] RECEIVED FRAME: From {frame['src_mac']} | Payload: '{frame['payload']}'")
            except Exception:
                break

    def send_frame(self, dst_mac: str, payload: str):
        frame = {
            "src_mac": self.mac_address,
            "dst_mac": dst_mac,
            "payload": payload
        }
        self.sock.sendall(json.dumps(frame).encode('utf-8'))

    def disconnect(self):
        self.is_listening = False
        self.sock.close()


def plot_mac_table_summary(mac_table_records: list, output_path: str = "Q4/mac_learning_table_chart.png"):
    """Generates a graphic visualization of MAC learning progression table."""
    plt.figure(figsize=(9, 5), dpi=300)
    ax = plt.gca()
    ax.axis("off")
    
    col_labels = ["Switch Port", "Learned MAC Address", "Connected Host", "Learning Mode"]
    table_data = []
    for rec in mac_table_records:
        table_data.append([f"Port {rec['port']}", rec["mac"], rec["host"], "Dynamic (Self-Learned)"])
        
    table = plt.table(cellText=table_data, colLabels=col_labels, loc="center", cellLoc="center")
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1.2, 2.0)

    # Style table header and cells
    for (row, col), cell in table.get_celld().items():
        if row == 0:
            cell.set_facecolor("#003366")
            cell.set_text_props(color="white", fontweight="bold")
        else:
            cell.set_facecolor("#F0F4F8" if row % 2 == 0 else "#FFFFFF")

    plt.title("Ethernet Switch MAC Address Table - Learned Dynamic Entries", 
              fontsize=12, fontweight="bold", pad=20, color="#003366")
    plt.tight_layout()
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.savefig(output_path, bbox_inches="tight", dpi=300)
    plt.close()
    print(f"[SUCCESS] MAC table chart saved to: {output_path}")


def get_mac_learning_explanation() -> str:
    return """================================================================================
TECHNICAL EXPLANATION: MAC ADDRESS LEARNING AND FRAME FORWARDING IN SWITCHES
================================================================================
1. The Role of the MAC Address Table:
   An Ethernet switch maintains a hardware CAM (Content Addressable Memory) table, 
   commonly called the MAC Address Table. It maps destination MAC addresses to specific 
   ingress/egress physical switch ports.

2. Source MAC Address Self-Learning:
   When an Ethernet frame enters any switch port:
   - The switch examines the SOURCE MAC address in the frame header.
   - If the Source MAC is not in the table, the switch creates a new dynamic entry 
     associating that MAC address with the receiving port and timestamps it.
   - If the MAC address already exists on that port, its aging timer is reset. 
     If it moved to a new port, the table entry is updated.

3. Frame Forwarding Decisions (Unicast vs Broadcast/Flood):
   After learning the source MAC, the switch inspects the DESTINATION MAC address:
   a) Known Unicast Forwarding: If the Destination MAC is present in the table, the 
      switch forwards the frame ONLY out the specific associated egress port (micro-segmentation).
   b) Unknown Unicast Flooding: If the Destination MAC is NOT in the table, the switch 
      floods the frame out all active ports EXCEPT the port on which it was received.
   c) Broadcast Forwarding: If Destination MAC is FF:FF:FF:FF:FF:FF, the frame is flooded 
      to all active ports (except source port).

4. Bandwidth Optimization:
   By learning MAC addresses, switches eliminate collisions and prevent unnecessary 
   traffic flooding, ensuring dedicated full-duplex bandwidth to each connected host.
================================================================================
"""

def main():
    print("=== CO4 AT1: QUESTION 4 - CLIENT-SERVER SOCKET MAC SWITCH SIMULATION ===")
    
    # Start Central Switch Server
    switch = SwitchServer(host="127.0.0.1", port=8888, log_file="Q4/mac_table_log.txt")
    switch.start_server()
    time.sleep(0.5)

    # Initialize 3 Hosts
    host1 = HostClient(mac_address="00:11:22:33:44:A1", host_name="Host_1")
    host2 = HostClient(mac_address="00:11:22:33:44:B2", host_name="Host_2")
    host3 = HostClient(mac_address="00:11:22:33:44:C3", host_name="Host_3")

    print("\nConnecting Hosts to Switch Ports...")
    host1.connect()
    time.sleep(0.3)
    host2.connect()
    time.sleep(0.3)
    host3.connect()
    time.sleep(0.5)

    print("\n--- STAGE 1: Frame Transmission 1 (Host_1 -> Host_2) [Unknown Unicast Flood & Learn Host_1] ---")
    host1.send_frame(dst_mac="00:11:22:33:44:B2", payload="Hello Host_2! This is frame 1 from Host_1.")
    time.sleep(1.0)

    print("\n--- STAGE 2: Frame Transmission 2 (Host_2 -> Host_1) [Known Unicast & Learn Host_2] ---")
    host2.send_frame(dst_mac="00:11:22:33:44:A1", payload="Reply from Host_2 to Host_1 received!")
    time.sleep(1.0)

    print("\n--- STAGE 3: Frame Transmission 3 (Host_3 -> Broadcast) [Broadcast Flood & Learn Host_3] ---")
    host3.send_frame(dst_mac="FF:FF:FF:FF:FF:FF", payload="ARP Broadcast Discovery request from Host_3.")
    time.sleep(1.0)

    # Clean disconnect hosts
    host1.disconnect()
    host2.disconnect()
    host3.disconnect()
    time.sleep(0.5)

    # Stop switch server & write logs
    switch.stop_server()

    # Generate Chart plot
    mac_records = [
        {"port": 1, "mac": "00:11:22:33:44:A1", "host": "Host_1"},
        {"port": 2, "mac": "00:11:22:33:44:B2", "host": "Host_2"},
        {"port": 3, "mac": "00:11:22:33:44:C3", "host": "Host_3"}
    ]
    plot_mac_table_summary(mac_records, "Q4/mac_learning_table_chart.png")

    # Output Technical Explanation
    explanation = get_mac_learning_explanation()
    print(explanation)
    with open("Q4/mac_learning_explanation.txt", "w") as f:
        f.write(explanation)

if __name__ == "__main__":
    main()
