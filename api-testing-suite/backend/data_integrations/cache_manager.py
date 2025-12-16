"""
Cache Manager
SQLite-based caching for external API responses
"""
import sqlite3
import json
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Optional, Dict
from contextlib import contextmanager
import threading


class CacheManager:
    """SQLite-based cache manager for external API data"""
    
    # Default TTLs in seconds
    DEFAULT_TTL = 86400 * 7  # 7 days
    TTL_BY_SOURCE = {
        'os_places': 86400 * 30,    # 30 days - address data rarely changes
        'ons': 86400 * 90,          # 90 days - quarterly updates
        'osm': 86400 * 7,           # 7 days - POI data can change
        'nhsbsa': 86400 * 30,       # 30 days - monthly updates
    }
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls, db_path: Optional[str] = None):
        """Singleton pattern for cache manager"""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self, db_path: Optional[str] = None):
        """Initialize cache manager with SQLite database"""
        if self._initialized:
            return
            
        if db_path is None:
            # Default path: backend/data/cache.db
            self.db_path = Path(__file__).parent.parent / "data" / "cache.db"
        else:
            self.db_path = Path(db_path)
        
        # Ensure directory exists
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize database
        self._init_db()
        self._initialized = True
    
    def _init_db(self):
        """Initialize SQLite database with cache table"""
        with self._get_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS cache (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL,
                    source TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    expires_at TEXT NOT NULL,
                    hit_count INTEGER DEFAULT 0
                )
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_cache_source ON cache(source)
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_cache_expires ON cache(expires_at)
            """)
            conn.commit()
    
    @contextmanager
    def _get_connection(self):
        """Get SQLite connection with context manager"""
        conn = sqlite3.connect(str(self.db_path), timeout=30)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()
    
    def _generate_key(self, source: str, identifier: str, **kwargs) -> str:
        """Generate unique cache key from source, identifier and optional params"""
        key_parts = [source, identifier]
        if kwargs:
            # Sort kwargs for consistent key generation
            sorted_kwargs = sorted(kwargs.items())
            key_parts.extend([f"{k}={v}" for k, v in sorted_kwargs])
        
        key_string = ":".join(str(p) for p in key_parts)
        return hashlib.md5(key_string.encode()).hexdigest()
    
    def get(self, source: str, identifier: str, **kwargs) -> Optional[Dict[str, Any]]:
        """
        Get cached value if exists and not expired
        
        Args:
            source: Data source name (e.g., 'os_places', 'ons')
            identifier: Unique identifier (e.g., postcode, UPRN)
            **kwargs: Additional parameters for key generation
            
        Returns:
            Cached data or None if not found/expired
        """
        key = self._generate_key(source, identifier, **kwargs)
        now = datetime.now().isoformat()
        
        with self._get_connection() as conn:
            cursor = conn.execute(
                """
                SELECT value, expires_at FROM cache 
                WHERE key = ? AND expires_at > ?
                """,
                (key, now)
            )
            row = cursor.fetchone()
            
            if row:
                # Update hit count
                conn.execute(
                    "UPDATE cache SET hit_count = hit_count + 1 WHERE key = ?",
                    (key,)
                )
                conn.commit()
                return json.loads(row['value'])
        
        return None
    
    def set(
        self, 
        source: str, 
        identifier: str, 
        value: Dict[str, Any],
        ttl_seconds: Optional[int] = None,
        **kwargs
    ) -> bool:
        """
        Cache a value with optional TTL
        
        Args:
            source: Data source name
            identifier: Unique identifier
            value: Data to cache (must be JSON serializable)
            ttl_seconds: Optional custom TTL, otherwise uses source default
            **kwargs: Additional parameters for key generation
            
        Returns:
            True if cached successfully
        """
        key = self._generate_key(source, identifier, **kwargs)
        
        if ttl_seconds is None:
            ttl_seconds = self.TTL_BY_SOURCE.get(source, self.DEFAULT_TTL)
        
        now = datetime.now()
        expires_at = now + timedelta(seconds=ttl_seconds)
        
        try:
            with self._get_connection() as conn:
                conn.execute(
                    """
                    INSERT OR REPLACE INTO cache (key, value, source, created_at, expires_at, hit_count)
                    VALUES (?, ?, ?, ?, ?, 0)
                    """,
                    (key, json.dumps(value), source, now.isoformat(), expires_at.isoformat())
                )
                conn.commit()
            return True
        except Exception as e:
            print(f"Cache set error: {e}")
            return False
    
    def delete(self, source: str, identifier: str, **kwargs) -> bool:
        """Delete a specific cache entry"""
        key = self._generate_key(source, identifier, **kwargs)
        
        with self._get_connection() as conn:
            cursor = conn.execute("DELETE FROM cache WHERE key = ?", (key,))
            conn.commit()
            return cursor.rowcount > 0
    
    def clear_source(self, source: str) -> int:
        """Clear all cache entries for a specific source"""
        with self._get_connection() as conn:
            cursor = conn.execute("DELETE FROM cache WHERE source = ?", (source,))
            conn.commit()
            return cursor.rowcount
    
    def clear_expired(self) -> int:
        """Remove all expired cache entries"""
        now = datetime.now().isoformat()
        
        with self._get_connection() as conn:
            cursor = conn.execute("DELETE FROM cache WHERE expires_at < ?", (now,))
            conn.commit()
            return cursor.rowcount
    
    def clear_all(self) -> int:
        """Clear entire cache"""
        with self._get_connection() as conn:
            cursor = conn.execute("DELETE FROM cache")
            conn.commit()
            return cursor.rowcount
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        now = datetime.now().isoformat()
        
        with self._get_connection() as conn:
            # Total entries
            total = conn.execute("SELECT COUNT(*) as count FROM cache").fetchone()['count']
            
            # Expired entries
            expired = conn.execute(
                "SELECT COUNT(*) as count FROM cache WHERE expires_at < ?",
                (now,)
            ).fetchone()['count']
            
            # By source
            by_source = {}
            cursor = conn.execute(
                """
                SELECT source, COUNT(*) as count, SUM(hit_count) as hits
                FROM cache GROUP BY source
                """
            )
            for row in cursor:
                by_source[row['source']] = {
                    'count': row['count'],
                    'total_hits': row['hits'] or 0
                }
            
            # Database size
            db_size = self.db_path.stat().st_size if self.db_path.exists() else 0
        
        return {
            'total_entries': total,
            'expired_entries': expired,
            'valid_entries': total - expired,
            'by_source': by_source,
            'db_size_bytes': db_size,
            'db_size_mb': round(db_size / (1024 * 1024), 2),
            'db_path': str(self.db_path)
        }


# Singleton instance
_cache_instance: Optional[CacheManager] = None


def get_cache_manager(db_path: Optional[str] = None) -> CacheManager:
    """Get or create cache manager singleton"""
    global _cache_instance
    if _cache_instance is None:
        _cache_instance = CacheManager(db_path)
    return _cache_instance
