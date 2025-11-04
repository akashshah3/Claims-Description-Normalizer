"""
Test script to verify database performance optimizations
Run this locally to test connection pooling and indexes
"""

import time
from database import (
    init_database, 
    get_connection, 
    close_connection,
    get_analytics_data,
    get_all_history,
    DATABASE_TYPE
)

def test_connection_pooling():
    """Test that connections are reused from pool"""
    print("\n=== Testing Connection Pooling ===")
    
    # Get 3 connections and close them
    connections = []
    start = time.time()
    
    for i in range(3):
        conn = get_connection()
        connections.append(conn)
        print(f"  Connection {i+1} obtained")
    
    # Close all connections (should return to pool)
    for conn in connections:
        close_connection(conn)
        print(f"  Connection returned to pool")
    
    elapsed = time.time() - start
    print(f"  Total time: {elapsed:.3f}s")
    
    # Get connections again (should be faster from pool)
    start = time.time()
    for i in range(3):
        conn = get_connection()
        close_connection(conn)
    
    elapsed_pooled = time.time() - start
    print(f"  Time with pool reuse: {elapsed_pooled:.3f}s")
    print(f"  ✅ Connection pooling {'working' if elapsed_pooled < elapsed else 'may need tuning'}")

def test_indexes():
    """Test that indexes improve query performance"""
    print("\n=== Testing Index Performance ===")
    
    if DATABASE_TYPE != "postgresql":
        print("  ⚠️  Skipping (only relevant for PostgreSQL)")
        return
    
    conn = get_connection()
    cursor = conn.cursor()
    
    # Check if indexes exist
    cursor.execute("""
        SELECT indexname 
        FROM pg_indexes 
        WHERE tablename = 'claim_history'
    """)
    indexes = [row[0] for row in cursor.fetchall()]
    
    print(f"  Found {len(indexes)} indexes:")
    for idx in indexes:
        print(f"    - {idx}")
    
    expected = [
        'idx_claim_history_timestamp',
        'idx_claim_history_loss_type', 
        'idx_claim_history_severity'
    ]
    
    missing = [idx for idx in expected if idx not in indexes]
    if missing:
        print(f"  ⚠️  Missing indexes: {missing}")
    else:
        print(f"  ✅ All expected indexes present")
    
    close_connection(conn)

def test_query_performance():
    """Test query execution time"""
    print("\n=== Testing Query Performance ===")
    
    # Test analytics query (complex with multiple GROUP BY)
    start = time.time()
    analytics = get_analytics_data()
    elapsed = time.time() - start
    
    print(f"  Analytics query time: {elapsed:.3f}s")
    print(f"  Total claims: {analytics['total_claims']}")
    
    if elapsed < 1.0:
        print(f"  ✅ Good performance (<1s)")
    elif elapsed < 2.0:
        print(f"  ⚠️  Acceptable performance (1-2s)")
    else:
        print(f"  ❌ Slow performance (>2s) - consider optimization")
    
    # Test history query
    start = time.time()
    history = get_all_history()
    elapsed = time.time() - start
    
    print(f"  History query time: {elapsed:.3f}s")
    print(f"  Records fetched: {len(history)}")
    
    if elapsed < 0.5:
        print(f"  ✅ Good performance (<0.5s)")
    else:
        print(f"  ⚠️  Consider adding LIMIT or pagination")

def test_timeout_configuration():
    """Test that timeouts are configured"""
    print("\n=== Testing Timeout Configuration ===")
    
    if DATABASE_TYPE != "postgresql":
        print("  ⚠️  Skipping (only relevant for PostgreSQL)")
        return
    
    conn = get_connection()
    cursor = conn.cursor()
    
    # Check statement_timeout
    cursor.execute("SHOW statement_timeout")
    timeout = cursor.fetchone()[0]
    print(f"  Statement timeout: {timeout}")
    
    if timeout == '5s' or timeout == '5000ms':
        print(f"  ✅ Statement timeout configured correctly")
    else:
        print(f"  ⚠️  Statement timeout: {timeout} (expected 5s)")
    
    close_connection(conn)

def main():
    """Run all tests"""
    print("="*60)
    print("Database Performance Optimization Tests")
    print("="*60)
    print(f"\nDatabase Type: {DATABASE_TYPE}")
    
    try:
        # Initialize database (creates tables and indexes)
        print("\nInitializing database...")
        init_database()
        print("✅ Database initialized")
        
        # Run tests
        test_connection_pooling()
        test_indexes()
        test_query_performance()
        test_timeout_configuration()
        
        print("\n" + "="*60)
        print("✅ All tests completed!")
        print("="*60)
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
