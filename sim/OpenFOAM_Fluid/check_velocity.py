import math
import os

# Pointing to the FINAL frame of our animation
u_file = "sim/OpenFOAM_Fluid/0.05/U"

print("Parsing Final OpenFOAM Velocity Field (0.05/U)...")
with open(u_file, 'r') as f:
    lines = f.readlines()

start_idx, n_cells = 0, 0
for i, line in enumerate(lines):
    if "internalField" in line and "List<vector>" in line:
        n_cells = int(lines[i+1].strip())
        start_idx = i + 3
        break

max_vel = 0.0
for i in range(n_cells):
    val = lines[start_idx + i].strip().strip('()').split()
    ux, uy, uz = float(val[0]), float(val[1]), float(val[2])
    mag = math.sqrt(ux**2 + uy**2 + uz**2)
    if mag > max_vel:
        max_vel = mag

print(f"\n[SUCCESS] The Solid-State Actuator generated a maximum wind speed of: {max_vel:.4f} m/s")
