# ui.py

import subprocess

def main():
    print("\n=== Prompt Suggestion System (Python UI) ===")
    query = input("Enter your topic or a short question:\n> ").strip()

    if not query:
        print("No input. Exiting.")
        return

    # Build command to call backend
    command = ["python", "python_backend.py", query]

    print("\nGetting suggestions...\n")

    try:
        # Run backend
        result = subprocess.run(command, capture_output=True, text=True)
        output = result.stdout.strip()

        if not output:
            print("No suggestions returned. Make sure the backend ran correctly.")
            return

        # Split output into lines and print one by one
        print("--- Suggestions ---")
        for idx, line in enumerate(output.splitlines(), 1):
            print(f"{line.strip()}")
        print("--- End ---\n")

    except Exception as e:
        print("Error running backend:", e)

if __name__ == "__main__":
    main()
