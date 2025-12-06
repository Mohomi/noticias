from conecta import rescata_clima

def test_direct():
    print("🧪 Testing rescata_clima() directly...")
    try:
        result = rescata_clima(1)
        print(f"Result: {result}")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_direct()
