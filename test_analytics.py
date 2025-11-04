#!/usr/bin/env python3
"""Test analytics data retrieval"""

from database import get_analytics_data, get_all_history, get_database_info

print("=" * 60)
print("ANALYTICS DATA TEST")
print("=" * 60)

# Database info
db_info = get_database_info()
print(f"\nDatabase Type: {db_info['database_type']}")
if db_info['database_host']:
    print(f"Database Host: {db_info['database_host']}")

# Get history count
print("\n" + "-" * 60)
history = get_all_history(limit=5)
print(f"History records: {len(history)}")

if history:
    print("\nLatest record:")
    latest = history[0]
    print(f"  ID: {latest.get('id')}")
    print(f"  Loss Type: {latest.get('loss_type')}")
    print(f"  Timestamp: {latest.get('timestamp')}")
    print(f"  Timestamp type: {type(latest.get('timestamp'))}")

# Get analytics
print("\n" + "-" * 60)
print("Testing analytics data...")
try:
    analytics = get_analytics_data()
    print(f"\n✅ Analytics loaded successfully!")
    print(f"  Total claims: {analytics['total_claims']}")
    print(f"  Loss types: {len(analytics['loss_type_distribution'])}")
    print(f"  Severity levels: {len(analytics['severity_distribution'])}")
    print(f"  Confidence levels: {len(analytics['confidence_distribution'])}")
    print(f"  Claims over time records: {len(analytics['claims_over_time'])}")
    
    if analytics['claims_over_time']:
        print(f"\n  Sample time record:")
        sample = analytics['claims_over_time'][0]
        print(f"    Date: {sample.get('date')}")
        print(f"    Date type: {type(sample.get('date'))}")
        print(f"    Count: {sample.get('count')}")
    
    print("\n" + "=" * 60)
    print("✅ ALL TESTS PASSED!")
    print("=" * 60)
    
except Exception as e:
    print(f"\n❌ ERROR: {str(e)}")
    import traceback
    traceback.print_exc()
