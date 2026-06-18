import numpy as np

def generate_ring_dataset(
    n_inner=35, 
    n_outer=45, 
    inner_radius_range=(0.0, 1.0), 
    outer_radius_range=(1.6, 2.5), 
    noise=0.08, 
    random_seed=7
):
    """
    Generates a 2D dataset with two concentric circular classes (inner ring/cluster and outer ring).
    
    Parameters:
    -----------
    n_inner : int
        Number of points in the inner class.
    n_outer : int
        Number of points in the outer class.
    inner_radius_range : tuple of (float, float)
        Min and max radius for the inner class.
    outer_radius_range : tuple of (float, float)
        Min and max radius for the outer class.
    noise : float
        Standard deviation of Gaussian noise added to the points.
    random_seed : int
        Seed for reproducibility.
        
    Returns:
    --------
    X : np.ndarray of shape (n_inner + n_outer, 2)
        The 2D feature coordinates.
    y : np.ndarray of shape (n_inner + n_outer,)
        The labels (0 for inner, 1 for outer).
    """
    np.random.seed(random_seed)
    
    # Generate inner points
    r_inner = np.random.uniform(inner_radius_range[0], inner_radius_range[1], n_inner)
    theta_inner = np.random.uniform(0, 2 * np.pi, n_inner)
    X_inner = np.column_stack((r_inner * np.cos(theta_inner), r_inner * np.sin(theta_inner)))
    
    # Generate outer points
    r_outer = np.random.uniform(outer_radius_range[0], outer_radius_range[1], n_outer)
    theta_outer = np.random.uniform(0, 2 * np.pi, n_outer)
    X_outer = np.column_stack((r_outer * np.cos(theta_outer), r_outer * np.sin(theta_outer)))
    
    # Add noise
    X_inner += np.random.normal(0, noise, X_inner.shape)
    X_outer += np.random.normal(0, noise, X_outer.shape)
    
    # Combine
    X = np.vstack((X_inner, X_outer))
    y = np.concatenate((np.zeros(n_inner), np.ones(n_outer)))
    
    return X, y
