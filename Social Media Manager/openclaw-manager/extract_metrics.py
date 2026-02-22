import os
import json
import re
import sys

def extract_metrics(reports_dir):
    metrics = {
        "area_mm2": 0.0,
        "power_mw": 0.0,
        "slack_ns": 0.0,
        "drc_violations": 0
    }

    # Common patterns for extraction
    patterns = {
        "area": re.compile(r"Chip area for module.*:\s*([\d\.]+)"),
        "power": re.compile(r"Total Power\s*=\s*([\d\.e\-]+)\s*W"),
        "slack": re.compile(r"worst slack\s*([\d\.\-]+)"),
        "drc": re.compile(r"violation count\s*([\d]+)")
    }

    collected_files = []
    for root, dirs, files in os.walk(reports_dir):
        for file in files:
            if file.endswith(".rpt") or file.endswith(".log") or file.endswith(".json"):
                path = os.path.join(root, file)
                collected_files.append((path, os.path.getmtime(path)))

    # Sort files by modification time descending to process newer files first
    collected_files.sort(key=lambda x: x[1], reverse=True)

    found_metrics = {k: False for k in metrics}

    for path, mtime in collected_files:
        try:
            with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                
                # Area
                if not found_metrics["area_mm2"]:
                    area_match = patterns["area"].search(content)
                    if area_match:
                        metrics["area_mm2"] = float(area_match.group(1))
                        found_metrics["area_mm2"] = True
                
                # Power (convert W to mW)
                if not found_metrics["power_mw"]:
                    power_match = patterns["power"].search(content)
                    if power_match:
                        metrics["power_mw"] = float(power_match.group(1)) * 1000
                        found_metrics["power_mw"] = True
                
                # Slack
                if not found_metrics["slack_ns"]:
                    slack_match = patterns["slack"].search(content)
                    if slack_match:
                        metrics["slack_ns"] = float(slack_match.group(1))
                        found_metrics["slack_ns"] = True
                        
                # DRC
                if not found_metrics["drc_violations"]:
                    drc_match = patterns["drc"].search(content)
                    if drc_match:
                        metrics["drc_violations"] = int(drc_match.group(1))
                        found_metrics["drc_violations"] = True
                        
            # If all found, we can stop early
            if all(found_metrics.values()):
                break
        except Exception as e:
            print(f"Error reading {path}: {e}")

    return metrics


def find_latest_completed_run(designs_dir):
    """
    Navigates designs/<name>/runs/<run_name> to find the latest run where GDS exists.
    """
    latest_run_path = None
    latest_mtime = 0
    
    if not os.path.exists(designs_dir):
        print(f"Designs directory not found: {designs_dir}")
        return None

    for design_name in os.listdir(designs_dir):
        design_path = os.path.join(designs_dir, design_name)
        if not os.path.isdir(design_path):
            continue
            
        runs_dir = os.path.join(design_path, "runs")
        if not os.path.exists(runs_dir):
            continue
            
        for run_name in os.listdir(runs_dir):
            run_path = os.path.join(runs_dir, run_name)
            if not os.path.isdir(run_path):
                continue
                
            # Check for GDS completion
            # Path pattern usually: runs/<run>/results/signoff/<design>.gds 
            # or runs/<run>/results/final/gds/<design>.gds
            gds_found = False
            results_dir = os.path.join(run_path, "results")
            if os.path.exists(results_dir):
                for root, dirs, files in os.walk(results_dir):
                    if any(f.endswith(".gds") for f in files):
                        gds_found = True
                        break
            
            if gds_found:
                mtime = os.path.getmtime(run_path)
                if mtime > latest_mtime:
                    latest_mtime = mtime
                    latest_run_path = run_path
                    
    return latest_run_path

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python extract_metrics.py <designs_directory>")
        sys.exit(1)

    designs_path = sys.argv[1]
    
    # Discovery phase
    latest_run = find_latest_completed_run(designs_path)
    
    if not latest_run:
        print("No completed GDS runs found.")
        sys.exit(1)
        
    print(f"Processing latest run: {latest_run}")
    data = extract_metrics(latest_run)
    
    # Store design name for the post
    design_name = os.path.basename(os.path.dirname(os.path.dirname(latest_run)))
    data["design_name"] = design_name
    
    # Ensure data directory exists
    os.makedirs("data/public_metrics", exist_ok=True)
    
    output_path = "data/public_metrics/latest.json"
    with open(output_path, 'w') as f:
        json.dump(data, f, indent=4)
        
    print(f"Metrics saved to {output_path}")
    print(json.dumps(data, indent=2))

