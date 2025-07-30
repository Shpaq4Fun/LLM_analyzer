# **Tool: select\_component**

## **1\. Purpose**

Selects a single, specific time-series signal from a list of reconstructed components based on a provided index.

## **2\. Strategic Advice**

This is a utility tool that acts as a bridge between a decomposition step and further processing. It should be used immediately after a decomposition has been made by another tool, such as *decompose\_matrix\_nmf,* and evaluated to select the component index. This tool takes that index and the original list of all reconstructed signals to formally isolate the single chosen signal, making it available for the next steps in the analysis pipeline.

## **3\. Input Specification**

* **Data Structure:** A Python dictionary.  
* **Domain / Context:** The dictionary must contain:  
  * signals\_reconstructed: A list of 1D NumPy arrays, where each array is a reconstructed time-domain signal.  
  * sampling\_rate: The sampling rate of the signals.

## **4\. Output Specification**

* **Data Structure:** A Python dictionary containing the selected signal and metadata.  
* **Domain / Context:**  
  * signal\_data: A 1D NumPy array representing the single selected time-domain signal.  
  * sampling\_rate: The sampling rate of the signal.  
  * image\_path: A string path to the saved plot of the selected signal.  
  * domain: A string identifier, set to 'time-series'.  
  * primary\_data: The key for the main data array, set to 'signal\_data'.

## **5\. Parameters**

| Name | Type | Description | Required | Default |
| :---- | :---- | :---- | :---- | :---- |
| data | dict | The dictionary containing the list of signals\_reconstructed and sampling\_rate. | Yes | None |
| output\_image\_path | str | The full path where the output PNG image of the selected signal will be saved. | Yes | None |
| component\_index | int | The integer index of the component to select from the list. | Yes | None |

## **6\. Next Steps Enabled**

* **Final Diagnostic Analysis:** The primary next step is to apply create\_envelope\_spectrum to the selected signal\_data to clearly see the modulating frequencies of the isolated fault.    
* **Further Filtering:** The isolated component can be subjected to further, more precise filtering if needed.

## **7\. Example Usage**
```
# Action to formally select component with index 2 after a visual evaluation  
selection_action = {  
    "tool_name": "select_component",  
    "params": {  
        "data": {  
            "signals_reconstructed": all_reconstructed_signals,  
            "sampling_rate": 50000  
        },  
        "output_image_path": "./outputs/run_xyz/selected_component.png",  
        "component_index": 2  
    },  
    "output_variable": "final_selected_signal"  
}

# The system's translator would convert this action to:  
# final_selected_signal = tools.decomposition.select_component(...)  
```