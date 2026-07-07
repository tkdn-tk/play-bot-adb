import sys
import questionary
from core.adb_resolver import resolve_adb_serial
from main import interactive_select_mumu

def main():
    print("--- Test ADB Port Extraction ---")
    selected_title = interactive_select_mumu()
    
    if not selected_title:
        print("No MuMu instance selected or found.")
        return
        
    print(f"\nSelected: {selected_title}")
    
    # Create a mock config to pass to resolve_adb_serial
    mock_config = {
        "emulator_window_title": selected_title,
        "adb": {}
    }
    
    serial = resolve_adb_serial(mock_config)
    print(f"\nResult: ADB Serial / Port extracted is -> {serial}")

if __name__ == "__main__":
    main()
