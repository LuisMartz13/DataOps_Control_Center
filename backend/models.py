from sqlalchemy import Column, Integer, String, DateTime, Float
from database import Base
from datetime import datetime


# =========================
# CONNECTIONS
# =========================

class Connection(Base):

    __tablename__ = "connections"

    id = Column(Integer, primary_key=True, index=True)

    nombre = Column(String)

    motor = Column(String)

    host = Column(String)

    port = Column(Integer)

    database_name = Column(String)

    user_name = Column(String)

    status = Column(String)

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )


# =========================
# METRICS
# =========================

class DBMetric(Base):

    __tablename__ = "db_metrics"

    id = Column(Integer, primary_key=True, index=True)

    db_id = Column(Integer)

    cpu = Column(Float)

    memory = Column(Float)

    connections = Column(Integer)

    locks = Column(Integer)

    deadlocks = Column(Integer)

    disk_usage = Column(Float)

    capture_time = Column(
        DateTime,
        default=datetime.utcnow
    )


# =========================
# QUERY ANALYZER
# =========================

class QueryLog(Base):

    __tablename__ = "query_log"

    id = Column(Integer, primary_key=True, index=True)

    query_text = Column(String)

    duration_ms = Column(Integer)

    rows_returned = Column(Integer)

    index_used = Column(String)

    execution_plan = Column(String)

    category = Column(String)

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )


# =========================
# ALERT ENGINE
# =========================

class Alert(Base):

    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)

    title = Column(String)

    severity = Column(String)

    message = Column(String)

    source = Column(String)

    trigger_condition = Column(String)

    affected_engine = Column(String)

    resolution_status = Column(String)

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )


# =========================
# AI ADVISOR
# =========================

class AIRecommendation(Base):

    __tablename__ = "ai_recommendations"

    id = Column(Integer, primary_key=True, index=True)

    title = Column(String)

    recommendation = Column(String)

    severity = Column(String)

    category = Column(String)

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )


# =========================
# USERS
# =========================

class User(Base):

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    username = Column(String, unique=True)

    password = Column(String)

    role = Column(String)

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )


# =========================
# CONCURRENCY MODULE
# =========================

class TXLog(Base):

    __tablename__ = "tx_log"

    id = Column(Integer, primary_key=True, index=True)

    session = Column(String)

    operation = Column(String)

    start_time = Column(DateTime)

    end_time = Column(DateTime)

    wait_time = Column(Integer)

    lock_type = Column(String)

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )


# =========================
# BACKUP & RECOVERY MODULE
# =========================

class BackupLog(Base):

    __tablename__ = "backup_logs"

    id = Column(Integer, primary_key=True, index=True)

    backup_type = Column(String)

    backup_size = Column(Float)

    duration_seconds = Column(Integer)

    status = Column(String)

    storage_location = Column(String)

    cloud_provider = Column(String)

    remote_url = Column(String)

    backup_hash = Column(String)

    restore_point = Column(String)

    retention_days = Column(Integer)

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )


# =========================
# REPLICATION MODULE
# =========================

class ReplicationLog(Base):

    __tablename__ = "replication_logs"

    id = Column(Integer, primary_key=True, index=True)

    primary_node = Column(String)

    replica_node = Column(String)

    replication_lag = Column(Float)

    status = Column(String)

    cap_theorem = Column(String)

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )


# =========================
# REDIS CACHE MODULE
# =========================

class CacheLog(Base):

    __tablename__ = "cache_logs"

    id = Column(Integer, primary_key=True, index=True)

    cache_key = Column(String)

    cache_status = Column(String)

    ttl = Column(Integer)

    hit_ratio = Column(Float)

    cache_size = Column(Float)

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )