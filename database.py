"""
Database operations for Claims History using SQLite
"""

import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from pathlib import Path


# Database file path
DB_FILE = Path(__file__).parent / "claims_history.db"


def init_database():
    """
    Initialize the SQLite database and create tables if they don't exist
    """
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
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
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
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
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row  # Enable column access by name
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT * FROM claim_history
        ORDER BY timestamp DESC
        LIMIT ?
    """, (limit,))
    
    rows = cursor.fetchall()
    conn.close()
    
    # Convert to list of dictionaries
    history = [dict(row) for row in rows]
    return history


def get_history_by_id(record_id: int) -> Optional[Dict]:
    """
    Retrieve a specific claim history record by ID
    
    Args:
        record_id: Database record ID
        
    Returns:
        Claim history dictionary or None if not found
    """
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT * FROM claim_history
        WHERE id = ?
    """, (record_id,))
    
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return dict(row)
    return None


def delete_history_item(record_id: int) -> bool:
    """
    Delete a specific claim history record
    
    Args:
        record_id: Database record ID
        
    Returns:
        True if deleted, False if not found
    """
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    cursor.execute("""
        DELETE FROM claim_history
        WHERE id = ?
    """, (record_id,))
    
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
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    query = "SELECT * FROM claim_history WHERE 1=1"
    params = []
    
    if keyword:
        query += " AND claim_text LIKE ?"
        params.append(f"%{keyword}%")
    
    if severity:
        query += " AND severity = ?"
        params.append(severity)
    
    query += " ORDER BY timestamp DESC LIMIT ?"
    params.append(limit)
    
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    
    history = [dict(row) for row in rows]
    return history


def get_history_stats() -> Dict:
    """
    Get statistics about claim history
    
    Returns:
        Dictionary with statistics (total count, severity breakdown, etc.)
    """
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Total count
    cursor.execute("SELECT COUNT(*) FROM claim_history")
    total_count = cursor.fetchone()[0]
    
    # Severity breakdown
    cursor.execute("""
        SELECT severity, COUNT(*) as count
        FROM claim_history
        GROUP BY severity
    """)
    severity_breakdown = dict(cursor.fetchall())
    
    # Most recent timestamp
    cursor.execute("SELECT MAX(timestamp) FROM claim_history")
    last_claim = cursor.fetchone()[0]
    
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
    conn = sqlite3.connect(DB_FILE)
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
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(history, f, indent=2, ensure_ascii=False)
    
    return len(history)
