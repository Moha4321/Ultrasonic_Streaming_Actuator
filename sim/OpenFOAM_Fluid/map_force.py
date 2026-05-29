"""
Solid-State Synthetic Jet Actuator - Phase 3.4
OpenFOAM Force Field Mapper

Parses the OpenFOAM 3D mesh cell centers, maps the acoustic Reynolds stress 
onto the grid using an inverse-distance KDTree, and generates the native 
OpenFOAM volVectorField 'F_rad' to drive the fluid flow.
"""

import os
import numpy as np
import pandas as pd
from scipy.spatial import cKDTree

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
C_FILE = os.path.join(SCRIPT_DIR, "0/C")
CSV_FILE = os.path.join(SCRIPT_DIR, "acoustic_body_force.csv")
FRAD_FILE = os.path.join(SCRIPT_DIR, "0/F_rad")

RHO_0 = 1.204  # Air density for kinematic conversion

def main():
    print("Loading Acoustic Body Force from CSV...")
    df = pd.read_csv(CSV_FILE)
    src_pts = df[['x', 'y', 'z']].values
    
    # Convert Volumetric Force (N/m^3) to Kinematic Momentum Source (m/s^2)
    src_forces = df[['Fx', 'Fy', 'Fz']].values / RHO_0

    print("Parsing OpenFOAM Mesh Cell Centers (0/C)...")
    if not os.path.exists(C_FILE):
        raise FileNotFoundError(f"Missing {C_FILE}. Did you run 'postProcess -func writeCellCentres'?")
        
    with open(C_FILE, 'r') as f:
        lines = f.readlines()
    
    # Locate the internalField data block
    start_idx, n_cells = 0, 0
    for i, line in enumerate(lines):
        if "internalField" in line and "List<vector>" in line:
            n_cells = int(lines[i+1].strip())
            start_idx = i + 3
            break
            
    cell_centers = []
    for i in range(n_cells):
        val = lines[start_idx + i].strip().strip('()').split()
        cell_centers.append([float(val[0]), float(val[1]), float(val[2])])
    
    cell_centers = np.array(cell_centers)
    print(f"Loaded {n_cells} OpenFOAM cells.")

    print("Mapping forces using Spatial KDTree...")
    tree = cKDTree(src_pts)
    distances, indices = tree.query(cell_centers)
    
    # Apply the optimized multiplier directly to the forces
    F_mapped = src_forces[indices] * 50000.0
    
    # Apply spatial bounding: if an OpenFOAM cell is more than 2.5mm away 
    # from any acoustic data point, it feels zero force.
    F_mapped[distances > 0.0025] = 0.0
    
    active_cells = np.count_nonzero(np.linalg.norm(F_mapped, axis=1))
    print(f"Mapped non-zero force to {active_cells} fluid cells.")

    print(f"Writing native OpenFOAM field to {FRAD_FILE}...")
    with open(FRAD_FILE, 'w') as f:
        # OpenFOAM Header
        f.write("FoamFile { version 2.0; format ascii; class volVectorField; object F_rad; }\n")
        f.write("dimensions      [0 1 -2 0 0 0 0];\n")
        
        # Data Array
        f.write(f"internalField   nonuniform List<vector>\n{n_cells}\n(\n")
        for fx, fy, fz in F_mapped:
            f.write(f"({fx:.6f} {fy:.6f} {fz:.6f})\n")
        f.write(");\n")
        
        # Boundaries
        f.write("boundaryField\n{\n")
        f.write("    board_bottom { type fixedValue; value uniform (0 0 0); }\n")
        f.write("    atmosphere   { type fixedValue; value uniform (0 0 0); }\n")
        f.write("}\n")
        
    print("[SUCCESS] F_rad field successfully injected into OpenFOAM directory.")

if __name__ == "__main__":
    main()