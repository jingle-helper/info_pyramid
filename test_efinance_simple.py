#!/usr/bin/env python3
"""Simple test script to verify efinance library functionality."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_efinance_basic():
    """Test basic efinance functionality."""
    
    print("🧪 Testing efinance library basic functionality...")
    print("=" * 50)
    
    try:
        # Test 1: Import efinance
        print("📦 Testing efinance import...")
        from ak_unified.adapters.efinance_adapter import _import_efinance
        ef = _import_efinance()
        print("✅ Successfully imported efinance")
        
        # Test 2: Check stock module
        print("\n📊 Testing stock module...")
        if hasattr(ef, 'stock'):
            print("✅ efinance.stock module available")
            
            # Test 3: Check get_quote_history method
            if hasattr(ef.stock, 'get_quote_history'):
                print("✅ efinance.stock.get_quote_history method available")
                
                # Test 4: Try to get data for a simple case
                print("\n🔍 Testing data retrieval...")
                print("   This might take a moment...")
                
                try:
                    # Try with a simple symbol and recent date
                    df = ef.stock.get_quote_history("600000", beg="20240101", end="20240131", klt=101)
                    
                    if isinstance(df, type(None)):
                        print("❌ efinance returned None")
                    elif hasattr(df, 'empty') and df.empty:
                        print("❌ efinance returned empty DataFrame")
                        print("   This might indicate:")
                        print("   - No data for the specified date range")
                        print("   - Network connectivity issues")
                        print("   - API rate limiting")
                        print("   - Invalid symbol format")
                    else:
                        print("✅ efinance returned data")
                        print(f"   Data shape: {df.shape}")
                        print(f"   Columns: {list(df.columns)}")
                        if hasattr(df, 'head'):
                            print(f"   First few rows:")
                            print(df.head())
                        
                except Exception as e:
                    print(f"❌ efinance.get_quote_history failed: {e}")
                    print("   This might indicate:")
                    print("   - Network connectivity issues")
                    print("   - API rate limiting")
                    print("   - Invalid parameters")
                    
            else:
                print("❌ efinance.stock.get_quote_history method not found")
        else:
            print("❌ efinance.stock module not available")
            
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        return False
    
    print("\n" + "=" * 50)
    print("🎯 Test summary:")
    print("If efinance returned data, the library is working correctly.")
    print("If efinance returned empty data or failed, the issue might be:")
    print("1. Network connectivity problems")
    print("2. API rate limiting")
    print("3. No data available for the specified parameters")
    print("4. Invalid symbol format")
    
    return True

if __name__ == "__main__":
    test_efinance_basic()