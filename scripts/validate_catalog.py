# /// script
# dependencies = []
# ///

import os
import sys
import json
import tempfile
import subprocess
import time
import urllib.request
import urllib.error

sys.stdout.reconfigure(encoding='utf-8')

def check_backend_alive(url="http://localhost:8080/api/health") -> bool:
    try:
        with urllib.request.urlopen(url, timeout=1.0) as response:
            if response.status == 200:
                data = json.loads(response.read().decode('utf-8'))
                return data.get("ok") == "true"
    except Exception:
        pass
    return False

def split_test_code(test_code: str):
    lines = test_code.splitlines()
    imports = []
    other_lines = []
    in_import_block = False
    for line in lines:
        stripped = line.strip()
        if not stripped:
            other_lines.append(line)
            continue
            
        if stripped.startswith("import"):
            if "(" in stripped:
                in_import_block = True
            else:
                # e.g. import "math" -> "math"
                imp_val = stripped.replace("import", "").strip()
                imports.append(imp_val)
        elif in_import_block:
            if ")" in stripped:
                in_import_block = False
            else:
                imports.append(stripped)
        else:
            other_lines.append(line)
    return imports, "\n".join(other_lines)

def run_local_compile(solution_code: str, test_code: str) -> tuple[bool, str]:
    """Compiles and runs the solution and tests locally using the host's Go installation."""
    # Ensure solution code has package main
    if "package main" not in solution_code:
        solution_code = "package main\n" + solution_code

    imports, remaining_test = split_test_code(test_code)
    
    # Merge default imports with test imports
    default_imports = ['"fmt"', '"reflect"']
    for imp in imports:
        imp_clean = imp.strip()
        if imp_clean and imp_clean not in default_imports:
            default_imports.append(imp_clean)
            
    # Build judge.go contents
    judge_lines = [
        "package main",
        "import (",
    ]
    for imp in default_imports:
        judge_lines.append(f"    {imp}")
    judge_lines.append(")")
    judge_lines.append("")
    judge_lines.append('func assertEqual(got, want any){ if !reflect.DeepEqual(got,want){ panic(fmt.Sprintf("got %#v, want %#v", got, want)) } }')
    judge_lines.append("")
    judge_lines.append(remaining_test)
    
    judge_code = "\n".join(judge_lines)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        main_file = os.path.join(tmpdir, "main.go")
        judge_file = os.path.join(tmpdir, "judge.go")
        
        with open(main_file, "w", encoding="utf-8") as f:
            f.write(solution_code)
        with open(judge_file, "w", encoding="utf-8") as f:
            f.write(judge_code)
            
        try:
            # Compile and run
            res = subprocess.run(
                ["go", "run", "main.go", "judge.go"],
                cwd=tmpdir,
                capture_output=True,
                text=True,
                timeout=5.0
            )
            if res.returncode == 0:
                out = res.stdout.strip() or "All tests passed."
                return True, out
            else:
                err = res.stderr.strip() or res.stdout.strip() or "Compilation/Execution failed"
                return False, err
        except subprocess.TimeoutExpired:
            return False, "Execution timed out (5s)"
        except Exception as e:
            return False, f"Runner error: {str(e)}"

def run_backend_submit(problem_id: str, code: str) -> tuple[bool, str]:
    url = "http://localhost:8080/api/run"
    payload = json.dumps({
        "problemId": problem_id,
        "code": code,
        "mode": "submit"
    }).encode("utf-8")
    
    req = urllib.request.Request(
        url,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    
    try:
        with urllib.request.urlopen(req, timeout=5.0) as response:
            if response.status == 200:
                res_data = json.loads(response.read().decode("utf-8"))
                verdict = res_data.get("verdict")
                output = res_data.get("output", "")
                err = res_data.get("error", "")
                
                if verdict == "Accepted":
                    return True, output
                else:
                    return False, f"Verdict: {verdict}\nError: {err}\nOutput: {output}"
            else:
                return False, f"HTTP Error {response.status}"
    except urllib.error.HTTPError as e:
        try:
            err_msg = e.read().decode("utf-8")
            return False, f"HTTP Error {e.code}: {err_msg}"
        except Exception:
            return False, f"HTTP Error {e.code}"
    except Exception as e:
        return False, f"Backend connection failed: {str(e)}"

def main():
    print("====================================================================")
    print("      GOPRAC / LEARNING PLATFORM - PROBLEM CATALOG VALIDATOR       ")
    print("====================================================================")
    
    catalog_path = "data/problems.json"
    if not os.path.exists(catalog_path):
        print(f"[!] Error: Catalog file not found at: {catalog_path}")
        print("    Please run the ingestion script first to generate it.")
        sys.exit(1)
        
    print(f"[*] Reading problem catalog from '{catalog_path}'...")
    try:
        with open(catalog_path, "r", encoding="utf-8") as f:
            catalog = json.load(f)
    except Exception as e:
        print(f"[!] Failed to parse JSON catalog: {e}")
        sys.exit(1)
        
    metadata = catalog.get("metadata", {})
    chapters = catalog.get("chapters", [])
    problems = catalog.get("problems", [])
    
    print(f"[✓] Catalog Metadata: '{metadata.get('title', 'Unknown')}' - {metadata.get('subtitle', '')}")
    print(f"[✓] Loaded {len(chapters)} chapters and {len(problems)} exercises.")
    
    backend_alive = check_backend_alive()
    if backend_alive:
        print("[*] Detected running GoPrac Backend server at http://localhost:8080")
        print("[*] Will validate via backend API first, falling back to local compilation if sandbox is unavailable.")
    else:
        print("[*] GoPrac Backend server not running at http://localhost:8080")
        print("[*] Validating all exercises locally on the host using the local Go compiler.")
        
    print("\n--- Starting Verification ---")
    
    passed_count = 0
    failed_count = 0
    start_time = time.time()
    
    for p in problems:
        p_id = p.get("id")
        p_title = p.get("title", f"Exercise {p.get('number')}")
        p_mode = p.get("exerciseMode", "judge")
        p_verifier = p.get("verifier", "local-tests")
        
        print(f"\n* Verifying {p_title} ({p_id})...")
        
        if p_mode != "judge" or p_verifier != "local-tests":
            print(f"  [-] Skipping: Non-judgeable or manual verification exercise.")
            continue
            
        solution_code = p.get("solutionCode")
        test_code = p.get("testCode")
        
        if not solution_code or not test_code:
            print("  [✗] FAILED: Missing solutionCode or testCode in catalog!")
            failed_count += 1
            continue
            
        success = False
        message = ""
        method_used = ""
        
        # 1. Try backend submit if backend is alive
        if backend_alive:
            try:
                success, message = run_backend_submit(p_id, solution_code)
                method_used = "GoPrac Docker Sandbox Backend"
                
                # If it failed due to sandbox engine missing, fall back to local compile
                if not success and "sandbox runtime unavailable" in message:
                    print("  [!] Backend sandbox unavailable. Falling back to local host compilation...")
                    success, message = run_local_compile(solution_code, test_code)
                    method_used = "Local Host Go Compiler (Fallback)"
            except Exception as e:
                print(f"  [!] Backend error: {e}. Falling back to local host compilation...")
                success, message = run_local_compile(solution_code, test_code)
                method_used = "Local Host Go Compiler (Fallback)"
        else:
            # 2. Local compile directly
            success, message = run_local_compile(solution_code, test_code)
            method_used = "Local Host Go Compiler"
            
        if success:
            print(f"  [✓] PASSED (via {method_used})")
            passed_count += 1
        else:
            print(f"  [✗] FAILED (via {method_used})")
            print("  --- Error Output ---")
            for line in message.splitlines():
                print(f"    {line}")
            print("  --------------------")
            failed_count += 1
            
    duration = time.time() - start_time
    print("\n====================================================================")
    print("                          VERIFICATION SUMMARY                      ")
    print("====================================================================")
    print(f"  Total Exercises Checked : {passed_count + failed_count}")
    print(f"  Passed Exercises       : {passed_count}")
    print(f"  Failed Exercises       : {failed_count}")
    print(f"  Total Duration         : {duration:.2f} seconds")
    print("====================================================================")
    
    if failed_count > 0:
        print("[!] Validation failed. Please review errors and correct exercise code.")
        sys.exit(1)
    else:
        print("[✓] Perfect! All judgeable exercises compiled and passed successfully!")
        sys.exit(0)

if __name__ == "__main__":
    main()
