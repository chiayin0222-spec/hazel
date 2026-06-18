import os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from utils.data_generator import generate_ring_dataset

def main():
    # 1. Generate concentric ring dataset with minimal noise for clean visualization
    X, y = generate_ring_dataset(
        n_inner=35, 
        n_outer=45, 
        inner_radius_range=(0.0, 1.0), 
        outer_radius_range=(1.6, 2.5), 
        noise=0.03, 
        random_seed=7
    )
    
    # Target Z mapping: z = x^2 + y^2
    Z_target = X[:, 0]**2 + X[:, 1]**2
    
    # 2. Setup Figure and 3D Axis
    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(1, 1, 1, projection='3d')
    fig.suptitle("SVM Kernel Trick: 2D Space to 3D Feature Space", fontsize=16, fontweight='bold')
    
    # Set axis limits
    ax.set_xlim(-3, 3)
    ax.set_ylim(-3, 3)
    ax.set_zlim(0, 8)
    ax.set_xlabel("Feature X")
    ax.set_ylabel("Feature Y")
    ax.set_zlabel("Mapped Z (x² + y²)")
    
    # Initialize scatter plots on z=0 plane
    # Class 0 (Inner, Blue) and Class 1 (Outer, Red)
    idx0 = (y == 0)
    idx1 = (y == 1)
    
    # Scatter plot data points initially flat on z = 0 plane
    scat0 = ax.scatter(
        X[idx0, 0], X[idx0, 1], np.zeros(np.sum(idx0)), 
        c='blue', edgecolors='k', s=50, label='Class 0 (Inner)', depthshade=False
    )
    scat1 = ax.scatter(
        X[idx1, 0], X[idx1, 1], np.zeros(np.sum(idx1)), 
        c='red', edgecolors='k', s=50, label='Class 1 (Outer)', depthshade=False
    )
    
    ax.legend(loc='upper left')
    
    # Initial camera view: flat 2D top-down (elevation=90, azimuth=-90)
    ax.view_init(elev=90, azim=-90)
    
    # 3. Create grid for drawing the paraboloid surface later
    r_grid = np.linspace(-2.8, 2.8, 40)
    xx, yy = np.meshgrid(r_grid, r_grid)
    zz_paraboloid = xx**2 + yy**2
    
    # Containers to keep track of plotted surfaces and boundaries
    surface_container = [None]
    hyperplane_container = [None]
    boundary_container = [None]
    
    # Add floating dynamic text box for stages
    text_box = ax.text2D(
        0.05, 0.95, "Stage 1: Non-linearly separable 2D Space", 
        transform=ax.transAxes, fontsize=12, fontweight='bold', 
        bbox=dict(facecolor='white', alpha=0.8, edgecolor='gray', boxstyle='round,pad=0.5')
    )
    text_container = [text_box]

    # Animation stages configuration:
    # Total frames: 160
    # Frames 0-30: Tilt camera (2D top-down to 3D perspective)
    # Frames 31-70: Lift data points (z goes from 0 to x^2 + y^2)
    # Frames 71-100: Render paraboloid surface (opacity increases)
    # Frames 101-130: Render separating hyperplane (opacity increases)
    # Frames 131-160: Camera rotation showing linear separation in 3D
    
    def update(frame):
        # Stage 1: Tilt camera
        if frame <= 30:
            t = frame / 30.0
            elev = 90 - t * 60  # 90 to 30
            azim = -90 + t * 45  # -90 to -45
            ax.view_init(elev=elev, azim=azim)
            text_container[0].set_text("Stage 1: Transitioning to 3D Perspective...")
            
        # Stage 2: Lift data points
        elif 30 < frame <= 70:
            t = (frame - 30) / 40.0
            z_curr0 = t * Z_target[idx0]
            z_curr1 = t * Z_target[idx1]
            
            # Update scatter data coordinates
            scat0._offsets3d = (X[idx0, 0], X[idx0, 1], z_curr0)
            scat1._offsets3d = (X[idx1, 0], X[idx1, 1], z_curr1)
            text_container[0].set_text("Stage 2: Mapped to 3D Feature Space (z = x² + y²)")
            
        # Stage 3: Render paraboloid surface
        elif 70 < frame <= 100:
            t = (frame - 70) / 30.0
            if surface_container[0] is not None:
                surface_container[0].remove()
            
            # Plot surface with increasing opacity
            surface_container[0] = ax.plot_surface(
                xx, yy, zz_paraboloid, 
                cmap=plt.cm.Blues, 
                alpha=t * 0.2, 
                edgecolor='none'
            )
            text_container[0].set_text("Stage 3: Revealing Mapping Surface (Paraboloid)")
            
        # Stage 4: Render separating hyperplane
        elif 100 < frame <= 130:
            t = (frame - 100) / 30.0
            if hyperplane_container[0] is not None:
                hyperplane_container[0].remove()
            if boundary_container[0] is not None:
                for line in boundary_container[0]:
                    line.remove()
                    
            # Hyperplane at z = 2.0
            zz_hyper = np.full_like(xx, 2.0)
            hyperplane_container[0] = ax.plot_surface(
                xx, yy, zz_hyper, 
                color='yellow', 
                alpha=t * 0.3, 
                edgecolor='none'
            )
            
            # Decision boundary projected back on z=0
            # Circle of radius sqrt(2.0)
            theta = np.linspace(0, 2 * np.pi, 100)
            x_circle = np.sqrt(2.0) * np.cos(theta)
            y_circle = np.sqrt(2.0) * np.sin(theta)
            z_circle = np.zeros_like(x_circle)
            
            # Plot decision boundary with increasing visibility
            boundary_container[0] = ax.plot(
                x_circle, y_circle, z_circle, 
                color='gold', 
                linewidth=2.5, 
                linestyle='-', 
                alpha=t
            )
            text_container[0].set_text("Stage 4: Placing Separating Hyperplane at z = 2.0\n& Projecting Boundary back to 2D")
            
        # Stage 5: Rotate camera for dynamic view
        elif 130 < frame <= 160:
            t = (frame - 130) / 30.0
            azim = -45 - t * 30  # -45 to -75
            ax.view_init(elev=30, azim=azim)
            text_container[0].set_text("Stage 5: Rotating camera to view clear separation...")
            
        return scat0, scat1
        
    # Create animation
    ani = animation.FuncAnimation(fig, update, frames=161, interval=50, blit=False)
    
    # Save the animation as a GIF
    os.makedirs("outputs", exist_ok=True)
    gif_path = os.path.join("outputs", "matplotlib_kernel_trick.gif")
    print("Rendering animation to GIF (this may take a few seconds)...")
    
    try:
        writer = animation.PillowWriter(fps=20)
        ani.save(gif_path, writer=writer)
        print(f"Animation saved successfully to: {gif_path}")
    except Exception as e:
        print(f"Failed to save GIF: {e}. Showing interactive animation instead.")
        
    plt.show()

if __name__ == "__main__":
    main()
