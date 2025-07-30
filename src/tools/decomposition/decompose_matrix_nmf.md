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
* **Domain / Context:** The dictionary must contain a 2D NumPy array like magnitude (for spectrograms) or csc\_map. 

## **4\. Output Specification**

* **Data Structure:** A Python dictionary containing the decomposition results.  
* **Domain / Context:**  
  * W\_basis\_vectors: A 2D NumPy array where each column is a basis vector (feature along the first dimension of the input matrix).  
  * H\_activations: A 2D NumPy array where each row is the activation of a basis vector over the second dimension of the input matrix. This is typically the primary data for the next selection step.  
  * component\_image\_paths: A dictionary with lists of file paths to the plots of each individual basis vector and activation vector.  
  * domain: A string identifier, set to 'decomposed\_matrix'.

## **5\. Parameters**

| Name | Type | Description | Required | Default |
| :---- | :---- | :---- | :---- | :---- |
| data | dict | The dictionary containing the 2D matrix and optional phase. | Yes | None |
| output\_image\_path | str | The full path to save the output PNG to. | Yes | None |
| n\_components | int | The number of components to extract. This is a critical parameter. | No | 3 |
| max\_iter | int | The maximum number of iterations for the algorithm. | No | 200 |
| tolerance | float | The tolerance for the stopping condition based on convergence. | No | 1e-4 |

## **6\. Next Steps Enabled**

* **Component Selection (Mandatory Next Step):** The output is evaluated by the quantitative parameterization module, which will perform component reconstruction to time series signals. The next step has to select one of the components for further analysis. Hence, the next mandatory tool is `select_component`.  


## **7\. Example Usage**
```
# Action to decompose a spectrogram into 5 components  
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