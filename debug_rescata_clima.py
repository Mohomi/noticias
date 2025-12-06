from conecta import rescata_clima
import sys

def debug_direct():
    print("🧪 Debugging rescata_clima() directly...")
    try:
        result = rescata_clima(1)
        print(f"Success: {result.get('success')}")
        print(f"Message: {result.get('message')}")
        print(f"Updated: {result.get('updated')}")
    except Exception as e:
        print(f"❌ Exception: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_direct()
