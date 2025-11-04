"""
Database operations for Claims History
Supports both SQLite (local) and PostgreSQL (Supabase cloud)
"""

import sqlite3
import json
import os
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database configuration helper
_config_cache = {"type": None, "url": None}

def get_database_config():
    """Get database configuration from Streamlit secrets or environment variables"""
    # Return cached config if available
    if _config_cache["type"] is not None:
        return _config_cache["type"], _config_cache["url"]
    
    # Try Streamlit secrets first (only works after streamlit is initialized)
    try:
        import streamlit as st
        if hasattr(st, 'secrets') and 'DATABASE_TYPE' in st.secrets:
            db_type = st.secrets.get("DATABASE_TYPE", "sqlite").lower()
            db_url = st.secrets.get("DATABASE_URL", "")
            _config_cache["type"] = db_type
            _config_cache["url"] = db_url
            return db_type, db_url
    except:
        pass
    
    # Fallback to environment variables
    db_type = os.getenv("DATABASE_TYPE", "sqlite").lower()
    db_url = os.getenv("DATABASE_URL", "")
    _config_cache["type"] = db_type
    _config_cache["url"] = db_url
    return db_type, db_url

# Get initial configuration from environment variables only (no streamlit import)
DATABASE_TYPE = os.getenv("DATABASE_TYPE", "sqlite").lower()
DATABASE_URL = os.getenv("DATABASE_URL", "")

# SQLite file path (only used when DATABASE_TYPE=sqlite)
DB_FILE = Path(__file__).parent / "claims_history.db"

# Import PostgreSQL adapter only if needed
if DATABASE_TYPE == "postgresql":
    try:
        import psycopg2
        from psycopg2.extras import RealDictCursor
    except ImportError:
        raise ImportError(
            "psycopg2 is required for PostgreSQL support. "
            "Install it with: pip install psycopg2-binary"
        )


def get_connection():
    """
    Get database connection based on DATABASE_TYPE
    
    Returns:
        Database connection object
    """
    # Get current configuration (checks Streamlit secrets if available)
    db_type, db_url = get_database_config()
    
    if db_type == "postgresql":
        if not db_url:
            raise ValueError(
                "DATABASE_URL must be set when using PostgreSQL. "
                "Please set DATABASE_URL in your .env file or Streamlit Cloud secrets."
            )
        try:
            return psycopg2.connect(db_url)
        except Exception as e:
            raise ConnectionError(
                f"Failed to connect to PostgreSQL database: {str(e)}. "
                "Please check your DATABASE_URL configuration."
            )
    else:
        return sqlite3.connect(DB_FILE)


def get_cursor(conn):
    """
    Get appropriate cursor for the database type
    
    Args:
        conn: Database connection
        
    Returns:
        Cursor object with appropriate row factory
    """
    db_type, _ = get_database_config()
    if db_type == "postgresql":
        return conn.cursor(cursor_factory=RealDictCursor)
    else:
        conn.row_factory = sqlite3.Row
        return conn.cursor()


def adapt_placeholder(query: str) -> str:
    """
    Adapt query placeholders based on database type
    SQLite uses ?, PostgreSQL uses %s
    
    Args:
        query: SQL query string with ? placeholders
        
    Returns:
        Query string with appropriate placeholders
    """
    db_type, _ = get_database_config()
    if db_type == "postgresql":
        return query.replace("?", "%s")
    return query


def init_database():
    """
    Initialize the database and create tables if they don't exist
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    if DATABASE_TYPE == "postgresql":
        # PostgreSQL schema
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS claim_history (
                id SERIAL PRIMARY KEY,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                claim_text TEXT NOT NULL,
                loss_type TEXT,
                severity TEXT,
                affected_assets TEXT,
                estimated_loss TEXT,
                incident_date TEXT,
                location TEXT,
                confidence TEXT,
                extraction_explanation TEXT
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS claim_recommendations (
                id SERIAL PRIMARY KEY,
                claim_id INTEGER NOT NULL,
                action TEXT NOT NULL,
                priority TEXT NOT NULL,
                category TEXT NOT NULL,
                icon TEXT,
                reasoning TEXT,
                FOREIGN KEY (claim_id) REFERENCES claim_history(id) ON DELETE CASCADE
            )
        """)
    else:
        # SQLite schema
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS claim_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                claim_text TEXT NOT NULL,
                loss_type TEXT,
                severity TEXT,
                affected_assets TEXT,
                estimated_loss TEXT,
                incident_date TEXT,
                location TEXT,
                confidence TEXT,
                extraction_explanation TEXT
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS claim_recommendations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                claim_id INTEGER NOT NULL,
                action TEXT NOT NULL,
                priority TEXT NOT NULL,
                category TEXT NOT NULL,
                icon TEXT,
                reasoning TEXT,
                FOREIGN KEY (claim_id) REFERENCES claim_history(id) ON DELETE CASCADE
            )
        """)
    
    conn.commit()
    conn.close()


def save_claim_to_history(claim_text: str, extracted_data: Dict) -> int:
    """
    Save a processed claim to the history database
    
    Args:
        claim_text: Original claim description
        extracted_data: Extracted structured data from AI
        
    Returns:
        ID of the inserted record
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    if DATABASE_TYPE == "postgresql":
        cursor.execute("""
            INSERT INTO claim_history (
                claim_text, loss_type, severity, affected_assets,
                estimated_loss, incident_date, location, confidence,
                extraction_explanation
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        """, (
            claim_text,
            extracted_data.get("loss_type", "Unknown"),
            extracted_data.get("severity", "Unknown"),
            extracted_data.get("affected_assets", "Not specified"),
            extracted_data.get("estimated_loss", "Not specified"),
            extracted_data.get("incident_date", "Not specified"),
            extracted_data.get("location", "Not specified"),
            extracted_data.get("confidence", "Unknown"),
            extracted_data.get("extraction_explanation", "")
        ))
        record_id = cursor.fetchone()[0]
    else:
        cursor.execute("""
            INSERT INTO claim_history (
                claim_text, loss_type, severity, affected_assets,
                estimated_loss, incident_date, location, confidence,
                extraction_explanation
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            claim_text,
            extracted_data.get("loss_type", "Unknown"),
            extracted_data.get("severity", "Unknown"),
            extracted_data.get("affected_assets", "Not specified"),
            extracted_data.get("estimated_loss", "Not specified"),
            extracted_data.get("incident_date", "Not specified"),
            extracted_data.get("location", "Not specified"),
            extracted_data.get("confidence", "Unknown"),
            extracted_data.get("extraction_explanation", "")
        ))
        record_id = cursor.lastrowid
    
    conn.commit()
    conn.close()
    
    return record_id


def get_all_history(limit: int = 100) -> List[Dict]:
    """
    Retrieve all claim history records
    
    Args:
        limit: Maximum number of records to retrieve
        
    Returns:
        List of claim history dictionaries
    """
    conn = get_connection()
    cursor = get_cursor(conn)
    
    query = adapt_placeholder("""
        SELECT * FROM claim_history
        ORDER BY timestamp DESC
        LIMIT ?
    """)
    
    cursor.execute(query, (limit,))
    rows = cursor.fetchall()
    conn.close()
    
    # Convert to list of dictionaries
    history = [dict(row) for row in rows]
    
    # Convert datetime objects to strings for PostgreSQL
    if DATABASE_TYPE == "postgresql":
        for record in history:
            if 'timestamp' in record and isinstance(record['timestamp'], datetime):
                record['timestamp'] = record['timestamp'].strftime('%Y-%m-%d %H:%M:%S')
    
    return history


def get_history_by_id(record_id: int) -> Optional[Dict]:
    """
    Retrieve a specific claim history record by ID
    
    Args:
        record_id: Database record ID
        
    Returns:
        Claim history dictionary or None if not found
    """
    conn = get_connection()
    cursor = get_cursor(conn)
    
    query = adapt_placeholder("""
        SELECT * FROM claim_history
        WHERE id = ?
    """)
    
    cursor.execute(query, (record_id,))
    row = cursor.fetchone()
    conn.close()
    
    if row:
        record = dict(row)
        # Convert datetime objects to strings for PostgreSQL
        if DATABASE_TYPE == "postgresql" and 'timestamp' in record:
            if isinstance(record['timestamp'], datetime):
                record['timestamp'] = record['timestamp'].strftime('%Y-%m-%d %H:%M:%S')
        return record
    return None


def delete_history_item(record_id: int) -> bool:
    """
    Delete a specific claim history record
    
    Args:
        record_id: Database record ID
        
    Returns:
        True if deleted, False if not found
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    query = adapt_placeholder("""
        DELETE FROM claim_history
        WHERE id = ?
    """)
    
    cursor.execute(query, (record_id,))
    rows_affected = cursor.rowcount
    
    conn.commit()
    conn.close()
    
    return rows_affected > 0


def search_history(
    keyword: Optional[str] = None,
    severity: Optional[str] = None,
    limit: int = 100
) -> List[Dict]:
    """
    Search claim history with filters
    
    Args:
        keyword: Search keyword (searches in claim_text)
        severity: Filter by severity level
        limit: Maximum number of records to retrieve
        
    Returns:
        List of matching claim history dictionaries
    """
    conn = get_connection()
    cursor = get_cursor(conn)
    
    query = "SELECT * FROM claim_history WHERE 1=1"
    params = []
    
    if keyword:
        if DATABASE_TYPE == "postgresql":
            query += " AND claim_text ILIKE %s"
        else:
            query += " AND claim_text LIKE ?"
        params.append(f"%{keyword}%")
    
    if severity:
        query += " AND severity = " + ("%s" if DATABASE_TYPE == "postgresql" else "?")
        params.append(severity)
    
    query += " ORDER BY timestamp DESC LIMIT " + ("%s" if DATABASE_TYPE == "postgresql" else "?")
    params.append(limit)
    
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    
    history = [dict(row) for row in rows]
    
    # Convert datetime objects to strings for PostgreSQL
    if DATABASE_TYPE == "postgresql":
        for record in history:
            if 'timestamp' in record and isinstance(record['timestamp'], datetime):
                record['timestamp'] = record['timestamp'].strftime('%Y-%m-%d %H:%M:%S')
    
    return history


def get_history_stats() -> Dict:
    """
    Get statistics about claim history
    
    Returns:
        Dictionary with statistics (total count, severity breakdown, etc.)
    """
    conn = get_connection()
    cursor = conn.cursor()  # Use plain cursor for simple queries
    
    # Total count
    cursor.execute("SELECT COUNT(*) as count FROM claim_history")
    result = cursor.fetchone()
    if DATABASE_TYPE == "postgresql":
        total_count = result[0] if result else 0
    else:
        total_count = result[0] if result else 0
    
    # Severity breakdown
    cursor.execute("""
        SELECT severity, COUNT(*) as count
        FROM claim_history
        GROUP BY severity
    """)
    severity_breakdown = dict(cursor.fetchall())
    
    # Most recent timestamp
    cursor.execute("SELECT MAX(timestamp) as max_timestamp FROM claim_history")
    result = cursor.fetchone()
    if DATABASE_TYPE == "postgresql":
        last_claim = result[0] if result else None
    else:
        last_claim = result[0] if result else None
    
    # Convert datetime to string for PostgreSQL
    if DATABASE_TYPE == "postgresql" and last_claim:
        if isinstance(last_claim, datetime):
            last_claim = last_claim.strftime('%Y-%m-%d %H:%M:%S')
    
    conn.close()
    
    return {
        "total_claims": total_count,
        "severity_breakdown": severity_breakdown,
        "last_claim_date": last_claim
    }


def clear_all_history() -> int:
    """
    Delete all claim history records
    
    Returns:
        Number of records deleted
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("DELETE FROM claim_history")
    rows_affected = cursor.rowcount
    
    conn.commit()
    conn.close()
    
    return rows_affected


def export_history_to_json(output_file: str = "claim_history_export.json"):
    """
    Export all claim history to a JSON file
    
    Args:
        output_file: Output file path
        
    Returns:
        Number of records exported
    """
    history = get_all_history(limit=10000)  # Export all
    
    # Convert datetime objects to strings for JSON serialization
    for record in history:
        if 'timestamp' in record and record['timestamp']:
            if isinstance(record['timestamp'], datetime):
                record['timestamp'] = record['timestamp'].isoformat()
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(history, f, indent=2, ensure_ascii=False, default=str)
    
    return len(history)


def get_analytics_data() -> Dict:
    """
    Get comprehensive analytics data for dashboard visualizations
    
    Returns:
        Dictionary with analytics including:
        - Loss type distribution
        - Severity distribution
        - Confidence distribution
        - Claims over time
        - Average confidence by severity
        - Total claims and key metrics
    """
    conn = get_connection()
    cursor = get_cursor(conn)
    
    # Total claims
    cursor.execute("SELECT COUNT(*) as count FROM claim_history")
    result = cursor.fetchone()
    if DATABASE_TYPE == "postgresql":
        total_claims = result['count'] if result else 0
    else:
        total_claims = result[0] if result else 0
    
    # Loss type distribution
    cursor.execute("""
        SELECT loss_type, COUNT(*) as count
        FROM claim_history
        GROUP BY loss_type
        ORDER BY count DESC
    """)
    loss_type_dist = [dict(row) for row in cursor.fetchall()]
    
    # Severity distribution
    cursor.execute("""
        SELECT severity, COUNT(*) as count
        FROM claim_history
        GROUP BY severity
        ORDER BY 
            CASE severity
                WHEN 'Critical' THEN 1
                WHEN 'High' THEN 2
                WHEN 'Medium' THEN 3
                WHEN 'Low' THEN 4
                ELSE 5
            END
    """)
    severity_dist = [dict(row) for row in cursor.fetchall()]
    
    # Confidence distribution
    cursor.execute("""
        SELECT confidence, COUNT(*) as count
        FROM claim_history
        GROUP BY confidence
        ORDER BY 
            CASE confidence
                WHEN 'High' THEN 1
                WHEN 'Medium' THEN 2
                WHEN 'Low' THEN 3
                ELSE 4
            END
    """)
    confidence_dist = [dict(row) for row in cursor.fetchall()]
    
    # Claims over time (by date)
    cursor.execute("""
        SELECT DATE(timestamp) as date, COUNT(*) as count
        FROM claim_history
        GROUP BY DATE(timestamp)
        ORDER BY date ASC
    """)
    claims_over_time = [dict(row) for row in cursor.fetchall()]
    
    # Average estimated loss (extract numeric values where possible)
    cursor.execute("""
        SELECT estimated_loss
        FROM claim_history
        WHERE estimated_loss IS NOT NULL 
        AND estimated_loss != 'Not specified'
        AND estimated_loss != 'Unknown'
    """)
    estimated_losses = cursor.fetchall()
    
    # Most recent claims
    cursor.execute("""
        SELECT MAX(timestamp) as last_claim,
               MIN(timestamp) as first_claim
        FROM claim_history
    """)
    date_range_row = cursor.fetchone()
    date_range = dict(date_range_row) if date_range_row else {}
    
    # Severity by loss type
    cursor.execute("""
        SELECT loss_type, severity, COUNT(*) as count
        FROM claim_history
        GROUP BY loss_type, severity
    """)
    severity_by_loss_type = [dict(row) for row in cursor.fetchall()]
    
    conn.close()
    
    # Extract estimated loss values
    if DATABASE_TYPE == "postgresql":
        loss_values = [row['estimated_loss'] for row in estimated_losses]
    else:
        loss_values = [row[0] for row in estimated_losses]
    
    # Convert datetime objects to strings for compatibility
    for record in claims_over_time:
        if 'date' in record and isinstance(record['date'], datetime):
            record['date'] = record['date'].strftime('%Y-%m-%d')
    
    # Convert date_range datetime objects to strings
    if date_range:
        for key in ['last_claim', 'first_claim']:
            if key in date_range and date_range[key]:
                if isinstance(date_range[key], datetime):
                    date_range[key] = date_range[key].strftime('%Y-%m-%d %H:%M:%S')
    
    return {
        "total_claims": total_claims,
        "loss_type_distribution": loss_type_dist,
        "severity_distribution": severity_dist,
        "confidence_distribution": confidence_dist,
        "claims_over_time": claims_over_time,
        "date_range": date_range,
        "severity_by_loss_type": severity_by_loss_type,
        "estimated_losses": loss_values
    }


def save_recommendations_to_history(claim_id: int, recommendations: List[Dict]) -> int:
    """
    Save recommendations for a specific claim
    
    Args:
        claim_id: ID of the claim in claim_history table
        recommendations: List of recommendation dictionaries
        
    Returns:
        Number of recommendations saved
    """
    if not recommendations:
        return 0
    
    conn = get_connection()
    cursor = conn.cursor()
    
    rows_inserted = 0
    
    # Insert each recommendation
    for rec in recommendations:
        if DATABASE_TYPE == "postgresql":
            cursor.execute("""
                INSERT INTO claim_recommendations (
                    claim_id, action, priority, category, icon, reasoning
                ) VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                claim_id,
                rec.get("action", ""),
                rec.get("priority", "Medium"),
                rec.get("category", "Processing"),
                rec.get("icon", "📋"),
                rec.get("reasoning", "")
            ))
        else:
            cursor.execute("""
                INSERT INTO claim_recommendations (
                    claim_id, action, priority, category, icon, reasoning
                ) VALUES (?, ?, ?, ?, ?, ?)
            """, (
                claim_id,
                rec.get("action", ""),
                rec.get("priority", "Medium"),
                rec.get("category", "Processing"),
                rec.get("icon", "📋"),
                rec.get("reasoning", "")
            ))
        rows_inserted += 1
    
    conn.commit()
    conn.close()
    
    return rows_inserted


def get_recommendations_by_claim_id(claim_id: int) -> List[Dict]:
    """
    Retrieve all recommendations for a specific claim
    
    Args:
        claim_id: ID of the claim
        
    Returns:
        List of recommendation dictionaries
    """
    conn = get_connection()
    cursor = get_cursor(conn)
    
    query = adapt_placeholder("""
        SELECT action, priority, category, icon, reasoning
        FROM claim_recommendations
        WHERE claim_id = ?
        ORDER BY 
            CASE priority
                WHEN 'Critical' THEN 1
                WHEN 'High' THEN 2
                WHEN 'Medium' THEN 3
                WHEN 'Low' THEN 4
                ELSE 5
            END,
            id
    """)
    
    cursor.execute(query, (claim_id,))
    rows = cursor.fetchall()
    conn.close()
    
    recommendations = [dict(row) for row in rows]
    return recommendations


def has_recommendations(claim_id: int) -> bool:
    """
    Check if a claim has recommendations stored
    
    Args:
        claim_id: ID of the claim
        
    Returns:
        True if recommendations exist, False otherwise
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    query = adapt_placeholder("""
        SELECT COUNT(*) as count FROM claim_recommendations
        WHERE claim_id = ?
    """)
    
    cursor.execute(query, (claim_id,))
    result = cursor.fetchone()
    count = result[0] if result else 0
    conn.close()
    
    return count > 0


def delete_recommendations_by_claim_id(claim_id: int) -> int:
    """
    Delete all recommendations for a specific claim
    
    Args:
        claim_id: ID of the claim
        
    Returns:
        Number of recommendations deleted
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    query = adapt_placeholder("""
        DELETE FROM claim_recommendations
        WHERE claim_id = ?
    """)
    
    cursor.execute(query, (claim_id,))
    rows_deleted = cursor.rowcount
    
    conn.commit()
    conn.close()
    
    return rows_deleted


# Utility function to get database info
def get_database_info() -> Dict:
    """
    Get information about the current database configuration
    
    Returns:
        Dictionary with database type and connection info
    """
    info = {
        "database_type": DATABASE_TYPE,
        "database_file": str(DB_FILE) if DATABASE_TYPE == "sqlite" else None,
        "database_host": DATABASE_URL.split("@")[1].split("/")[0] if DATABASE_TYPE == "postgresql" and DATABASE_URL else None
    }
    return info
