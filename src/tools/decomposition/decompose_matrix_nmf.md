# **Tool: decompose\_matrix\_nmf**

## **1\. Purpose**

Decomposes a non-negative 2D matrix (V) into a set of additive basis vectors (W) and their corresponding activations (H).

## **2\. Strategic Advice**

This is a powerful processing tool for source separation and pattern discovery. Use it when a 2D data representation (like a spectrogram or CSC map) is complex and appears to contain components that might be separated. The output is not a final result, but a set of building blocks that must be analyzed and selected in a subsequent step.

**Use Case 1: Decomposing a Spectrogram (Time-Frequency Matrix)**

* **W Vectors represent:** Carrier frequency profiles - spectral shapes or "what" is happening (e.g., a harmonic profile). Interpretation: custom data-driven filters can be designed from these profiles to extract individual components from the original time-series signal.
* **H Vectors represent:** Temporal activations or "when" it is happening (e.g., the impulsiveness of a fault). Interpretation: indicators of event occurrence in time domain.
* **Goal:** To separate different sound sources or signal components that occur at the same time but have different frequency characteristics.

**Use Case 2: Decomposing a CSC Map (Carrier Freq vs. Cyclic Freq Matrix)**

* **W Vectors represent:** Carrier frequency profiles - spectral shapes or "what" is happening (e.g., a harmonic profile). Interpretation: custom data-driven filters can be designed from these profiles to extract individual components from the original time-series signal.
* **H Vectors represent:** The corresponding "activation" of that profile across different cyclic frequencies.  Interpretation: equivalent to envelope spectra of the individual components, may contain modulation pattern of the fault component.
* **Goal:** To identify groups of carrier frequencies that are modulated by the same set of cyclic frequencies, potentially revealing a single underlying mechanical process.

## **3\. Input Specification**

* **Data Structure:** A Python dictionary from a previous step.
* **Domain / Context:** The dictionary must contain the following keys:
  * `primary_data`: The name of the key holding the 2D matrix to be factorized (e.g., 'magnitude', 'csc_map').
  * `secondary_data`: The name of the key for the x-axis labels.
  * `tertiary_data`: The name of the key for the y-axis labels.
  * `original_signal_data` (optional): The original time-series data for reconstruction.
  * `original_phase` (optional): The original phase information for reconstruction.
  * `sampling_rate`, `nperseg`, `noverlap` (optional): Parameters for STFT-based reconstructions.

## **4. Output Specification**

* **Data Structure:** A Python dictionary containing the decomposition results.
* **Domain / Context:** The output dictionary will contain the following keys:
  * `W_basis_vectors`: A 2D NumPy array where each column is a basis vector.
  * `H_activations`: A 2D NumPy array where each row is the activation of a basis vector.
  * `image_path`: The file path to the plot of the decomposition.
  * `domain`: A string identifier, set to 'decomposed_matrix'.
  * `primary_data`: Set to 'H_activations'.
  * `secondary_data`: Set to 'W_basis_vectors'.
  * Plus, it carries over `original_phase`, `original_domain`, `sampling_rate`, `nperseg`, `noverlap`, `carrier_frequencies`, and `original_signal_data` if they were in the input.

## **5\. Parameters**

| Name | Type | Description | Required | Default |
| :---- | :---- | :---- | :---- | :---- |
| data | dict | The dictionary containing the 2D matrix and its metadata. | Yes | None |
| output\_dir | str | The directory to save the output plots to. | Yes | None |
| n\_components | int | The number of components to extract. This is a critical parameter. | No | 3 |
| max\_iter | int | The maximum number of iterations for the algorithm. | No | 200 |
| tolerance | float | The tolerance for the stopping condition based on convergence. | No | 1e-4 |

## **6\. Next Steps Enabled**

* **Component Selection (Mandatory Next Step):** The output is evaluated by the quantitative parameterization module, which will perform component reconstruction to time series signals. The next step has to select one of the components for further analysis. Hence, the next mandatory tool is `select_component`.


## **7\. Example Usage**
```
# Action to decompose a spectrogram into 3 components
nmf_action = {
    "tool_name": "decompose_matrix_nmf",
    "params": {
        "data": spectrogram_results,
        "output_dir": "./outputs/run_xyz/nmf_components/",
        "n_components": 3
    },
    "output_variable": "nmf_results"
}

# The system's translator would convert this action to:
# nmf_results = tools.decomposition.decompose_matrix_nmf(...)
```
