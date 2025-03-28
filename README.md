# AutopsyTool

**AutopsyTool** is a modular, automated PDF processing application designed to streamline tasks like batch PDF processing, merging, and compression. Built using PySide6, the tool features a modern, theme-switchable interface that adapts to both dark and light modes. In addition, the configuration editor allows you to synchronize working directories and dynamically slice output file names across multiple batches.

## Features

- **Batch PDF Processing:**  
  Configure and merge multiple PDFs in batches based on user-defined settings such as file patterns, page inclusion/exclusion, and merge order.  
  *Supports dynamic synchronization of working directories and output file name slicing across batches.*

- **PDF Merging:**  
  Select multiple PDF files, preview pages with inclusion checkboxes, rearrange the order, and merge selected pages into a single PDF.

- **PDF Compression:**  
  Compress PDF files by adjusting compression quality for embedded images while receiving live progress updates.

- **Dynamic Theming:**  
  Switch between dark and light themes at runtime using a dedicated theme control in the dashboard.

## Project Structure

```
AutopsyTool/
├── autopsy/
│   ├── __init__.py
│   ├── assets/
│   │   └── autopsy.ico          # Application icon
│   ├── core/
│   │   ├── __init__.py
│   │   ├── pdf_batch_core.py     # Core business logic for batch PDF processing
│   │   ├── pdf_merge_core.py     # Core merging logic for PDFs
│   │   ├── pdf_compress_core.py  # Core compression logic for PDFs
│   │   └── pdf_split_core.py     # Core splitting logic for PDFs
│   ├── ui/
│   │   ├── __init__.py
│   │   ├── dashboard.py          # Main dashboard with theme switcher and tool launchers
│   │   ├── about_dialog.py       # About dialog with project and developer info
│   │   ├── pdf_batch_tool.py     # UI for Batch PDF Processing (with config editor and sync feature)
│   │   ├── pdf_merge_tool.py     # UI for PDF Merging
│   │   ├── pdf_compress_tool.py  # UI for PDF Compression
│   │   ├── pdf_convert_tool.py   # UI for PDF Conversion (to DOCX, PPT, or Images)
│   │   └── pdf_split_tool.py     # UI for PDF Splitting
│   └── utils.py                 # Helper functions (e.g., resource_path)
├── dark.qss                     # Dark theme stylesheet
├── light.qss                    # Light theme stylesheet
├── config.json                  # Sample configuration file for batch processing
├── requirements.txt             # Python package dependencies
└── run.py                       # Entry point to launch the application
```

## Installation

1. **Clone the Repository:**

   ```bash
   git clone <repository_url>
   cd AutopsyTool
   ```

2. **Create and Activate a Virtual Environment:**

   - **On Windows:**
     ```bash
     python -m venv venv
     venv\Scripts\activate
     ```
   - **On macOS/Linux:**
     ```bash
     python3 -m venv venv
     source venv/bin/activate
     ```

3. **Install Dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. **Run the Application:**

   ```bash
   python run.py
   ```

2. **Dashboard Overview:**

   - **Tool Launchers:**  
     Use the buttons on the dashboard to launch the Automation (Batch PDF Processing), PDF Merger, PDF Compression, PDF Conversion, and PDF Split tools.

   - **Theme Switching:**  
     Use the theme switch button (located in the header area) to toggle between dark and light modes. The global stylesheet is applied so that all tool windows reflect the chosen theme.

3. **Batch PDF Processing:**
   - **Configuration:**  
     Configure batches by selecting working directories, output names, and file patterns.  
     The Edit Config window provides a sync feature to update the working directory of batch 1 across all batches. It also supports slicing the output file names (using positive or negative slice indices) to synchronize a specific part (for example, the customer code).
   - **Saving Configurations:**  
     Save your configuration to a JSON file for later use.

4. **PDF Merging:**  
   Select PDFs, preview page thumbnails, include/exclude pages via checkboxes, rearrange the order using move up/down buttons, and merge the selected pages.

5. **PDF Compression:**  
   Select a PDF, adjust the compression quality using the slider, and monitor the progress via a progress bar.

6. **PDF Conversion:**  
   Convert PDFs to DOCX, PPT, or image files. For image conversion, you can select the output format (JPG, PNG, or BMP).

7. **PDF Splitting:**  
   Split a PDF using one of three modes: every page, after specific pages, or in chunks of N pages.

## Contributing

This project is for personal use and is not publicly open for contribution.

## License

This project is for personal use and is not publicly licensed.

## Contact

For any questions or feedback, please contact [Raja Gupta](mailto:erRaja97@gmail.com).

---