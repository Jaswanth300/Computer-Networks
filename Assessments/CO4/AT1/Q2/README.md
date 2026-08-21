# Question 2: IEEE 802.3 UTP Cable Segment Length Validator

## Overview
This module implements the `validate_segment(length_m)` function in Python to verify whether a given Unshielded Twisted Pair (UTP) cable segment length satisfies the IEEE 802.3 Ethernet standard (maximum 100 meters).

## Key Features
- **Function `validate_segment(length_m)`**: Takes a numeric length input and returns `(True, success_msg)` for valid segment lengths ($\le 100.0\text{m}$) and `(False, error_msg)` for lengths exceeding the 100m limit or invalid inputs.
- **Robust Error Handling**: Traps negative cable lengths, zero length, non-numeric data types (strings, booleans, None), and provides descriptive error messages.
- **Visual Compliance Plot**: Generates a bar chart comparing test cases against the 100m IEEE 802.3 threshold line (`cable_validation_plot.png`).
- **Technical IEEE 802.3 Analysis**: Explains the 90m horizontal + 10m patch cable breakdown, signal attenuation (insertion loss), propagation delay, and CSMA/CD slot time limits.

## Files Generated
- `q2_cable_validator.py`: Primary Python script containing function definition, test suite, and visual plotting logic.
- `test_execution_log.txt`: Recorded output log of all test case evaluations.
- `cable_validation_plot.png`: High-resolution graphical bar chart showing cable length compliance vs 100m IEEE limit.
- `ieee_802_3_analysis.txt`: Technical document detailing electrical and physical constraints behind the 100-meter rule.

## Test Results Summary
| Test Case | Input Length | Expected | Result | Message Summary |
|---|---|---|---|---|
| Case 1: Standard Valid | `50.0m` | Valid | `True` | Complies with IEEE 802.3 (Safety margin: 50.00m) |
| Case 2: Boundary Limit | `100.0m` | Valid | `True` | Complies with IEEE 802.3 (Safety margin: 0.00m) |
| Case 3: Exceeds Limit | `125.5m` | Invalid | `False` | Exceeds 100.0m limit by 25.50m |
| Case 4: Negative Length | `-15.0m` | Invalid | `False` | Must be a positive non-zero distance |
| Case 5: Invalid Type | `'one_hundred'` | Invalid | `False` | Must be a numeric value |

To execute Question 2:
```bash
python Q2/q2_cable_validator.py
```
