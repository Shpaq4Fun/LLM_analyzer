import numpy as np
import matplotlib.pyplot as plt
import os
import pickle
from typing import Dict, Any, Tuple, Optional, Union
from numpy.typing import NDArray
from src.lib.rlowess_smoother import rlowess2
 

def decompose_matrix_nmf(
    data: Dict[str, Any],
    output_image_path: str,
    n_components: int = 3,
    max_iter: int = 150,
    **kwargs
) -> Dict[str, Any]:
    """
    Factorize a non-negative matrix V into W (basis) and H (activations) using Non-negative Matrix Factorization (NMF).
    
    This implementation uses the multiplicative update algorithm to decompose the input matrix V into two non-negative
    matrices W (basis vectors) and H (activations) such that V ≈ WH. The algorithm is particularly useful for
    parts-based representation of data and feature extraction from non-negative data such as spectrograms.

    Parameters
    ----------
    data : Dict[str, Any]
        Dictionary containing the following keys:
        - 'primary_data': str
            Name of the key in data containing the 2D non-negative matrix to factorize (e.g., spectrogram, CSC map).
            The matrix should have shape (n_features, n_samples).
        - 'secondary_data': str, optional
            Name of the key containing horizontal axis labels (e.g., time points).
        - 'tertiary_data': str, optional
            Name of the key containing vertical axis labels (e.g., frequency bins).
        - 'sampling_rate': float, optional
            Sampling rate of the original signal in Hz.
        - 'nperseg': int, optional
            Length of each segment used in STFT if the input is a spectrogram.
        - 'noverlap': int, optional
            Number of points to overlap between segments if the input is a spectrogram.
        - 'original_phase': np.ndarray, optional
            Phase information if the input is derived from a complex spectrogram.
        - 'original_signal_data': np.ndarray, optional
            The original time-domain signal if available.

    output_image_path : str
        Path where the visualization of the decomposition will be saved.
        The parent directory will be created if it doesn't exist.
        
    n_components : int, default=3
        Number of components (rank) for the factorization.
        Must be a positive integer less than min(n_features, n_samples).
        
    max_iter : int, default=150
        Maximum number of iterations for the multiplicative update algorithm.
        More iterations may lead to better convergence but increase computation time.
        
    **kwargs
        Additional keyword arguments (not currently used, for future compatibility).

    Returns
    -------
    Dict[str, Any]
        Dictionary containing the following keys:
        - 'W_basis_vectors': np.ndarray
            Basis matrix of shape (n_features, n_components).
        - 'H_activations': np.ndarray
            Activation matrix of shape (n_components, n_samples).
        - 'image_path': str
            Path to the saved visualization.
        - 'domain': str
            Set to 'decomposed_matrix' to indicate the type of data.
        - 'original_phase': np.ndarray or None
            Phase information if provided in the input.
        - 'original_domain': str or None
            Domain of the original data (e.g., 'time-frequency-matrix').
        - 'sampling_rate': float or None
            Sampling rate if provided in the input.
        - 'nperseg': int or None
            Segment length if provided in the input.
        - 'noverlap': int or None
            Overlap between segments if provided in the input.
        - 'carrier_frequencies': np.ndarray or None
            Frequency values if the input is a spectrogram.
        - 'original_signal_data': np.ndarray or None
            Original time-domain signal if provided.
        - 'primary_data': str
            Name of the primary data field.
        - 'secondary_data': str or None
            Name of the secondary data field if provided.
            
    Notes
    -----
    - The implementation applies a power transform (V^(1/4)) and normalization to the input matrix
      to improve the decomposition results.
    - The algorithm may not converge to a global minimum due to the non-convex nature of NMF.
    - For better results, consider normalizing or scaling your input data appropriately.
    """
    primary_data = data.get('primary_data')
    if primary_data is None:
        print("Warning: No primary data provided for decompose_matrix_nmf tool.")

    V = data.get(primary_data)
    V = np.power(V,1/4)
    V = V/np.max(V)
    if V is None:
        print("Warning: No signal data provided for decompose_matrix_nmf tool.")

    secondary_data = data.get('secondary_data')
    if secondary_data is None:
        print("Warning: No secondary_data provided for decompose_matrix_nmf tool.")

    tertiary_data = data.get('tertiary_data')
    if tertiary_data is None:
        print("Warning: No tertiary_data provided for decompose_matrix_nmf tool.")

    sampling_rate = data.get('sampling_rate')
    nperseg = data.get('nperseg')
    noverlap = data.get('noverlap')

    # --- Input Validation and Data Extraction ---
    # Generically find the primary 2D matrix for decomposition

    # Pass the phase through for later reconstruction (if applicable)
    original_phase = data.get('original_phase')
    
    # --- Lee and Seung NMF Algorithm ---
    epsilon = 1e-5
    W = np.random.rand(V.shape[0], n_components)
    H = np.random.rand(n_components, V.shape[1])

    for i in range(max_iter):
        # H_old = H.copy()
        W_T = W.T
        H = H * ((W_T @ V) / (W_T @ W @ H + epsilon))
        H_T = H.T
        W = W * ((V @ H_T) / (W @ (H @ H_T) + epsilon))
        
        norms = np.sqrt(np.sum(H.T ** 2, axis=0))
        H = H / norms[:, np.newaxis]
        W = W * norms[np.newaxis, :]
        # H = H / np.matlib.repmat(norms, H.shape[1], 1).T
        # W = W * np.matlib.repmat(norms, W.shape[0], 1)

        # error = np.linalg.norm(H - H_old) / (np.linalg.norm(H_old) + epsilon)
        # if error < tolerance:
        #     print(f"NMF converged at iteration {i+1}")
        #     break
    
    # if not os.path.isfile(output_image_path):
        # Plot basis vectors (columns of W)\
    fig, ax = plt.subplots(n_components,2,figsize=[7,6])
    for i in range(n_components):
        ax[i,0].plot(W[:, i], linewidth=0.5)
        predictions_ma = rlowess2(np.arange(len(W[:, i])), W[:, i], window_size=9, it=5, degree=1)
        ax[i,0].plot(predictions_ma, linewidth=0.5, color='red')
        ax[i,0].set_title(f'Basis Vector {i}')
        ax[i,0].set_xlabel(f'{secondary_data}')
        ax[i,0].set_ylabel('Weight')
        ax[i,0].grid(True)

        ax[i,1].plot(H[i, :], linewidth=0.5)
        ax[i,1].set_title(f'Activation Vector {i}')
        ax[i,1].set_xlabel(f'{tertiary_data}')
        ax[i,1].set_ylabel('Weight')
        ax[i,1].grid(True)
    
    plt.savefig(output_image_path)
    fig_path = os.path.join(f"{output_image_path[:-2]}kl")
    with open(fig_path, 'wb') as f:
        pickle.dump(fig, f)
    plt.close()




    # --- Return the structured data output ---
    results = {
        'W_basis_vectors': W,
        'H_activations': H,
        'image_path': output_image_path,
        'domain': 'decomposed_matrix',
        'original_phase': original_phase,
        'original_domain': data.get('domain'),
        'sampling_rate': sampling_rate,
        'nperseg': nperseg,
        'noverlap': noverlap,
        'carrier_frequencies': data.get(tertiary_data),
        'original_signal_data': data.get('original_signal_data'),
        'primary_data': 'H_activations',
        'secondary_data': 'W_basis_vectors'
    }
    
    return results

