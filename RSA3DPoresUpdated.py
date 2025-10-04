import gmsh
import random
import numpy as np

# -----------------------------
# User-defined parameters
# -----------------------------
seed_value = 50             # random seed for reproducibility
random.seed(seed_value)
np.random.seed(seed_value)

# Initialize Gmsh
gmsh.initialize()
gmsh.model.add("cube_with_random_pores")

# Cube parameters
L = 1.0                    # cube size
boundary_offset = 0.01     # slightly bigger offset since pores are larger

# Pore parameters
target_porosity = 0.05     # 5% pore volume fraction
r_min, r_max = 0.03, 0.1  # min and max pore radius (larger pores)

# Create a cubic domain (1 x 1 x 1)
cube = gmsh.model.occ.addBox(0, 0, 0, L, L, L)

# Cube volume
cube_volume = L**3
target_pore_volume = target_porosity * cube_volume

# Function to generate a random pore (center + radius)
def generate_random_pore(existing_pores):
    while True:
        r = random.uniform(r_min, r_max)
        x = random.uniform(boundary_offset + r, L - boundary_offset - r)
        y = random.uniform(boundary_offset + r, L - boundary_offset - r)
        z = random.uniform(boundary_offset + r, L - boundary_offset - r)
        candidate = np.array([x, y, z])

        # Check overlap with existing pores
        if all(np.linalg.norm(candidate - center) > (r + radius)
               for center, radius in existing_pores):
            return candidate, r

# Generate pores until target volume is reached
pore_list = []  # stores (center, radius)
total_pore_volume = 0.0
sphere_tags = []

while total_pore_volume < target_pore_volume:
    center, r = generate_random_pore(pore_list)
    pore_list.append((center, r))
    total_pore_volume += (4.0/3.0) * np.pi * r**3

    # Create sphere and store its tag
    tag = gmsh.model.occ.addSphere(center[0], center[1], center[2], r)
    sphere_tags.append(tag)

print(f"Generated {len(pore_list)} pores, pore volume fraction = {total_pore_volume/cube_volume:.4f}")

# Subtract pores from the cube
sphere_entities = [(3, tag) for tag in sphere_tags]
gmsh.model.occ.cut([(3, cube)], sphere_entities, removeObject=True, removeTool=True)

# Synchronize before export
gmsh.model.occ.synchronize()

# Export to STEP file
gmsh.write("cube_with_5percent_pores_Huge_rmin_0_03_rmax_0_1.step")
print("STEP file saved: cube_with_random_pores_5percent_larger_Huge.step")

# Save pore centers and radii to a text file
with open("pore_centers_radii_5percent_larger_Huge.txt", "w") as f:
    for center, r in pore_list:
        f.write(f"{center[0]}, {center[1]}, {center[2]}, {r}\n")

print("Pore centers & radii saved to pore_centers_radii_5percent_larger_Huge.txt")

# Finalize Gmsh
gmsh.finalize()
