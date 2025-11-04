"""
Test script to verify PostgreSQL database integration
"""

import os
from dotenv import load_dotenv
from database import (
    init_database, 
    save_claim_to_history, 
    get_all_history,
    get_database_info,
    DATABASE_TYPE
)

# Load environment variables
load_dotenv()

def test_database_connection():
    """Test database connection and basic operations"""
    print("=" * 60)
    print("DATABASE CONNECTION TEST")
    print("=" * 60)
    
    # Show database configuration
    db_info = get_database_info()
    print(f"\n✅ Database Type: {db_info['database_type'].upper()}")
    if db_info['database_type'] == 'sqlite':
        print(f"✅ Database File: {db_info['database_file']}")
    else:
        print(f"✅ Database Host: {db_info['database_host']}")
    
    print("\n" + "-" * 60)
    print("Testing Database Operations...")
    print("-" * 60)
    
    try:
        # Initialize database
        print("\n1. Initializing database...")
        init_database()
        print("   ✅ Database initialized successfully")
        
        # Test insert
        print("\n2. Testing INSERT operation...")
        test_data = {
            "loss_type": "Test Accident",
            "severity": "Low",
            "affected_assets": "Test Asset",
            "estimated_loss": "₹5,000",
            "incident_date": "2025-11-05",
            "location": "Test Location",
            "confidence": "High",
            "extraction_explanation": "Test explanation"
        }
        
        claim_id = save_claim_to_history("Test claim description", test_data)
        print(f"   ✅ Claim saved with ID: {claim_id}")
        
        # Test retrieve
        print("\n3. Testing SELECT operation...")
        history = get_all_history(limit=5)
        print(f"   ✅ Retrieved {len(history)} records")
        
        if history:
            print("\n   Latest claim:")
            latest = history[0]
            print(f"   - ID: {latest.get('id')}")
            print(f"   - Loss Type: {latest.get('loss_type')}")
            print(f"   - Severity: {latest.get('severity')}")
            print(f"   - Timestamp: {latest.get('timestamp')}")
        
        print("\n" + "=" * 60)
        print("✅ ALL TESTS PASSED!")
        print("=" * 60)
        
        if DATABASE_TYPE == "postgresql":
            print("\n🎉 PostgreSQL (Supabase) connection successful!")
        else:
            print("\n📁 SQLite database working correctly!")
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    test_database_connection()
