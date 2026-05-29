"""
Solid-State Synthetic Jet Actuator - Phase 3.4
OpenFOAM Case Generator

This script programmatically generates the required OpenFOAM dictionary files 
for a transient incompressible Navier-Stokes simulation (pimpleFoam), including 
a dynamically compiled C++ fvOption to inject the acoustic streaming force.
"""

import os

CASE_DIR = os.path.dirname(os.path.abspath(__file__))

def write_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w') as f:
        f.write(content)

def main():
    print("Generating OpenFOAM Case Structure...")

    # 1. blockMeshDict (The 3D Grid: 10cm x 10cm x 10cm, ~125,000 cells)
    blockMesh = """/*--------------------------------*- C++ -*----------------------------------*\\
| =========                 |                                                 |
| \\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox           |
|  \\    /   O peration     | Version:  v2312 (or compatible)                 |
|   \\  /    A nd           | Website:  www.openfoam.com                      |
|    \\/     M anipulation  |                                                 |
\\*---------------------------------------------------------------------------*/
FoamFile { version 2.0; format ascii; class dictionary; object blockMeshDict; }

scale   1;
vertices
(
    (-0.05 -0.05  0.00) ( 0.05 -0.05  0.00) ( 0.05  0.05  0.00) (-0.05  0.05  0.00)
    (-0.05 -0.05  0.10) ( 0.05 -0.05  0.10) ( 0.05  0.05  0.10) (-0.05  0.05  0.10)
);

blocks
(
    hex (0 1 2 3 4 5 6 7) (50 50 50) simpleGrading (1 1 1)
);

edges ();

boundary
(
    board_bottom
    {
        type wall;
        faces ( (0 3 2 1) );
    }
    atmosphere
    {
        type patch;
        faces ( (4 5 6 7) (0 1 5 4) (1 2 6 5) (2 3 7 6) (3 0 4 7) );
    }
);
"""
    write_file(os.path.join(CASE_DIR, "system/blockMeshDict"), blockMesh)

    # 2. controlDict (Simulation Settings)
    controlDict = """FoamFile { version 2.0; format ascii; class dictionary; object controlDict; }
application     pimpleFoam;
startFrom       startTime;
startTime       0;
stopAt          endTime;
endTime         0.2; // Simulate 0.2 seconds of real time
deltaT          0.001;
writeControl    timeStep;
writeInterval   10;
purgeWrite      0;
writeFormat     ascii;
writePrecision  6;
writeCompression off;
timeFormat      general;
timePrecision   6;
runTimeModifiable true;
"""
    write_file(os.path.join(CASE_DIR, "system/controlDict"), controlDict)

    # 3. fvOptions (The C++ Injection of the Lighthill Force)
    fvOptions = """FoamFile { version 2.0; format ascii; class dictionary; object fvOptions; }
momentumSource
{
    type            coded;
    selectionMode   all;
    name            acousticStreamingForce;
    
    codeAddSup
    #{
        // Look up the F_rad field we will generate via Python and add it to the Navier-Stokes momentum equation
        const volVectorField& F_rad = mesh().lookupObject<volVectorField>("F_rad");
        eqn += F_rad;
    #};
}
"""
    write_file(os.path.join(CASE_DIR, "system/fvOptions"), fvOptions)

    # 4. fvSchemes & fvSolution (Math Solvers)
    # Keeping it minimal but highly stable for incompressible transient flow
    fvSchemes = """FoamFile { version 2.0; format ascii; class dictionary; object fvSchemes; }
ddtSchemes { default Euler; }
gradSchemes { default Gauss linear; }
divSchemes { default none; div(phi,U) Gauss linearUpwind grad(U); }
laplacianSchemes { default Gauss linear orthogonal; }
interpolationSchemes { default linear; }
snGradSchemes { default orthogonal; }
"""
    write_file(os.path.join(CASE_DIR, "system/fvSchemes"), fvSchemes)

    fvSolution = """FoamFile { version 2.0; format ascii; class dictionary; object fvSolution; }
solvers {
    p { solver PCG; preconditioner DIC; tolerance 1e-06; relTol 0.05; }
    pFinal { $p; relTol 0; }
    U { solver smoothSolver; smoother symGaussSeidel; tolerance 1e-05; relTol 0; }
}
PIMPLE { nOuterCorrectors 1; nCorrectors 2; nNonOrthogonalCorrectors 0; pRefCell 0; pRefValue 0; }
"""
    write_file(os.path.join(CASE_DIR, "system/fvSolution"), fvSolution)

    # 5. Fluid Properties (Air)
    transport = """FoamFile { version 2.0; format ascii; class dictionary; object transportProperties; }
transportModel  Newtonian;
nu              [0 2 -1 0 0 0 0] 1.5e-5; // Kinematic viscosity of air
"""
    write_file(os.path.join(CASE_DIR, "constant/transportProperties"), transport)

    # 6. Initial Conditions (U, p)
    U = """FoamFile { version 2.0; format ascii; class volVectorField; object U; }
dimensions      [0 1 -1 0 0 0 0];
internalField   uniform (0 0 0);
boundaryField
{
    board_bottom { type fixedValue; value uniform (0 0 0); }
    atmosphere   { type pressureInletOutletVelocity; value uniform (0 0 0); }
}
"""
    write_file(os.path.join(CASE_DIR, "0/U"), U)

    p = """FoamFile { version 2.0; format ascii; class volScalarField; object p; }
dimensions      [0 2 -2 0 0 0 0];
internalField   uniform 0;
boundaryField
{
    board_bottom { type zeroGradient; }
    atmosphere   { type totalPressure; p0 uniform 0; U U; phi phi; rho none; value uniform 0; }
}
"""
    write_file(os.path.join(CASE_DIR, "0/p"), p)

    print("[SUCCESS] OpenFOAM Dictionary Tree generated successfully in sim/OpenFOAM_Fluid/")

if __name__ == "__main__":
    main()