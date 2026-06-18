import numpy as np
from sklearn.svm import SVC

def train_svm(X, y, kernel='rbf', C=10.0, gamma=1.0, degree=3):
    """
    Trains a Support Vector Classifier (SVC) model.
    
    Parameters:
    -----------
    X : np.ndarray
        Training features of shape (n_samples, 2).
    y : np.ndarray
        Training labels of shape (n_samples,).
    kernel : str
        Specifies the kernel type ('linear', 'poly', 'rbf', 'sigmoid').
    C : float
        Regularization parameter.
    gamma : float or str
        Kernel coefficient for 'rbf', 'poly', and 'sigmoid'.
    degree : int
        Degree of the polynomial kernel function ('poly').
        
    Returns:
    --------
    model : sklearn.svm.SVC
        The trained SVM model.
    """
    model = SVC(kernel=kernel, C=C, gamma=gamma, degree=degree, random_state=42)
    model.fit(X, y)
    return model

def make_decision_grid(X, resolution=100, padding=0.5):
    """
    Generates a 2D grid based on the bounds of input features X.
    
    Parameters:
    -----------
    X : np.ndarray
        Features of shape (n_samples, 2).
    resolution : int
        Number of grid points along each dimension.
    padding : float
        Amount of padding to add beyond the min/max of X.
        
    Returns:
    --------
    xx : np.ndarray of shape (resolution, resolution)
        Grid coordinates along the X axis.
    yy : np.ndarray of shape (resolution, resolution)
        Grid coordinates along the Y axis.
    grid_points : np.ndarray of shape (resolution * resolution, 2)
        Concatenated grid coordinates ready for model prediction.
    """
    x_min, x_max = X[:, 0].min() - padding, X[:, 0].max() + padding
    y_min, y_max = X[:, 1].min() - padding, X[:, 1].max() + padding
    
    xx, yy = np.meshgrid(
        np.linspace(x_min, x_max, resolution),
        np.linspace(y_min, y_max, resolution)
    )
    grid_points = np.c_[xx.ravel(), yy.ravel()]
    
    return xx, yy, grid_points

def compute_decision_surface(model, grid_points, resolution=100):
    """
    Computes decision function scores on the grid points and reshapes to grid shape.
    
    Parameters:
    -----------
    model : sklearn.svm.SVC
        Trained SVM model.
    grid_points : np.ndarray
        Evaluation grid points of shape (N, 2).
    resolution : int
        Grid resolution (must match what make_decision_grid produced).
        
    Returns:
    --------
    Z : np.ndarray of shape (resolution, resolution)
        Decision scores shaped to the evaluation grid.
    """
    Z = model.decision_function(grid_points)
    Z = Z.reshape(resolution, resolution)
    return Z
