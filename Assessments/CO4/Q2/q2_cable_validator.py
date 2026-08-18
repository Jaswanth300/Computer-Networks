"""
Question 2: IEEE 802.3 UTP Cable Segment Length Validator
Course: Computer Networks (CSA07) - Assessment Tool 1 (CO4)

This script defines and demonstrates the `validate_segment(length_m)` function,
verifying whether UTP cable segment lengths comply with the IEEE 802.3 Ethernet standard
(maximum 100 meters). Includes test cases, error handling, visual compliance plotting,
and detailed technical interpretation.
"""

import os
import matplotlib.pyplot as plt

def validate_segment(length_m) -> tuple[bool, str]:
    """
    Verifies whether a given UTP cable segment length satisfies the IEEE 802.3 standard.
    
    Parameters:
        length_m (float or int): Cable length in meters.
        
    Returns:
        tuple[bool, str]: 
            - (True, Success message) for valid cable lengths (0 < length_m <= 100).
            - (False, Error message) for invalid lengths exceeding limit or non-physical inputs.
    """
    # Type validation
    if not isinstance(length_m, (int, float)) or isinstance(length_m, bool):
        return False, f"Invalid input type '{type(length_m).__name__}': Cable length must be a numeric value (int or float)."

    # Physical bounds check
    if length_m <= 0:
        return False, f"Invalid cable length ({length_m}m): Cable length must be a positive non-zero physical distance."

    # IEEE 802.3 Maximum Length Enforcement (100.0 Meters)
    MAX_IEEE_802_3_LENGTH = 100.0

    if length_m <= MAX_IEEE_802_3_LENGTH:
        margin = MAX_IEEE_802_3_LENGTH - length_m
        return True, f"VALID: Cable length {length_m:.2f}m complies with IEEE 802.3 standard (Safety margin: {margin:.2f}m)."
    else:
        excess = length_m - MAX_IEEE_802_3_LENGTH
        return False, f"ERROR: Cable length {length_m:.2f}m exceeds the IEEE 802.3 permissible limit of {MAX_IEEE_802_3_LENGTH:.1f}m by {excess:.2f}m."


def plot_cable_validation_results(test_data: list, output_path: str = "Q2/cable_validation_plot.png"):
    """
    Generates a visual bar chart comparing tested cable segment lengths 
    against the 100m IEEE 802.3 standard threshold line.
    """
    plt.figure(figsize=(10, 6), dpi=300)
    
    labels = []
    lengths = []
    colors = []
    
    for case_name, length_val, is_valid, msg in test_data:
        labels.append(case_name)
        if isinstance(length_val, (int, float)) and length_val > 0:
            lengths.append(length_val)
            colors.append("#2E7D32" if is_valid else "#C62828") # Green for valid, Red for invalid
        else:
            lengths.append(0)
            colors.append("#757575") # Grey for invalid/type errors

    bars = plt.bar(labels, lengths, color=colors, width=0.55, edgecolor="black", linewidth=1.2)
    
    # Draw IEEE 802.3 Max Limit Line (100m)
    plt.axhline(y=100.0, color="#1565C0", linestyle="--", linewidth=2.5, label="IEEE 802.3 Limit (100.0 m)")
    
    # Value annotations on bars
    for bar, length_val in zip(bars, lengths):
        height = bar.get_height()
        if height > 0:
            plt.text(bar.get_x() + bar.get_width()/2.0, height + 2, f"{length_val:.1f} m", 
                     ha="center", va="bottom", fontsize=9, fontweight="bold")
            
    plt.title("IEEE 802.3 UTP Cable Segment Length Compliance Verification", fontsize=12, fontweight="bold", pad=15, color="#003366")
    plt.xlabel("Test Scenarios", fontsize=10, fontweight="bold", labelpad=10)
    plt.ylabel("Cable Segment Length (Meters)", fontsize=10, fontweight="bold")
    plt.ylim(0, max(lengths + [110]) + 25)
    plt.grid(axis="y", linestyle=":", alpha=0.6)
    plt.legend(loc="upper right", frameon=True, facecolor="#F0F4F8")
    
    plt.tight_layout()
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.savefig(output_path, bbox_inches="tight", dpi=300)
    plt.close()
    print(f"[SUCCESS] Cable validation plot saved to: {output_path}")


def get_ieee_802_3_technical_analysis() -> str:
    return """================================================================================
TECHNICAL ANALYSIS: IEEE 802.3 ETHERNET UTP CABLE SEGMENT LIMITS (100m)
================================================================================
1. Standard Specification (IEEE 802.3 / TIA/EIA-568):
   The IEEE 802.3 standard strictly dictates a maximum channel length of 100 meters 
   (328 feet) for Unshielded Twisted Pair (UTP) cabling (Cat5e, Cat6, Cat6A) in Fast 
   Ethernet (100BASE-TX) and Gigabit Ethernet (1000BASE-T) deployments.

2. Cabling Breakdown:
   - Solid Horizontal Cabling (In-wall/Conduit): Maximum 90 meters (295 ft).
   - Patch Cords (Work area + Equipment room total): Maximum 10 meters (33 ft).
   - Total Channel Limit: 90m + 10m = 100 meters.

3. Physical & Electrical Constraints driving the 100m limit:
   a) Signal Attenuation (Insertion Loss): High-frequency electrical signals decay 
      as they travel along copper conductors. Beyond 100m, signal strength drops 
      below receiver detection sensitivity thresholds, causing bit errors (BER).
   b) Propagation Delay & CSMA/CD Slot Time: In shared Ethernet networks, collision 
      detection relies on a minimum frame size (64 bytes = 512 bits) being transmitted 
      long enough for signals to traverse the farthest network points and return. 
      Distances beyond 100m violate the 51.2 microsecond round-trip delay ceiling, 
      causing late collisions that go undetected.
   c) Near-End Crosstalk (NEXT) & Jitter: Increased length amplifies electromagnetic 
      interference between adjacent twisted pairs, degrading Signal-to-Noise Ratio (SNR).
================================================================================
"""

def main():
    print("=== CO4 AT1: QUESTION 2 - IEEE 802.3 UTP CABLE LENGTH VALIDATOR ===")
    
    # Defined Test Cases
    test_cases = [
        ("Case 1 (Standard Valid)", 50.0),
        ("Case 2 (Boundary Limit Valid)", 100.0),
        ("Case 3 (Exceeds Limit)", 125.5),
        ("Case 4 (Negative Length)", -15.0),
        ("Case 5 (Invalid Type)", "one_hundred")
    ]
    
    test_results_log = []
    plot_data = []

    print("\nExecuting Test Cases:\n" + "-" * 75)
    
    for case_name, length_val in test_cases:
        is_valid, msg = validate_segment(length_val)
        print(f"[{case_name}] Input: {repr(length_val)}")
        print(f"  Result: isValid = {is_valid}")
        print(f"  Message: {msg}")
        print("-" * 75)
        
        test_results_log.append(f"[{case_name}] Input: {repr(length_val)}\n  isValid: {is_valid}\n  Message: {msg}\n")
        plot_data.append((case_name, length_val, is_valid, msg))

    os.makedirs("Q2", exist_ok=True)
    
    # Save log report
    with open("Q2/test_execution_log.txt", "w") as f:
        f.write("=== Q2: UTP CABLE VALIDATION EXECUTION LOG ===\n\n")
        f.write("\n".join(test_results_log))
        
    # Generate compliance chart
    plot_cable_validation_results(plot_data, "Q2/cable_validation_plot.png")

    # Output technical analysis
    analysis = get_ieee_802_3_technical_analysis()
    print(analysis)
    with open("Q2/ieee_802_3_analysis.txt", "w") as f:
        f.write(analysis)

if __name__ == "__main__":
    main()
