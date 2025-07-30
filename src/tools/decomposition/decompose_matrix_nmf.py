import numpy as np
import matplotlib.pyplot as plt
import os

def decompose_matrix_nmf(
    data: dict,
    output_image_path: str,
    n_components: int = 3,
    max_iter: int = 200,
    tolerance: float = 1e-4
) -> dict:
    """
    Decomposes a generic non-negative 2D matrix (V) into two smaller matrices
    (W and H) using the classic Lee and Seung NMF algorithm.

    Args:
        data (dict): The output dictionary from a previous tool. Must contain a 2D
                     matrix under a key like 'magnitude' or 'csc_map'. Can also
                     contain 'phase' which will be passed through.
        output_image_path (str): Path to a directory where component plot images will be saved.
        n_components (int): The number of components (rank) for the factorization.
        max_iter (int, optional): The maximum number of iterations. Defaults to 200.
        tolerance (float, optional): Tolerance for the stopping condition. Defaults to 1e-4.

    Returns:
        dict: A dictionary containing the decomposition results.
    """
    primary_data = data.get('primary_data')
    if primary_data is None:
        print("Warning: No primary data provided for decompose_matrix_nmf tool.")

    V = data.get(primary_data)
    V = np.log10(V)
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
    epsilon = 1e-9
    W = np.random.rand(V.shape[0], n_components)
    H = np.random.rand(n_components, V.shape[1])

    for i in range(max_iter):
        H_old = H.copy()
        W_T = W.T
        H = H * ((W_T @ V) / (W_T @ W @ H + epsilon))
        H_T = H.T
        W = W * ((V @ H_T) / (W @ H @ H_T + epsilon))
        
        error = np.linalg.norm(H - H_old) / (np.linalg.norm(H_old) + epsilon)
        if error < tolerance:
            print(f"NMF converged at iteration {i+1}")
            break
    
    # Plot basis vectors (columns of W)
    fig, ax = plt.subplots(n_components,2,figsize=[12,9])
    for i in range(n_components):
        ax[i,0].plot(W[:, i])
        ax[i,0].set_title(f'Basis Vector {i+1}')
        ax[i,0].set_xlabel(f'{secondary_data}')
        ax[i,0].set_ylabel('Weight')
        ax[i,0].grid(True)

        ax[i,1].plot(H[i, :])
        ax[i,1].set_title(f'Activation Vector {i+1}')
        ax[i,1].set_xlabel(f'{tertiary_data}')
        ax[i,1].set_ylabel('Weight')
        ax[i,1].grid(True)
    
    plt.savefig(output_image_path)
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
