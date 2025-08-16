#!/usr/bin/env python3
"""Debug script to verify efinance parameter transformation and call flow."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def debug_efinance_flow():
    """Debug the efinance parameter transformation and call flow."""
    
    print("🔍 Debugging efinance parameter transformation flow...")
    print("=" * 60)
    
    # Test 1: Check parameter transformation
    try:
        from ak_unified.registry_v2 import _efinance_ohlcv_params
        print("✅ Successfully imported _efinance_ohlcv_params")
        
        # Test input parameters
        input_params = {"symbol": "600000.SH", "start": "2024-01-01", "end": "2024-01-31"}
        print(f"📥 Input params: {input_params}")
        
        # Transform parameters
        transformed_params = _efinance_ohlcv_params(input_params)
        print(f"🔄 Transformed params: {transformed_params}")
        
        # Verify transformation
        expected_symbol = "600000"
        expected_start = "20240101"
        expected_end = "20240131"
        
        if transformed_params["symbol"] != expected_symbol:
            print(f"❌ Symbol transformation failed: expected '{expected_symbol}', got '{transformed_params['symbol']}'")
        else:
            print(f"✅ Symbol transformation: {input_params['symbol']} → {transformed_params['symbol']}")
            
        if transformed_params["start"] != expected_start:
            print(f"❌ Start date transformation failed: expected '{expected_start}', got '{transformed_params['start']}'")
        else:
            print(f"✅ Start date transformation: {input_params['start']} → {transformed_params['start']}")
            
        if transformed_params["end"] != expected_end:
            print(f"❌ End date transformation failed: expected '{expected_end}', got '{transformed_params['end']}'")
        else:
            print(f"✅ End date transformation: {input_params['end']} → {transformed_params['end']}")
            
    except Exception as e:
        print(f"❌ Parameter transformation test failed: {e}")
        return False
    
    print("\n" + "=" * 60)
    
    # Test 2: Check efinance adapter import
    try:
        from ak_unified.adapters.efinance_adapter import _import_efinance
        print("✅ Successfully imported efinance adapter")
        
        # Try to import efinance library
        try:
            ef = _import_efinance()
            print("✅ Successfully imported efinance library")
            
            # Check if we can access the stock module
            if hasattr(ef, 'stock'):
                print("✅ efinance.stock module available")
                
                # Check if get_quote_history method exists
                if hasattr(ef.stock, 'get_quote_history'):
                    print("✅ efinance.stock.get_quote_history method available")
                else:
                    print("❌ efinance.stock.get_quote_history method not found")
            else:
                print("❌ efinance.stock module not available")
                
        except Exception as e:
            print(f"❌ Failed to import efinance library: {e}")
            return False
            
    except Exception as e:
        print(f"❌ efinance adapter import test failed: {e}")
        return False
    
    print("\n" + "=" * 60)
    
    # Test 3: Check registry_v2 configuration
    try:
        from ak_unified.registry_v2 import REGISTRY_V2
        print("✅ Successfully imported REGISTRY_V2")
        
        # Check ohlcva_daily dataset
        dsid = "securities.equity.cn.ohlcva_daily"
        if dsid in REGISTRY_V2:
            dataset = REGISTRY_V2[dsid]
            print(f"✅ Found dataset: {dsid}")
            print(f"   Category: {dataset.category}")
            print(f"   Domain: {dataset.domain}")
            print(f"   Providers count: {len(dataset.providers)}")
            
            # Check efinance provider
            efinance_provider = None
            for provider in dataset.providers:
                if provider.adapter == "efinance":
                    efinance_provider = provider
                    break
            
            if efinance_provider:
                print("✅ Found efinance provider")
                print(f"   API ID: {efinance_provider.api_id}")
                print(f"   Has param_transform: {efinance_provider.param_transform is not None}")
                if efinance_provider.param_transform:
                    print(f"   Param transform function: {efinance_provider.param_transform.__name__}")
            else:
                print("❌ efinance provider not found")
                
        else:
            print(f"❌ Dataset not found: {dsid}")
            print(f"   Available datasets: {list(REGISTRY_V2.keys())}")
            
    except Exception as e:
        print(f"❌ Registry_v2 configuration test failed: {e}")
        return False
    
    print("\n" + "=" * 60)
    
    # Test 4: Simulate the actual call flow
    try:
        print("🧪 Simulating actual call flow...")
        
        # Simulate the parameter transformation
        input_params = {"symbol": "600000.SH", "start": "2024-01-01", "end": "2024-01-31"}
        transformed_params = _efinance_ohlcv_params(input_params)
        
        print(f"📥 Original params: {input_params}")
        print(f"🔄 Transformed params: {transformed_params}")
        
        # Check if the transformed params would work with efinance
        symbol = transformed_params.get('symbol')
        start = transformed_params.get('start')
        end = transformed_params.get('end')
        
        print(f"🔍 Final parameters for efinance call:")
        print(f"   symbol: '{symbol}' (type: {type(symbol)})")
        print(f"   start: '{start}' (type: {type(start)})")
        print(f"   end: '{end}' (type: {type(end)})")
        
        # Validate parameters
        if not symbol:
            print("❌ Symbol is empty or None")
        elif len(symbol) != 6:
            print(f"❌ Symbol length is {len(symbol)}, expected 6")
        else:
            print("✅ Symbol format looks correct")
            
        if not start:
            print("❌ Start date is empty or None")
        elif len(start) != 8:
            print(f"❌ Start date length is {len(start)}, expected 8")
        else:
            print("✅ Start date format looks correct")
            
        if not end:
            print("❌ End date is empty or None")
        elif len(end) != 8:
            print(f"❌ End date length is {len(end)}, expected 8")
        else:
            print("✅ End date format looks correct")
            
    except Exception as e:
        print(f"❌ Call flow simulation failed: {e}")
        return False
    
    print("\n" + "=" * 60)
    print("🎯 Debug summary:")
    print("If all tests passed, the parameter transformation should work correctly.")
    print("If efinance still returns empty data, the issue might be:")
    print("1. efinance library cannot fetch data for the given symbol/date range")
    print("2. Network issues or API rate limiting")
    print("3. Data format issues in the response")
    
    return True

if __name__ == "__main__":
    debug_efinance_flow()