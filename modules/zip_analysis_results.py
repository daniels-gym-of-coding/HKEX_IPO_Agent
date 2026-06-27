import os
import zipfile
import glob

def zip_analysis_results(filings_dir: str = "filings", output_filename: str = "analysis_results.zip") -> None:
    """
    Finds all individual filing analysis files (*-analysis.txt) in the filings directory
    and packages them into a single zip archive.

    Args:
        filings_dir: Directory containing individual filing analyses.
        output_filename: Name of the resulting zip file to be created in the root.
    """
    # Normalize paths
    current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    if not os.path.isabs(filings_dir):
        abs_filings_dir = os.path.join(current_dir, filings_dir)
    else:
        abs_filings_dir = filings_dir

    if not os.path.isabs(output_filename):
        abs_output_path = os.path.join(current_dir, output_filename)
    else:
        abs_output_path = output_filename

    # Search for all *-analysis.txt files
    search_pattern = os.path.join(abs_filings_dir, "*-analysis.txt")
    analysis_files = glob.glob(search_pattern)

    if not analysis_files:
        print(f"No analysis files (*-analysis.txt) found in {abs_filings_dir}. Nothing to zip.")
        return

    print(f"Found {len(analysis_files)} analysis files. Zipping them into '{abs_output_path}'...")

    try:
        with zipfile.ZipFile(abs_output_path, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for file_path in sorted(analysis_files):
                arcname = os.path.basename(file_path)
                zip_file.write(file_path, arcname=arcname)
                print(f"Added {arcname} to zip.")
        print(f"Successfully created zip archive: {output_filename}")
    except Exception as e:
        print(f"Error creating zip archive: {e}")
