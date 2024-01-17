This script is designed to configure a "blank" server for specific purposes. 

This includes:
- setting an available IP address.
- setting an available hostname.
- installing necessary packages.

The script can be:
- executed interactively (invoked without parameters).
- executed with console output but without interaction (invoked with "-a" or "--automatic").
- executed silently (invoked with "-s" or "--silent").

LIMITS
- The script must be executed as root. 
- The script should not be executed in a shared Windows folder, as a Python environment cannot be set up there.
