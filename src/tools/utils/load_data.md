# **Tool: load\_data**

## **1\. Purpose**

Visualizes the initial, raw time-series signal by generating a standard amplitude vs. time plot. For convenience, the plot displays a trimmed version of the signal (approximately 2 seconds long).

## **2\. Strategic Advice**

This tool should always be the **first action** in any new analysis pipeline. Its purpose is to establish a visual baseline of the input data. The generated plot allows the orchestrator (and the user) to perform an initial qualitative assessment of the signal\'s characteristics, such as its overall amplitude, the presence of obvious transients, or significant DC offsets, before any processing is applied.

## **3\. Input Specification**

* **Data Structure:** 1D NumPy array.
* **Domain:** Raw time-series signal.

## **4\. Output Specification**

* **Data Structure:** A Python dictionary containing multiple keys for data and metadata.
* **Domain / Context:**
  * signal\_data: The original 1D NumPy array passed as input.
  * sampling\_rate: The original sampling rate integer passed as input.
  * image\_path: A string path to the saved PNG visualization of the time-series plot.
  * domain: A string identifier, set to 'time-series', for use by the Quantitative Parameterization Module.
  * primary\_data: The key for the main data array, set to 'signal\_data'.

## **5\. Parameters**

| Name | Type | Description | Required | Default |
| :---- | :---- | :---- | :---- | :---- |
| signal\_data | np.ndarray | 1D NumPy array containing the time-series signal. | Yes | None |
| sampling\_rate | int | The sampling frequency of the signal in Hz. | Yes | None |
| output\_dir | str | The directory where the output plot will be saved. | Yes | None |

## **6\. Next Steps Enabled**

* Provides the initial signal\_data required by all subsequent processing and transformation tools.
* The primary next step is typically to apply a wideband analysis tool to understand the frequency content, such as create\_signal\_spectrogram or create\_fft\_spectrum.
* The output can be fed into the **Quantitative Parameterization Module** to calculate baseline statistics (e.g., Kurtosis, Crest Factor) for the raw signal.

## **7\. Example Usage**
```
# The very first action in a pipeline, visualizing the initial state.
load_action = {
    "tool_name": "load_data",
    "params": {
        "signal_data": initial_signal_from_gui,
        "sampling_rate": initial_fs_from_gui,
        "output_dir": "./outputs/run_xyz/"
    },
    "output_variable": "initial_data"
}

# The system's translator would convert this action to:
# initial_data = tools.utils.load_data(...)
```
