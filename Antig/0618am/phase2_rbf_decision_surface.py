import os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from utils.data_generator import generate_ring_dataset
from utils.svm_utils import train_svm, make_decision_grid, compute_decision_surface

def main():
    # 1. Generate concentric ring dataset with noise
    X, y = generate_ring_dataset(
        n_inner=35, 
        n_outer=45, 
        inner_radius_range=(0.0, 1.0), 
        outer_radius_range=(1.6, 2.5), 
        noise=0.08, 
        random_seed=7
    )
    
    # 2. Train a real SVC model with RBF kernel
    C_param = 10.0
    gamma_param = 1.0
    model = train_svm(X, y, kernel='rbf', C=C_param, gamma=gamma_param)
    
    # 3. Create grid and compute decision function surface
    grid_resolution = 100
    xx, yy, grid_points = make_decision_grid(X, resolution=grid_resolution, padding=0.5)
    Z = compute_decision_surface(model, grid_points, resolution=grid_resolution)
    
    # 4. Set up visualization
    fig = plt.figure(figsize=(15, 6))
    fig.suptitle(f"Real RBF SVM Decision Surface (C={C_param}, gamma={gamma_param})", fontsize=16)
    
    # --- SUBPLOT 1: 2D Decision Boundary ---
    ax1 = fig.add_subplot(1, 2, 1)
    ax1.set_title("2D Space with f(x, y) Contours")
    
    # Plot decision boundary contours
    # f(x,y)=0 is the boundary, f(x,y)=1 and -1 are the margins
    contour_fill = ax1.contourf(xx, yy, Z, levels=50, cmap=plt.cm.RdBu_r, alpha=0.3)
    cbar = fig.colorbar(contour_fill, ax=ax1, label="Decision Score f(x, y)")
    
    contour_lines = ax1.contour(
        xx, yy, Z, 
        levels=[-1.0, 0.0, 1.0], 
        colors=['darkred', 'yellow', 'darkblue'], 
        linestyles=['--', '-', '--'], 
        linewidths=[1.5, 2.5, 1.5]
    )
    ax1.clabel(contour_lines, inline=True, fontsize=10, fmt={-1.0: 'f = -1', 0.0: 'f = 0 (Boundary)', 1.0: 'f = +1'})
    
    # Scatter plot data points
    ax1.scatter(X[y == 0, 0], X[y == 0, 1], c='blue', edgecolors='k', label='Class 0 (Inner)', s=40)
    ax1.scatter(X[y == 1, 0], X[y == 1, 1], c='red', edgecolors='k', label='Class 1 (Outer)', s=40)
    
    # Highlight support vectors
    sv = model.support_vectors_
    ax1.scatter(
        sv[:, 0], sv[:, 1], 
        s=120, facecolors='none', edgecolors='yellow', 
        linewidths=1.5, label='Support Vectors'
    )
    
    ax1.set_xlabel("Feature X")
    ax1.set_ylabel("Feature Y")
    ax1.legend(loc='upper right')
    ax1.grid(True, linestyle=':', alpha=0.6)
    
    # --- SUBPLOT 2: 3D Decision Function Surface ---
    ax2 = fig.add_subplot(1, 2, 2, projection='3d')
    ax2.set_title("3D Space: z = f(x, y) Decision Surface")
    
    # Plot the decision function surface f(x, y)
    surf = ax2.plot_surface(
        xx, yy, Z, 
        cmap=plt.cm.RdBu_r, 
        alpha=0.5, 
        edgecolor='none', 
        rcount=50, ccount=50
    )
    
    # Draw reference z=0 plane
    z_zero = np.zeros_like(xx)
    ax2.plot_surface(
        xx, yy, z_zero, 
        color='yellow', 
        alpha=0.15, 
        edgecolor='none'
    )
    
    # Plot data points lifted to their actual decision score heights
    z_points = model.decision_function(X)
    ax2.scatter(
        X[y == 0, 0], X[y == 0, 1], z_points[y == 0], 
        c='blue', edgecolors='k', s=35, label='Class 0 (Inner)'
    )
    ax2.scatter(
        X[y == 1, 0], X[y == 1, 1], z_points[y == 1], 
        c='red', edgecolors='k', s=35, label='Class 1 (Outer)'
    )
    
    # Highlight support vectors in 3D
    sv_indices = model.support_
    ax2.scatter(
        X[sv_indices, 0], X[sv_indices, 1], z_points[sv_indices], 
        s=100, facecolors='none', edgecolors='yellow', 
        linewidths=1.8, depthshade=False, label='Support Vectors'
    )
    
    # Set labels
    ax2.set_xlabel("Feature X")
    ax2.set_ylabel("Feature Y")
    ax2.set_zlabel("Decision Score f(x, y)")
    ax2.view_init(elev=30, azim=-45)
    
    # Create outputs folder if it doesn't exist
    os.makedirs("outputs", exist_ok=True)
    
    # Save output plot
    output_path = os.path.join("outputs", "rbf_decision_surface.png")
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    print(f"Decision surface visualization saved successfully to: {output_path}")
    
    # Show the plot
    plt.show()

if __name__ == "__main__":
    main()
