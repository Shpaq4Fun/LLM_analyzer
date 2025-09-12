from numba import jit
import numpy as np

def rlowess2(x, y, window_size=20, it=3, degree=1, use_numba=True):
    """
    Optimized RLOWESS: Robust Locally Weighted Scatterplot Smoothing
    
    Parameters:
    -----------
    x : array-like
        The independent variable values.
    y : array-like
        The dependent variable values.
    window_size : int, optional (default=20)
        The number of points to use for each local fit.
    it : int, optional (default=3)
        The number of robustifying iterations to perform.
    degree : int, optional (default=1)
        The degree of the local polynomial fit.
    use_numba : bool, optional (default=True)
        Whether to use Numba JIT compilation for performance.
        
    Returns:
    --------
    y_smooth : array
        The smoothed values of y.
    """
    x = np.asarray(x, dtype=np.float64)
    y = np.asarray(y, dtype=np.float64)
    
    # Sort data by x values
    order = np.argsort(x)
    x = x[order]
    y = y[order]
    
    n = len(x)
    
    # Ensure window_size is at least degree + 1 and at most n
    window_size = max(min(window_size, n), degree + 1)
    
    # Use optimized implementation
    if use_numba:
        try:
            y_smooth = _rlowess_numba(x, y, window_size, it, degree)
        except:
            # Fall back to numpy if numba fails
            y_smooth = _rlowess_numpy(x, y, window_size, it, degree)
    else:
        y_smooth = _rlowess_numpy(x, y, window_size, it, degree)
    
    # Restore original order
    inverse_order = np.argsort(order)
    return y_smooth[inverse_order]

@jit(nopython=True, cache=True)
def _rlowess_numba(x, y, window_size, it, degree):
    """Numba-accelerated RLOWESS implementation."""
    n = len(x)
    y_smooth = np.zeros_like(y)
    residuals = np.zeros_like(y)
    
    # Pre-compute x powers for polynomial fitting
    x_powers = np.ones((n, degree + 1))
    for j in range(1, degree + 1):
        x_powers[:, j] = x ** j
    
    for iteration in range(it + 1):
        # Calculate robust weights after first iteration
        if iteration > 0:
            # Compute median absolute deviation
            abs_resid = np.abs(residuals)
            s = np.median(abs_resid)
            
            # Skip robustifying if s is too small
            if s < 1e-10:
                break
            
            # Compute robust weights using bisquare function
            robust_weights = np.zeros_like(residuals)
            for i in range(n):
                if abs_resid[i] < 6 * s:
                    u = abs_resid[i] / (6 * s)
                    robust_weights[i] = (1 - u**2)**2
        else:
            robust_weights = np.ones(n)
        
        # For each point, perform local regression
        for i in range(n):
            # Find window indices efficiently
            half_window = window_size // 2
            left_idx = max(0, i - half_window)
            right_idx = min(n, left_idx + window_size)
            
            # Adjust if window is truncated on the right
            if right_idx - left_idx < window_size:
                left_idx = max(0, right_idx - window_size)
            
            # Calculate distances and weights for points in window
            local_x = x[left_idx:right_idx]
            local_y = y[left_idx:right_idx]
            distances = np.abs(local_x - x[i])
            
            # Find maximum distance for normalization
            max_dist = np.max(distances)
            if max_dist == 0:
                max_dist = 1.0
                
            # Calculate tricube weights
            local_weights = np.zeros(right_idx - left_idx)
            for j in range(len(local_weights)):
                ratio = distances[j] / max_dist
                local_weights[j] = (1 - ratio**3)**3
                
            # Apply robust weights
            if iteration > 0:
                local_weights *= robust_weights[left_idx:right_idx]
            
            # Skip if all weights are effectively zero
            if np.max(local_weights) < 1e-10:
                y_smooth[i] = y[i]
                continue
            
            # Create weighted design matrix and response
            X = x_powers[left_idx:right_idx, :]
            w_sqrt = np.sqrt(local_weights)
            
            # Weight the design matrix and response
            X_w = np.zeros((right_idx - left_idx, degree + 1))
            for j in range(right_idx - left_idx):
                for k in range(degree + 1):
                    X_w[j, k] = X[j, k] * w_sqrt[j]
            
            y_w = local_y * w_sqrt
            
            # Solve weighted least squares using QR decomposition
            # (simplified approach for numba compatibility)
            try:
                # Simple attempt to solve using normal equations
                XtX = np.zeros((degree + 1, degree + 1))
                Xty = np.zeros(degree + 1)
                
                for j in range(degree + 1):
                    Xty[j] = np.sum(X_w[:, j] * y_w)
                    for k in range(j, degree + 1):
                        XtX[j, k] = np.sum(X_w[:, j] * X_w[:, k])
                        if j != k:
                            XtX[k, j] = XtX[j, k]
                
                # Add regularization to avoid singular matrix
                for j in range(degree + 1):
                    XtX[j, j] += 1e-10
                
                # Solve linear system
                b = np.zeros(degree + 1)
                # Simple Gauss elimination (could be improved)
                for j in range(degree + 1):
                    b[j] = Xty[j]
                    for k in range(j):
                        b[j] -= XtX[j, k] * b[k]
                    b[j] /= XtX[j, j]
                
                # Prediction at the point of interest
                y_pred = 0.0
                for j in range(degree + 1):
                    y_pred += b[j] * x[i]**j
                
                y_smooth[i] = y_pred
            except:
                # Fallback if something goes wrong
                y_smooth[i] = y[i]
        
        # Update residuals for next iteration
        for i in range(n):
            residuals[i] = y[i] - y_smooth[i]
    
    return y_smooth

def _rlowess_numpy(x, y, window_size, it, degree):
    """NumPy-based RLOWESS implementation (no Numba)."""
    n = len(x)
    y_smooth = np.zeros_like(y)
    
    # Pre-compute powers of x for polynomial fitting
    x_powers = np.vander(x, degree + 1, increasing=True)
    
    # Perform robust iterations
    for iteration in range(it + 1):
        if iteration > 0:
            # Compute residuals and median absolute deviation
            residuals = y - y_smooth
            s = np.median(np.abs(residuals))
            
            if s < 1e-10:  # Skip robustifying if s is too small
                break
                
            # Compute robust weights using bisquare function
            robust_weights = np.zeros_like(residuals)
            mask = np.abs(residuals) < 6 * s
            u = np.abs(residuals[mask]) / (6 * s)
            robust_weights[mask] = (1 - u**2)**2
        else:
            robust_weights = np.ones(n)
        
        # Use vectorization for faster processing
        # Process in chunks to avoid memory issues with large datasets
        chunk_size = min(10000, n)  # Adjust based on available memory
        for chunk_start in range(0, n, chunk_size):
            chunk_end = min(chunk_start + chunk_size, n)
            chunk_indices = np.arange(chunk_start, chunk_end)
            
            # For each point in chunk, find its window
            for i in chunk_indices:
                # Find window indices efficiently
                half_window = window_size // 2
                left_idx = max(0, i - half_window)
                right_idx = min(n, left_idx + window_size)
                
                # Adjust if window is truncated on the right
                if right_idx - left_idx < window_size:
                    left_idx = max(0, right_idx - window_size)
                
                window_indices = np.arange(left_idx, right_idx)
                
                # Get local data
                x_local = x[window_indices]
                y_local = y[window_indices]
                X_local = x_powers[window_indices, :]
                
                # Calculate tricube weights
                distances = np.abs(x_local - x[i])
                max_dist = np.max(distances)
                if max_dist == 0:
                    tricube_weights = np.ones_like(distances)
                else:
                    tricube_weights = (1 - (distances/max_dist)**3)**3
                
                # Combine with robust weights
                combined_weights = tricube_weights * robust_weights[window_indices]
                
                # Skip if all weights are too small
                if np.max(combined_weights) < 1e-10:
                    y_smooth[i] = y[i]
                    continue
                
                # Weighted least squares solution
                try:
                    # Efficient weighted least squares using matrix operations
                    w_sqrt = np.sqrt(combined_weights)
                    X_weighted = X_local * w_sqrt[:, np.newaxis]
                    y_weighted = y_local * w_sqrt
                    
                    # Using np.linalg.lstsq for better numerical stability
                    b = np.linalg.lstsq(X_weighted, y_weighted, rcond=None)[0]
                    
                    # Prediction at the point of interest
                    y_smooth[i] = np.sum([b[j] * x[i]**j for j in range(degree + 1)])
                except:
                    # Fallback
                    y_smooth[i] = y[i]
    
    return y_smooth