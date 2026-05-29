"""
Solid-State Synthetic Jet Actuator - Phase 3.1
JAX-Accelerated Phased Array Beamforming Calculator

This script computes the precise microsecond time delays and phase shifts 
required for an 8x8 Uniform Rectangular Array (URA) to synthesize a focal 
point in 3D space. It is JIT-compiled for Apple Silicon optimization.
"""

import jax
import jax.numpy as jnp
from jax import jit
import matplotlib.pyplot as plt
import numpy as np

# ------------------------------------------------------------------
# 1. System Physical Constants
# ------------------------------------------------------------------
C0 = 343.0            # Speed of sound in air at 20C (m/s)
F0 = 40e3             # Center frequency of transducers (Hz)
OMEGA = 2 * jnp.pi * F0 # Angular frequency (rad/s)
PITCH = 10.5e-3       # Spacing between transducer centers (m)
N_X, N_Y = 8, 8       # Array dimensions

# ------------------------------------------------------------------
# 2. JIT-Compiled Core Math Engine
# ------------------------------------------------------------------
@jit
def compute_focal_laws(x_f, y_f, z_f, tx_x, tx_y):
    """
    Computes the time delays and phase shifts for the transducer array.
    JIT-compiled via XLA for near-instantaneous execution.
    """
    # Eq 1: L2 Norm distance from each transducer to the focal coordinate
    R = jnp.sqrt((tx_x - x_f)**2 + (tx_y - y_f)**2 + (0.0 - z_f)**2)
    
    # Eq 2: Time Delay calculation
    # The farthest element fires at t=0. Closer elements are delayed.
    R_max = jnp.max(R)
    delays = (R_max - R) / C0
    
    # Phase shifts in radians, bounded [0, 2pi)
    phase_shifts = jnp.mod(delays * OMEGA, 2.0 * jnp.pi)
    
    return delays, phase_shifts, R

# ------------------------------------------------------------------
# 3. Array Geometry Initialization
# ------------------------------------------------------------------
def generate_array_grid():
    """Generates the physical (X, Y) coordinates of the 8x8 array."""
    # Center the array at (0,0)
    x_coords = jnp.linspace(-(N_X-1)/2 * PITCH, (N_X-1)/2 * PITCH, N_X)
    y_coords = jnp.linspace(-(N_Y-1)/2 * PITCH, (N_Y-1)/2 * PITCH, N_Y)
    
    tx_x, tx_y = jnp.meshgrid(x_coords, y_coords)
    return tx_x, tx_y

# ------------------------------------------------------------------
# 4. Execution & Visualization
# ------------------------------------------------------------------
def main():
    print(f"[{jax.devices()[0].device_kind}] Initializing JAX Compute Engine...")
    
    tx_x, tx_y = generate_array_grid()
    
    # Define Target Focal Point (e.g., dead center, 5 cm above the board)
    focal_target = (0.0, 0.0, 0.05) 
    print(f"Target Focal Coordinate (X, Y, Z): {focal_target} meters")
    
    # Execute JIT-compiled function
    delays, phases, distances = compute_focal_laws(*focal_target, tx_x, tx_y)
    
    # Convert from JAX arrays to standard NumPy for printing/saving
    delays_us = np.array(delays) * 1e6  # Convert to microseconds
    phases_deg = np.degrees(np.array(phases))
    
    print("\n--- Time Delays (Microseconds) ---")
    print(np.round(delays_us, 1))
    
    # Save the output for ElmerFEM
    np.savetxt("math/python_scripts/phase_boundary_conditions.csv", 
               phases_deg, delimiter=",", fmt="%.2f", 
               header="Phase shifts (degrees) for ElmerFEM boundary conditions")
    print("\n[SUCCESS] Boundary conditions exported to phase_boundary_conditions.csv")

    # Plot the Phase Delay Profile (The "Acoustic Lens")
    plt.figure(figsize=(6, 5))
    plt.pcolormesh(tx_x * 1000, tx_y * 1000, delays_us, shading='auto', cmap='inferno')
    plt.colorbar(label='Firing Delay ($\mu s$)')
    plt.title('Array Firing Delays to Synthesize Focal Point')
    plt.xlabel('Array X (mm)')
    plt.ylabel('Array Y (mm)')
    plt.axis('equal')
    plt.tight_layout()
    plt.savefig('docs/delay_profile.png', dpi=300)
    print("[SUCCESS] Delay profile visualization saved to docs/delay_profile.png")

if __name__ == "__main__":
    main()