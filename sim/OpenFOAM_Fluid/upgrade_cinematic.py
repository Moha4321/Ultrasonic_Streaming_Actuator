import os

CASE_DIR = os.path.dirname(os.path.abspath(__file__))

def write_file(path, content):
    with open(path, 'w') as f:
        f.write(content)

# 1. High-Def Mesh (80x80x80 = 512,000 cells) -> Beautiful but fast!
blockMesh = """FoamFile { version 2.0; format ascii; class dictionary; object blockMeshDict; }
scale   1;
vertices ( (-0.05 -0.05 0.00) (0.05 -0.05 0.00) (0.05 0.05 0.00) (-0.05 0.05 0.00) (-0.05 -0.05 0.10) (0.05 -0.05 0.10) (0.05 0.05 0.10) (-0.05 0.05 0.10) );
blocks ( hex (0 1 2 3 4 5 6 7) (80 80 80) simpleGrading (1 1 1) );
edges ();
boundary (
    board_bottom { type wall; faces ( (0 3 2 1) ); }
    atmosphere { type patch; faces ( (4 5 6 7) (0 1 5 4) (1 2 6 5) (2 3 7 6) (3 0 4 7) ); }
);"""
write_file(os.path.join(CASE_DIR, "system/blockMeshDict"), blockMesh)

# 2. Perfect Animation Stepping: 100 Frames total!
controlDict = """FoamFile { version 2.0; format ascii; class dictionary; object controlDict; }
application     pimpleFoam;
startFrom       startTime;
startTime       0;
stopAt          endTime;
endTime         0.05; 
deltaT          0.0005;
adjustTimeStep  yes;
maxCo           0.95;
writeControl    adjustableRunTime;
writeInterval   0.0005; // SAVES A FRAME EVERY 0.0005 SECONDS
purgeWrite      0;
writeFormat     ascii;
writePrecision  6;
writeCompression off;
timeFormat      general;
timePrecision   6;
runTimeModifiable true;
"""
write_file(os.path.join(CASE_DIR, "system/controlDict"), controlDict)

# 3. Optimized Force Multiplier
with open(os.path.join(CASE_DIR, "map_force.py"), 'r') as f:
    script_data = f.read()

# Replace old multiplier with the optimized one
if "MEGA MULTIPLIER" in script_data:
    script_data = script_data.split(" * ")[0] + " * 50000.0 # OPTIMIZED MULTIPLIER\n"
else:
    script_data = script_data.replace("F_mapped = src_forces[indices]", "F_mapped = src_forces[indices] * 50000.0 # OPTIMIZED MULTIPLIER\n")

write_file(os.path.join(CASE_DIR, "map_force.py"), script_data)
print("[SUCCESS] Optimized 100-Frame Animation Case Generated.")
