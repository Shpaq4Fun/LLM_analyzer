"""
Tkinter/CustomTkinter GUI for AIDA: AI-Driven Analyzer.

- Lets the user load data (.mat), build/load RAG indices, and enter analysis context
- Launches LLMOrchestrator in a background thread and visualizes the pipeline
- Displays logs and result plots with interactive selection
"""

# src/gui/main_window.py

import customtkinter as ctk
from tkinter import filedialog
import scipy.io
import numpy as np
import os, pickle
import threading
import queue
from src.core.rag_builder import RAGBuilder
from src.core.LLMOrchestrator import LLMOrchestrator
import h5py
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from datetime import datetime
from PIL import Image
import matplotlib
matplotlib.use('TkAgg')

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.loaded_data = None
        self.rag_builder = RAGBuilder()

        self.load_icon = ctk.CTkImage(Image.open("src/gui/assets/file-plus-2.png"), size=(24, 24))
        self.play_icon = ctk.CTkImage(Image.open("src/gui/assets/play.png"), size=(24, 24))
        self.build_icon = ctk.CTkImage(Image.open("src/gui/assets/library.png"), size=(24, 24))
        self.load2_icon = ctk.CTkImage(Image.open("src/gui/assets/folder-down.png"), size=(24, 24))

        # --- Basic Window Configuration ---
        self.title("AIDA: AI-Driven Analyzer")
        self.geometry("1800x1000")
        self.configure(fg_color="#1a202c")

        self.flowchart_blocks = {} # To store mapping of canvas item ID to action data
        self.last_flowchart_rect_id = None # To track the last block for drawing arrows

        # --- Grid Layout Configuration ---
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=4)
        self.grid_columnconfigure(2, weight=4)
        self.grid_rowconfigure(0, weight=1)

        # --- Header ---
        # header = ctk.CTkFrame(self, fg_color="#1a202c", corner_radius=0)
        # header.grid(row=0, column=0, columnspan=3, sticky="ew", pady=(0, 0))
        # header_label = ctk.CTkLabel(header, text="AIDA: AI-Driven Analyzer        LORA: LLM-Orchestrated Research Agent", font=ctk.CTkFont(size=20, weight="bold"), text_color="#f7fafc")
        # header_label.pack(pady=0)

        # --- Main Panels ---
        self._create_controls_panel()
        self._create_visualization_panel()
        self._create_log_panel()

        self.log_message("System", "Welcome! \n\nInstructions: \n\n1. Load the data, \n2. Load RAG index (or build a new one), \n3. Enter your analysis objective and data description,\n4. Start the analysis.")

        # --- Threading and Queue Setup ---
        self.rag_queue = queue.Queue()
        self.flowchart_x_offset = 10 # Starting X position for flowchart blocks
        self.flowchart_y_offset = 10 # Starting Y position for flowchart blocks
        self.flowchart_block_width = 150
        self.flowchart_block_height = 60
        self.flowchart_horizontal_spacing = 30
        self.flowchart_vertical_spacing = 20
        self.after(100, self.process_queue)

    def _create_panel(self, parent, row, column, rowspan=1, columnspan=1):
        """Helper function to create a consistent panel style."""
        panel = ctk.CTkFrame(parent, fg_color="#1a202c", corner_radius=0, border_width=0, border_color="#2d3748")
        panel.grid(row=row, column=column, rowspan=rowspan, columnspan=columnspan, sticky="nsew", padx=0, pady=0)
        return panel

    def _create_controls_panel(self):
        controls_panel = self._create_panel(self, 0, 0)
        controls_panel.grid_columnconfigure(0, weight=1)
        controls_panel.grid_rowconfigure(11, weight=1) # Allow controls to space out

        header = ctk.CTkLabel(controls_panel, text="AIDA", font=ctk.CTkFont(size=40, weight="bold"))
        header.grid(row=0, column=0, sticky="n", padx=15, pady=(10,0))

        header0 = ctk.CTkLabel(controls_panel, text="AI-Driven Analyzer", font=ctk.CTkFont(size=12))
        header0.grid(row=1, column=0, sticky="n", padx=15, pady=(0,0))

        header1 = ctk.CTkLabel(controls_panel, text="1. Load data", font=ctk.CTkFont(size=14))
        header1.grid(row=2, column=0, sticky="w", padx=10, pady=2)

        # Load Data Button
        self.load_data_btn = ctk.CTkButton(controls_panel,
                                           text="Load Data File (.mat)",
                                           text_color="#f7fafc",
                                           command=self.load_data_file,
                                           fg_color=("#3182ce", "#3D5F7E"),
                                           hover_color="#2b6cb0",
                                           corner_radius=8,
                                           image=self.load_icon,      # <--- PRZYPISZ IKONĘ
                                           font=ctk.CTkFont(family="Helvetica", size=20, weight="bold"))
        self.load_data_btn.configure(height=50)
        self.load_data_btn.grid(row=3, column=0, sticky="ew", padx=30, pady=0)

        # Objective Input
        obj_label = ctk.CTkLabel(controls_panel, text="2. Analysis Objective:", font=ctk.CTkFont(size=14))
        obj_label.grid(row=4, column=0, sticky="w", padx=10)
        self.objective_input = ctk.CTkTextbox(controls_panel, height=290, fg_color="#4a5568", border_color="#5a6578", corner_radius=0)
        self.objective_input.grid(row=5, column=0, sticky="ew", padx=10, pady=(0, 0))

        # Data Description Input
        desc_label = ctk.CTkLabel(controls_panel, text="3. Data Description:", font=ctk.CTkFont(size=14))
        desc_label.grid(row=6, column=0, sticky="w", padx=10, pady=(10, 0))
        self.data_description_input = ctk.CTkTextbox(controls_panel, height=290, fg_color="#4a5568", border_color="#5a6578", corner_radius=0)
        self.data_description_input.grid(row=7, column=0, sticky="new", padx=10, pady=(0, 2))

        # Buttons
        buttons_label = ctk.CTkLabel(controls_panel, text="4. Knowledge Base:", font=ctk.CTkFont(size=14))
        buttons_label.grid(row=8, column=0, sticky="nw", padx=10, pady=(10, 0))
        button_frame = ctk.CTkFrame(controls_panel, fg_color="transparent")
        button_frame.grid(row=9, column=0, sticky="new", padx=20, pady=0)
        button_frame.grid_columnconfigure(0, weight=1)
        button_frame.grid_columnconfigure(1, weight=1)
        button_frame.grid_rowconfigure(0, weight=1)

        self.build_rag_btn = ctk.CTkButton(button_frame, text="Build RAG Index", command=self.on_build_rag_index, fg_color=("#3182ce", "#3D5F7E"), hover_color="#2b6cb0", font=ctk.CTkFont(family="Helvetica", size=14, weight="bold"), width=180, image=self.build_icon)
        self.build_rag_btn.configure(height=50)
        self.build_rag_btn.grid(row=0, column=0, sticky="nsew", pady=2, padx=10)

        self.load_rag_btn = ctk.CTkButton(button_frame, text="Load RAG Index", command=self.on_load_rag_index, fg_color=("#3182ce", "#3D5F7E"), hover_color="#2b6cb0", font=ctk.CTkFont(family="Helvetica", size=14, weight="bold"), width=180, image=self.load2_icon)
        self.load_rag_btn.configure(height=50)
        self.load_rag_btn.grid(row=0, column=1, sticky="nsew", pady=2, padx=10)

        self.start_btn = ctk.CTkButton(controls_panel, text="Start Analysis", command=self.on_start_analysis, fg_color=("#3182ce", "#3D5F7E"), hover_color="#2b6cb0", font=ctk.CTkFont(family="Helvetica", size=20, weight="bold"),image=self.play_icon)
        self.start_btn.configure(height=50)
        self.start_btn.grid(row=11, column=0, sticky="ew", pady=2, padx=30)


    def _create_visualization_panel(self):
        viz_panel = self._create_panel(self, 0, 1)
        viz_panel.grid_rowconfigure(1, weight=1)
        viz_panel.grid_rowconfigure(3, weight=5)
        viz_panel.grid_columnconfigure(0, weight=1)

        # Flowchart
        flowchart_header = ctk.CTkLabel(viz_panel, text="  Action Sequence Flowchart  ", font=ctk.CTkFont(size=16, weight="bold"), bg_color="#303949")
        flowchart_header.grid(row=0, column=0, sticky="w", padx=2, pady=0)
        self.flowchart_canvas = ctk.CTkCanvas(viz_panel, background="#303949", highlightthickness=0,scrollregion = (0,0,2000,1000))
        self.flowchart_canvas.grid(row=1, column=0, sticky="nsew", padx=2, pady=(0, 10))
        ctk_textbox_scrollbar = ctk.CTkScrollbar(self.flowchart_canvas, command=self.flowchart_canvas.yview)
        ctk_textbox_scrollbar.place(relx=1,rely=0,relheight=1,anchor='ne')
        self.flowchart_canvas.configure(yscrollcommand=ctk_textbox_scrollbar.set)
        # Plot
        plot_header = ctk.CTkLabel(viz_panel, text="  Result Plot  ", font=ctk.CTkFont(size=16, weight="bold"), bg_color="#303949")
        plot_header.grid(row=2, column=0, sticky="w", padx=2, pady=0)
        self.plot_canvas = ctk.CTkCanvas(viz_panel, background="#303949", highlightthickness=0)
        self.plot_canvas.grid(row=3, column=0, sticky="nsew", padx=2, pady=(0, 2))

    def _create_log_panel(self):
        log_panel = self._create_panel(self, 0, 2)
        log_panel.grid_rowconfigure(1, weight=1)
        log_panel.grid_columnconfigure(0, weight=1)

        header = ctk.CTkLabel(log_panel, text="  Log  ", font=ctk.CTkFont(size=16, weight="bold"), bg_color="#303949")
        header.grid(row=0, column=0, sticky="w", padx=2, pady=0)

        self.log_textbox = ctk.CTkTextbox(log_panel, fg_color="#303949", text_color="#e2e8f0", activate_scrollbars=True, corner_radius=0, width=450)
        self.log_textbox.grid(row=1, column=0, sticky="nsew", padx=2, pady=(0, 2))

        # Configure a tag for the sender's name to make it stand out
        self.log_textbox.tag_config("sender_style", foreground="#63b3ed", underline=True) # A nice light blue color
        # self.log_textbox.tag_config("llm_style", foreground="#ebebeb") # A nice light blue color
        self.log_textbox.tag_config("translator_style", foreground="#6d9dd4") # A nice light blue color
        self.log_textbox.configure(state="disabled")

    def log_message(self, sender, message):
        """Appends a formatted message to the log text box."""
        self.log_textbox.configure(state="normal")
        self.log_textbox.insert("end", f"{sender}:", "sender_style")
        match sender:
            case "System":
                self.log_textbox.insert("end", f"  {message} \n\n")
            case "Prompt Translator":
                self.log_textbox.insert("end", f"  {message} \n\n", "translator_style")
            case "LLM Orchestrator":
                self.log_textbox.insert("end", f"  {message} \n\n")
            case "User":
                self.log_textbox.insert("end", f"  {message} \n\n")
            case "RAGBuilder":
                self.log_textbox.insert("end", f"  {message} \n\n")
            case "LLM Orchestrator (Error)":
                self.log_textbox.insert("end", f"  {message} \n\n")

        # self.log_textbox.insert("end", f"{sender}:", "sender_style")
        # self.log_textbox.insert("end", f"  {message} \n\n")
        self.log_textbox.configure(state="disabled")
        self.log_textbox.see("end") # Scroll to the end

    def on_start_analysis(self):
        """Placeholder function for the start button."""
        objective = self.objective_input.get("1.0", "end-1c")
        description = self.data_description_input.get("1.0", "end-1c")

        if self.loaded_data is None:
            self.log_message("System", "Error: Please load a data file before starting the analysis.")
            return

        if not objective.strip() or not description.strip():
            self.log_message("System", "Error: Please provide both an Analysis Objective and Data Description.")
            return

        self.log_message("User", f"Starting analysis with objective: \"{objective.strip()}\"")
        # self.log_message("System", "Backend processing would start here...")

        # self.start_btn.configure(state="disabled")

        # Create a unique run ID for this analysis
        run_id = f"run_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        # Instantiate and run the orchestrator in a separate thread
        self.orchestrator = LLMOrchestrator(
            user_data_description=description,
            user_objective=objective,
            run_id=run_id,
            loaded_data=self.loaded_data,
            signal_var_name=self.signal_var_name,
            fs_var_name=self.fs_var_name,
            log_queue=self.rag_queue
        )

        analysis_thread = threading.Thread(target=self.orchestrator.run_analysis_pipeline)
        analysis_thread.start()
        # self.orchestrator.delete_caches()

    def on_build_rag_index(self):
        """Opens a dialog to select the knowledge base directory and starts the RAG index build process."""
        self.log_message("System", "Please select the root directory of your knowledge base.")
        knowledge_base_path = filedialog.askdirectory(title="Select Knowledge Base Directory")

        self.log_message("System", "Please select the root directory of your toolbase.")
        tools_path = filedialog.askdirectory(title="Select Tools Directory")

        if not knowledge_base_path or not tools_path:
            self.log_message("System", "RAG index build cancelled.")
            return

        self.log_message("System", f"Knowledge base selected: {knowledge_base_path}")
        self.log_message("System", f"Toolbase selected: {tools_path}")
        self.log_message("System", "Starting RAG index build process...")

        self.build_rag_btn.configure(state="disabled")
        self.load_rag_btn.configure(state="disabled")
        self.start_btn.configure(state="disabled")

        # Run the build process in a separate thread to avoid freezing the GUI
        thread = threading.Thread(target=self.rag_builder.build_index, args=([knowledge_base_path], self.rag_queue, "./vector_store"))
        thread.start()
        thread1 = threading.Thread(target=self.rag_builder.build_index, args=([tools_path], self.rag_queue, "./vector_store_tools"))
        thread1.start()

    def process_queue(self):
        """
        Process messages from the worker thread queue.
        This is run periodically from the main GUI thread.
        """
        try:
            message, data = self.rag_queue.get_nowait()

            if message == "log":
                self.log_message(data['sender'], data['message'])
            elif message == "flowchart_add_step":
                self._add_flowchart_step(data) # Pass the entire data dictionary
            elif message == "finish":
                self.log_message("System", "RAG index build process finished.")
                self.build_rag_btn.configure(state="normal")
                self.load_rag_btn.configure(state="normal")
                self.start_btn.configure(state="normal")
            elif message == "error":
                self.log_message("System", f"Error building RAG index: {data}")
                self.build_rag_btn.configure(state="normal")
                self.load_rag_btn.configure(state="normal")
                self.start_btn.configure(state="normal")

        except queue.Empty:
            pass
        finally:
            self.after(100, self.process_queue)

    def on_load_rag_index(self):
        """Opens a dialog to select the persisted index directory and loads it."""
        # self.log_message("System", "Please select the directory containing the persisted RAG index (e.g., 'chroma_db').")
        # index_path = filedialog.askdirectory(title="Select Persisted Index Directory")
        index_path = "./vector_store"
        index_path_tools = "./vector_store_tools"
        if not index_path:
            self.log_message("System", "RAG index loading cancelled.")
            return

        try:
            self.rag_builder.load_index(index_path)
            self.log_message("System", f"Successfully loaded RAG index from {index_path}")
            self.rag_builder.load_index(index_path_tools)
            self.log_message("System", f"Successfully loaded RAG index from {index_path_tools}")
        except Exception as e:
            self.log_message("System", f"Error loading RAG index: {e}")

    def load_data_file(self):
        """Opens a file dialog to select and load a .mat file."""
        file_path = filedialog.askopenfilename(
            title="Select a MATLAB Data File",
            filetypes=(("MATLAB files", "*.mat"), ("All files", "*.*"))
        )
        if not file_path:
            self.log_message("System", "Data loading cancelled.")
            return

        try:
            try:
                mat_data = scipy.io.loadmat(file_path)
                # f = h5py.File('mytestfile.hdf5', 'r')
            except:
                mat_data = h5py.File(file_path, 'r')

            # Filter out private variables (e.g., '__header__', '__version__') from the list of keys.
            # These are typically metadata from the MAT file and not actual data arrays.
            varnames = [
                k for k in mat_data.keys()
                if not (k.startswith('__') and k.endswith('__'))
            ]

            # For each variable, convert it to a NumPy array and extract the first column.
            # This assumes the data is stored in a 2D array where the signal is the first column.
            # Using np.asarray is slightly more efficient as it avoids a copy if the object is already an array.
            self.loaded_data = {
                k: np.asarray(mat_data[k])[:, 0] for k in varnames
            }
            # print(self.loaded_data)

            if not self.loaded_data:
                self.log_message("System", "Error: No suitable data arrays found in the selected .mat file.")
                return

            self.log_message("System", f"Successfully loaded data from {file_path}")
            self.log_message("System", f"Found data keys: {', '.join(self.loaded_data.keys())}")
            # Optionally, populate the data description
            self.data_description_input.delete("1.0", "end")
            # self.data_description_input.insert("1.0", f"Loaded .mat file with variables: {', '.join(self.loaded_data.keys())},\n")

            self._find_data_variables()
            # self.plot_time_series() # Removed: Plotting now handled by load_data action

        except Exception as e:
            self.log_message("System", f"Error loading file: {e}")
            self.loaded_data = None

    def _find_data_variables(self):
        """
        Analyzes the loaded data to find the names of the signal and fs variables.
        """
        if self.loaded_data is None:
            return

        # Find the longest array, assume it's the signal
        self.signal_var_name = max(self.loaded_data, key=lambda k: len(self.loaded_data[k]))

        # Find a scalar value, assume it's fs
        self.fs_var_name = None
        for k, v in self.loaded_data.items():
            if len(v) == 1:
                self.fs_var_name = k
                break


        if self.signal_var_name and self.fs_var_name:
            self.log_message("System", f"Automatically identified signal variable: '{self.signal_var_name}' and fs variable: '{self.fs_var_name}'")
        else:
            self.log_message("System", "Could not automatically identify signal and fs variables. Orchestrator will attempt to interpret and assign them.")

    def _display_image_on_plot_canvas(self, image_path):
        """Displays an image from a given path on the plot canvas."""
        if not image_path or not os.path.exists(image_path):
            self.log_message("System", f"Error: Image file not found at {image_path}")
            return

        # Clear previous plot/image
        for widget in self.plot_canvas.winfo_children():
            widget.destroy()

        try:
            '''
            # Use PIL to open the image
            from PIL import Image
            img = Image.open(image_path)
            # Resize image to fit canvas while maintaining aspect ratio
            canvas_width = self.plot_canvas.winfo_width()
            canvas_height = self.plot_canvas.winfo_height()
            if canvas_width == 1 and canvas_height == 1: # Default size before actual rendering
                canvas_width = 800 # Use a reasonable default
                canvas_height = 600
            img_width, img_height = img.size
            aspect_ratio = img_width / img_height
            if img_width > canvas_width or img_height > canvas_height:
                if (canvas_width / aspect_ratio) <= canvas_height:
                    new_width = canvas_width
                    new_height = int(canvas_width / aspect_ratio)
                else:
                    new_height = canvas_height
                    new_width = int(canvas_height * aspect_ratio)
                img = img.resize((new_width, new_height), Image.LANCZOS)
            self.tk_image = ImageTk.PhotoImage(img) # Keep a reference!
            # Center the image on the canvas
            x_center = canvas_width / 2
            y_center = canvas_height / 2
            canvas_image_id = self.plot_canvas.create_image(x_center, y_center, image=self.tk_image, anchor="center")
            self.plot_canvas.image = self.tk_image # Store reference to prevent garbage collection
            '''
            fig_path = os.path.join(f"{image_path[:-2]}kl")
            with open(fig_path, 'rb') as f:
                fig = pickle.load(f)
            # Create a canvas widget to display the figure
            fig.set_size_inches(6, 6)
            canvas = FigureCanvasTkAgg(fig, master=self.plot_canvas)
            canvas.draw()

            # Create a toolbar for the canvas
            toolbar = NavigationToolbar2Tk(canvas, self.plot_canvas, pack_toolbar=False)
            toolbar.update()

            # Pack the canvas and the toolbar
            toolbar.pack(side="top", fill="x", expand=False)
            canvas.get_tk_widget().pack(side="top", fill="both", expand=True)

        except Exception as e:
            self.log_message("System", f"Error displaying image: {e}")


    def _add_flowchart_step(self, data):
        """Adds a new step to the flowchart visualization with dynamic width and connecting arrows."""
        tool_name = data.get('tool_name', 'N/A')
        output_variable = data.get('output_variable', 'N/A')
        action_id = data.get('action_id', 'N/A')
        canvas = self.flowchart_canvas

        # --- Dynamic Width Calculation ---
        font_bold = ctk.CTkFont(family="Arial", size=12, weight="bold")
        text_content = f"{action_id}: {tool_name}"
        text_width = font_bold.measure(text_content)

        padding = 30  # 15px padding on each side
        dynamic_block_width = max(self.flowchart_block_width, text_width + padding)

        # --- Position Calculation ---
        x1 = self.flowchart_x_offset
        y1 = self.flowchart_y_offset
        x2 = x1 + dynamic_block_width
        y2 = y1 + self.flowchart_block_height

        # --- Draw Block ---
        rect_id = canvas.create_rectangle(x1, y1, x2, y2, fill="#4a5568", outline="#63b3ed", width=2)
        self.flowchart_blocks[rect_id] = data

        # --- Arrow Drawing ---
        if self.last_flowchart_rect_id is not None:
            # last_coords = canvas.coords(self.last_flowchart_rect_id)
            arrow_color = "#63b3ed"

            if y1 == self.last_coords[1]:  # Same row
                start_x = self.last_coords[2]
                start_y = self.last_coords[1] + self.flowchart_block_height / 2
                end_x = x1
                end_y = y1 + self.flowchart_block_height / 2
                canvas.create_line(start_x, start_y, end_x, end_y, fill=arrow_color, width=1.5, arrow='last')
            else:  # New row
                # For a new row, draw a vertical line down, then horizontal, then vertical up to the new block
                start_x = self.last_coords[2] - ( (self.last_coords[2] - self.last_coords[0]) / 2 )
                start_y = self.last_coords[3]

                # The point where the line turns from down to right
                turn_y = start_y + self.flowchart_vertical_spacing / 2

                # End point at the top-middle of the new block
                end_x = x1 + dynamic_block_width / 2
                end_y = y1

                # Draw the arrow segments
                canvas.create_line(start_x, start_y, start_x, turn_y, fill=arrow_color, width=1.5) # Down
                canvas.create_line(start_x, turn_y, end_x, turn_y, fill=arrow_color, width=1.5) # Across
                canvas.create_line(end_x, turn_y, end_x, end_y, fill=arrow_color, width=1.5, arrow='last') # Up

        # --- Add Text & Bind Events ---
        text_tool_id = canvas.create_text(x1 + dynamic_block_width / 2, y1 + self.flowchart_block_height / 3,
                                           text=text_content, fill="white", font=font_bold)
        text_output_id = canvas.create_text(x1 + dynamic_block_width / 2, y1 + 2 * self.flowchart_block_height / 3,
                                           text=f"Output: {output_variable}", fill="#a0aec0", font=("Arial", 9))

        block_tag = f"block_{rect_id}"
        canvas.addtag_withtag(block_tag, rect_id)
        canvas.addtag_withtag(block_tag, text_tool_id)
        canvas.addtag_withtag(block_tag, text_output_id)
        canvas.tag_bind(block_tag, "<Button-1>", lambda event, r_id=rect_id: self._on_flowchart_click(event, r_id))

        # --- Update for Next Block ---
        self.last_flowchart_rect_id = rect_id
        self.last_coords = [x1, y1, x2, y2]
        self.flowchart_x_offset += dynamic_block_width + self.flowchart_horizontal_spacing

        image_path = data.get('image_path')
        # --- Display the plot for the added step ---
        self._display_image_on_plot_canvas(image_path)

        if self.flowchart_x_offset + dynamic_block_width > canvas.winfo_width() and canvas.winfo_width() > 0:
            self.flowchart_x_offset = 10
            self.flowchart_y_offset += self.flowchart_block_height + self.flowchart_vertical_spacing

            if self.flowchart_y_offset + self.flowchart_block_height > 1000:#canvas.winfo_height():
                self.log_message("System", "Flowchart content exceeds canvas height.")

    def _on_flowchart_click(self, event, rect_id):
        """Handles click events on flowchart blocks to display their associated plot."""
        if rect_id in self.flowchart_blocks:
            action_data = self.flowchart_blocks[rect_id]
            action_id = action_data.get('action_id')

            # The orchestrator instance is needed to get the run_id
            if not hasattr(self, 'orchestrator') or self.orchestrator is None:
                self.log_message("System", "Error: Orchestrator not initialized, cannot find plots.")
                # Attempt to display a single image path if it exists from older runs
                image_path = action_data.get('image_path')
                if image_path and isinstance(image_path, str):
                     self._display_image_on_plot_canvas(image_path)
                return

            run_id = self.orchestrator.run_id
            run_dir = f"./run_state/{run_id}"

            # The first step (ID 0) is special, its plot name is different
            if action_id == 0:
                plot_prefix = f"step_{action_id}_input_image"
            else:
                plot_prefix = f"step_{action_id}_"

            try:
                if not os.path.exists(run_dir):
                    self.log_message("System", f"Error: Run directory not found at {run_dir}")
                    return
                all_files = os.listdir(run_dir)
                image_files = [os.path.join(run_dir, f) for f in all_files if f.startswith(plot_prefix) and f.endswith('.png')]
            except Exception as e:
                self.log_message("System", f"Error accessing run directory: {e}")
                image_files = []

            if len(image_files) == 1:
                # self.log_message("Flowchart", f"Displaying plot for {action_data.get('tool_name')} (Action ID: {action_id})")
                self._display_image_on_plot_canvas(image_files[0])
            elif len(image_files) > 1:
                self._show_plot_selection_menu(event, image_files, action_data)
            else:
                # Fallback to the original image_path if no files are found by prefix
                image_path = action_data.get('image_path')
                if image_path and isinstance(image_path, str) and os.path.exists(image_path):
                     self._display_image_on_plot_canvas(image_path)
                else:
                    self.log_message("Flowchart", f"No plot available for {action_data.get('tool_name')} (Action ID: {action_id}). Searched for files starting with '{plot_prefix}' in {run_dir}.")
        else:
            self.log_message("Flowchart", "Clicked item not associated with a known action block.")

    def _show_plot_selection_menu(self, event, image_paths, action_data):
        """Creates a dropdown menu to select a plot at the click location."""
        # Destroy any existing menu first
        for widget in self.flowchart_canvas.winfo_children():
            if isinstance(widget, ctk.CTkOptionMenu):
                widget.destroy()

        menu = ctk.CTkOptionMenu(
            self.flowchart_canvas,
            values=[os.path.basename(p) for p in image_paths],
            command=lambda choice: self._display_selected_plot(choice, image_paths, action_data, menu)
        )
        menu.place(x=event.x, y=event.y)

    def _display_selected_plot(self, choice, image_paths, action_data, menu):
        """Displays the selected plot and removes the dropdown."""
        selected_path = next((p for p in image_paths if os.path.basename(p) == choice), None)
        if selected_path:
            # self.log_message("Flowchart", f"Displaying plot {choice} for {action_data.get('tool_name')} (Action ID: {action_data.get('action_id')})")
            self._display_image_on_plot_canvas(selected_path)

        menu.destroy()
