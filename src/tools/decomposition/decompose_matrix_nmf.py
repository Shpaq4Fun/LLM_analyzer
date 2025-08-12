import numpy as np
import matplotlib.pyplot as plt
import os
import pickle

def decompose_matrix_nmf(
    data: dict,
    output_image_path: str,
    n_components: int = 3,
    max_iter: int = 150
) -> dict:
    """
    Factorize a non-negative matrix V into W (basis) and H (activations) using NMF.

    Parameters (in `data` dict expected keys):
    - primary_data: str, name of the 2D matrix to factorize (e.g., spectrogram, CSC map)
    - secondary_data: str, name of the horizontal axis variable (for labels)
    - tertiary_data: str, name of the vertical axis variable (for labels)
    - sampling_rate, nperseg, noverlap, original_phase, original_signal_data (optional)

    Other parameters:
    - n_components: number of components (rank)
    - max_iter: number of multiplicative update iterations
    - tolerance: reserved for convergence checks (not used in current implementation)

    Returns:
    - dict with keys:
        W_basis_vectors, H_activations, image_path, domain ('decomposed_matrix'),
        original_phase, original_domain, sampling_rate, nperseg, noverlap,
        carrier_frequencies, original_signal_data, primary_data, secondary_data
    """
    primary_data = data.get('primary_data')
    if primary_data is None:
        print("Warning: No primary data provided for decompose_matrix_nmf tool.")

    V = data.get(primary_data)
    V = np.sqrt(V)
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
    
    if not os.path.isfile(output_image_path):
        # Plot basis vectors (columns of W)\
        fig, ax = plt.subplots(n_components,2,figsize=[7,6])
        for i in range(n_components):
            ax[i,0].plot(W[:, i], linewidth=0.5)
            ax[i,0].set_title(f'Basis Vector {i+1}')
            ax[i,0].set_xlabel(f'{secondary_data}')
            ax[i,0].set_ylabel('Weight')
            ax[i,0].grid(True)

            ax[i,1].plot(H[i, :], linewidth=0.5)
            ax[i,1].set_title(f'Activation Vector {i+1}')
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
