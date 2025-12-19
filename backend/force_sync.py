import asyncio
from api.sync import perform_account_sync

print("--- Forcing Manual Sync with HTS ---")
try:
    # Run the core sync function we refactored
    result = perform_account_sync()
    print("\n--- Sync Result ---")
    print(result)
except Exception as e:
    print(f"\n❌ Error during sync: {e}")
