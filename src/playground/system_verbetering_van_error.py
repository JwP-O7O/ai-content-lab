import subprocess
import shutil
import sys


def run_ruff(directory="."):
    """Runs ruff and handles potential errors more robustly."""
    try:
        if not shutil.which("ruff"):
            return {
                "success": False,
                "error": "ruff not found. Please ensure ruff is installed and in your PATH.",
            }

        result = subprocess.run(
            ["ruff", "check", directory],
            capture_output=True,
            text=True,
            check=False,  # Don't raise exception on non-zero exit code, we'll handle it
            timeout=60,  # Added timeout for robustness
        )

        if result.returncode != 0:
            return {
                "success": False,
                "error": f"ruff failed with exit code {result.returncode}.\nStderr: {result.stderr}\nStdout: {result.stdout}",
            }
        else:
            return {"success": True, "stdout": result.stdout}

    except subprocess.TimeoutExpired:
        return {"success": False, "error": "ruff check timed out."}
    except FileNotFoundError:
        return {"success": False, "error": "ruff executable not found."}
    except PermissionError:
        return {"success": False, "error": "Permission denied when running ruff."}
    except OSError as e:  # Catch other OS-related errors (e.g., environment issues)
        return {"success": False, "error": f"OS error occurred while running ruff: {e}"}
    except Exception as e:
        return {"success": False, "error": f"An unexpected error occurred: {e}"}


if __name__ == "__main__":
    # Example usage
    result = run_ruff(".")
    if result["success"]:
        print("ruff check successful.")
        if "stdout" in result:
            print(result["stdout"])
    else:
        print(f"ruff check failed: {result['error']}")
        sys.exit(1)  # Indicate failure to the calling environment.
