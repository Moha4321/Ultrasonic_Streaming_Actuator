"""
Solid-State Synthetic Jet Actuator - Phase 3.3
Lighthill-Nyborg Acoustic Streaming Force Extractor
"""

import pyvista as pv
import numpy as np
import pandas as pd
import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "../../"))
VTU_PATH = os.path.join(PROJECT_ROOT, "sim/ElmerFEM_Acoustics/mesh/acoustic_field_t0001.vtu")
OUT_PATH = os.path.join(PROJECT_ROOT, "sim/OpenFOAM_Fluid/acoustic_body_force.csv")

RHO_0 = 1.204        # Air density (kg/m^3)
C_0 = 343.0          # Speed of sound (m/s)
F_0 = 40e3           # Frequency (Hz)
OMEGA = 2 * np.pi * F_0

def main():
    print(f"Loading Acoustic Mesh from:\n{VTU_PATH}")
    if not os.path.exists(VTU_PATH):
        raise FileNotFoundError(f"Missing VTU file!")
        
    mesh = pv.read(VTU_PATH)
    keys = list(mesh.point_data.keys())
    print(f"Mesh loaded. Points: {mesh.n_points}. Available arrays: {keys}")

    # Dynamically extract pressure based on PyVista's naming convention
    if "pressure" in keys:
        p_data = mesh.point_data["pressure"]
        if len(p_data.shape) > 1:
            p_re = p_data[:, 0]
            p_im = p_data[:, 1]
        else:
            p_re = p_data
            p_im = np.zeros_like(p_re)
    elif "pressure 1" in keys or "Pressure 1" in keys:
        k1 = "pressure 1" if "pressure 1" in keys else "Pressure 1"
        k2 = "pressure 2" if "pressure 2" in keys else "Pressure 2"
        p_re = mesh.point_data[k1]
        p_im = mesh.point_data[k2]
    else:
        raise KeyError("Could not locate pressure field in VTU data.")

    # Save standardized names for the derivative engine
    mesh.point_data["P_Real"] = p_re
    mesh.point_data["P_Imag"] = p_im

    p_re_max = np.max(np.abs(p_re))
    print(f"Max Absolute Pressure (Real): {p_re_max:.2f} Pa")
    if p_re_max < 1e-10:
        print("\n[WARNING] The pressure field is completely ZERO.")
        sys.exit(1)

    print("Computing pressure spatial gradients (Nabla p)...")
    mesh = mesh.compute_derivative(scalars="P_Real")
    mesh.rename_array("gradient", "Grad_P_Real")
    
    mesh = mesh.compute_derivative(scalars="P_Imag")
    mesh.rename_array("gradient", "Grad_P_Imag")

    print("Computing first-order acoustic velocity vector field (u_1)...")
    grad_p_re = mesh.point_data["Grad_P_Real"]
    grad_p_im = mesh.point_data["Grad_P_Imag"]
    
    coeff = 1.0 / (OMEGA * RHO_0)
    u1_re = -coeff * grad_p_im
    u1_im =  coeff * grad_p_re

    print("Computing Acoustic Intensity (I) and Bulk Body Force (F_rad)...")
    # Intensity vector (W/m^2)
    Ix = 0.5 * (p_re * u1_re[:, 0] + p_im * u1_im[:, 0])
    Iy = 0.5 * (p_re * u1_re[:, 1] + p_im * u1_im[:, 1])
    Iz = 0.5 * (p_re * u1_re[:, 2] + p_im * u1_im[:, 2])
    
    alpha = 0.5 # Attenuation coefficient
    
    force_coeff = (2.0 * alpha) / C_0
    Fx = force_coeff * Ix
    Fy = force_coeff * Iy
    Fz = force_coeff * Iz
    
    print("Formatting force field for OpenFOAM fvOptions interpolation...")
    pts = mesh.points
    df = pd.DataFrame({
        'x': pts[:, 0],
        'y': pts[:, 1],
        'z': pts[:, 2],
        'Fx': Fx,
        'Fy': Fy,
        'Fz': Fz
    })
    
    df['F_mag'] = np.sqrt(df['Fx']**2 + df['Fy']**2 + df['Fz']**2)
    df_filtered = df[df['F_mag'] > 1e-4].copy()
    df_filtered.drop(columns=['F_mag'], inplace=True)
    
    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    df_filtered.to_csv(OUT_PATH, index=False)
    
    print(f"[SUCCESS] Extracted {len(df_filtered)} non-zero body force coordinates.")
    print(f"[SUCCESS] Exported Lighthill forcing term to: {OUT_PATH}")

if __name__ == "__main__":
    main()