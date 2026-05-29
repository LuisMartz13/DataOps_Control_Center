from redis_config import redis_client
import random
import threading
import time

from datetime import datetime, timedelta

from jose import jwt

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import engine, SessionLocal

import os
import json


from models import (
    Base,
    Connection,
    DBMetric,
    QueryLog,
    Alert,
    AIRecommendation,
    User,
    TXLog,
    BackupLog,
    ReplicationLog,
    CacheLog
)

from schemas import (
    ConnectionCreate,
    UserLogin
)

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="DataOps Control Hub",
    description="Plataforma inteligente para monitoreo, optimización y administración de bases de datos",
    version="2.0.0"
)

SECRET_KEY = "dataops_secret_key"

ALGORITHM = "HS256"

ACCESS_TOKEN_EXPIRE_MINUTES = 60

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get(
"/",
      tags=["Sistema"]
)
def home():

    return {
        "message": "DataOps Control Center funcionando"
    }


# =========================
# AUTH SYSTEM
# =========================

@app.post(
"/register",
    tags=["Autenticación"]
)
def register_user(user: UserLogin):

    db = SessionLocal()

    existing_user = db.query(User).filter(
        User.username == user.username
    ).first()

    if existing_user:

        db.close()

        return {
            "error": "Usuario ya existe"
        }

    new_user = User(
        username=user.username,
        password=user.password,
        role="admin"
    )

    db.add(new_user)

    db.commit()

    db.close()

    return {
        "message": "Usuario registrado"
    }


@app.post(
"/login",
     tags=["Autenticación"]
)
def login(user: UserLogin):

    db = SessionLocal()

    existing_user = db.query(User).filter(
        User.username == user.username,
        User.password == user.password
    ).first()

    if not existing_user:

        db.close()

        return {
            "error": "Credenciales inválidas"
        }

    expire = datetime.utcnow() + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )

    payload = {
        "sub": existing_user.username,
        "exp": expire
    }

    access_token = jwt.encode(
        payload,
        SECRET_KEY,
        algorithm=ALGORITHM
    )

    db.close()

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "username": existing_user.username,
        "role": existing_user.role
    }


# =========================
# CONNECTIONS
# =========================

@app.post(
"/connections",
     tags=["Conexiones"]
)
def create_connection(connection: ConnectionCreate):

    db = SessionLocal()

    new_connection = Connection(
        nombre=connection.nombre,
        motor=connection.motor,
        host=connection.host,
        port=connection.port,
        database_name=connection.database_name,
        user_name=connection.user_name,
        status=connection.status
    )

    db.add(new_connection)

    db.commit()

    db.refresh(new_connection)

    db.close()

    return {
        "message": "Conexión creada correctamente",
        "id": new_connection.id
    }


@app.get(
    "/connections",
tags=["Conexiones"]
)
def get_connections():

    db = SessionLocal()

    connections = db.query(Connection).all()

    db.close()

    return connections

@app.delete(
    "/connections/{connection_id}",
tags=["Conexiones"]
)
def delete_connection(connection_id: int):

    db = SessionLocal()

    connection = db.query(Connection).filter(
        Connection.id == connection_id
    ).first()

    if not connection:

        db.close()

        return {
            "error": "Conexión no encontrada"
        }

    db.delete(connection)

    db.commit()

    db.close()

    return {
        "message": "Conexión eliminada"
    }


# =========================
# METRICS
# =========================

@app.post(
    "/generate_metrics",
    tags=["Métricas"]
)
def generate_metrics():

    db = SessionLocal()

    connections = db.query(Connection).all()

    for connection in connections:

        metric = DBMetric(
            db_id=connection.id,
            cpu=random.uniform(10, 95),
            memory=random.uniform(20, 98),
            connections=random.randint(1, 300),
            locks=random.randint(0, 30),
            deadlocks=random.randint(0, 10),
            disk_usage=random.uniform(20, 95)
        )

        db.add(metric)

    db.commit()

    db.close()

    return {
        "message": "Métricas generadas"
    }


@app.get(
    "/metrics",
    tags=["Métricas"]
)
def get_metrics():

    db = SessionLocal()

    metrics = db.query(DBMetric).all()

    db.close()

    return metrics


# =========================
# QUERY ANALYZER
# =========================

@app.post(
    "/generate_queries",
    tags=["Consultas SQL"]
)
def generate_queries():

    db = SessionLocal()

    fake_queries = [

        "SELECT * FROM users",

        "SELECT * FROM orders",

        "UPDATE products SET price = 100",

        "DELETE FROM sessions",

        "SELECT * FROM transactions"

    ]

    for query in fake_queries:

        duration = random.randint(50, 3000)

        if duration < 100:

            category = "FAST"

        elif duration < 500:

            category = "MEDIUM"

        elif duration < 2000:

            category = "SLOW"

        else:

            category = "CRITICAL"

        new_query = QueryLog(
            query_text=query,
            duration_ms=duration,
            rows_returned=random.randint(1, 500),
            index_used="idx_primary",
            execution_plan="Seq Scan",
            category=category
        )

        db.add(new_query)

    db.commit()

    db.close()

    return {
        "message": "Queries generadas"
    }


@app.get(
    "/queries",
    tags=["Consultas SQL"]
)
def get_queries():

    db = SessionLocal()

    queries = db.query(QueryLog).all()

    db.close()

    return queries


# =========================
# CONCURRENCY MODULE
# =========================

@app.post(
    "/generate_transactions",
    tags=["Concurrencia"]
)
def generate_transactions():

    db = SessionLocal()

    operations = [
        "INSERT",
        "UPDATE",
        "DELETE",
        "SELECT"
    ]

    lock_types = [
        "SHARED",
        "EXCLUSIVE",
        "DEADLOCK",
        "TIMEOUT"
    ]

    deadlocks = 0

    timeouts = 0

    for i in range(100):

        start = datetime.utcnow()

        wait = random.randint(10, 5000)

        end = start + timedelta(
            milliseconds=wait
        )

        lock = random.choice(
            lock_types
        )

        if lock == "DEADLOCK":

            deadlocks += 1

        if lock == "TIMEOUT":

            timeouts += 1

        tx = TXLog(

            session=f"SESSION_{i}",

            operation=random.choice(
                operations
            ),

            start_time=start,

            end_time=end,

            wait_time=wait,

            lock_type=lock
        )

        db.add(tx)

    if deadlocks > 10:

        alert = Alert(
            title="DEADLOCK DETECTADO",
            severity="CRITICAL",
            message=f"Se detectaron {deadlocks} deadlocks",
            source="CONCURRENCY MODULE",
            trigger_condition="deadlocks > 10",
            affected_engine="PostgreSQL",
            resolution_status="OPEN"
        )

        db.add(alert)

    if timeouts > 15:

        alert = Alert(
            title="TIMEOUT DETECTADO",
            severity="HIGH",
            message=f"Se detectaron {timeouts} timeouts",
            source="CONCURRENCY MODULE",
            trigger_condition="timeouts > 15",
            affected_engine="PostgreSQL",
            resolution_status="OPEN"
        )

        db.add(alert)

    db.commit()

    db.close()

    return {
        "message": "100 transacciones generadas",
        "deadlocks": deadlocks,
        "timeouts": timeouts
    }


@app.get(
    "/transactions",
    tags=["Concurrencia"]
)
def get_transactions():

    db = SessionLocal()

    transactions = db.query(
        TXLog
    ).all()

    db.close()

    return transactions


# =========================
# BACKUP & RECOVERY MODULE
# =========================

@app.post(
    "/generate_backups",
    tags=["Backups"]
)
def generate_backups():

    db = SessionLocal()

    backup_types = [
        "FULL",
        "DIFFERENTIAL",
        "INCREMENTAL"
    ]

    cloud_providers = [
        "AWS S3",
        "AZURE BLOB"
    ]

    snapshot_types = [
        "PRE_DEPLOY",
        "PRE_TEST",
        "PRE_IMPORT"
    ]

    statuses = [
        "SUCCESS",
        "FAILED"
    ]

    success_count = 0

    failed_count = 0

    for i in range(20):

        status = random.choice(
            statuses
        )

        if status == "SUCCESS":

            success_count += 1

        else:

            failed_count += 1

        provider = random.choice(
            cloud_providers
        )

        backup = BackupLog(

            backup_type=random.choice(
                backup_types
            ),

            backup_size=round(
                random.uniform(1, 500),
                2
            ),

            duration_seconds=random.randint(
                10,
                500
            ),

            status=status,

            storage_location=f"/backups/backup_{i}.bak",

            cloud_provider=provider,

            remote_url=f"https://cloud-storage/{provider}/backup_{i}.bak",

            backup_hash=f"HASH_{random.randint(10000,99999)}",

            restore_point=random.choice(
                snapshot_types
            ),

            retention_days=random.randint(
                7,
                90
            )
        )

        db.add(backup)

    if failed_count > 5:

        alert = Alert(

            title="BACKUP FALLIDO",

            severity="CRITICAL",

            message=f"Se detectaron {failed_count} backups fallidos",

            source="BACKUP MODULE",

            trigger_condition="failed_backups > 5",

            affected_engine="PostgreSQL",

            resolution_status="OPEN"
        )

        db.add(alert)

    db.commit()

    db.close()

    return {

        "message": "Backups generados",

        "successful_backups": success_count,

        "failed_backups": failed_count,

        "sla_compliance":
            "YES"
            if failed_count < 5
            else "NO",

        "rpo": "15 minutos",

        "rto": "45 segundos",

        "snapshots": snapshot_types
    }


@app.post(
    "/restore_backup",
    tags=["Backups"]
)
def restore_backup():

    recovery_time = round(
        random.uniform(5, 120),
        2
    )

    disaster_type = random.choice([
        "DROP TABLE",
        "CORRUPCIÓN",
        "FALLO DE DISCO"
    ])

    return {

        "message":
            "Backup restaurado correctamente",

        "recovery_time_seconds":
            recovery_time,

        "rpo":
            "15 minutos",

        "rto":
            f"{recovery_time} segundos",

        "restore_status":
            "SUCCESS",

        "disaster_simulated":
            disaster_type
    }

@app.post(
    "/upload_cloud_backup",
    tags=["Backups"]
)
def upload_cloud_backup():

    file_name = f"backup_{datetime.now().timestamp()}.json"

    backup_data = {
        "status": "BACKUP_OK",
        "date": str(datetime.now())
    }

    CLOUD_PATH = "./cloud_storage"

    os.makedirs(CLOUD_PATH, exist_ok=True)

    with open(f"{CLOUD_PATH}/{file_name}", "w") as file:
        json.dump(backup_data, file)

    return {
        "message": "Backup subido a la nube",
        "file": file_name
    }


@app.get(
    "/cloud_backups",
    tags=["Backups"]
)
def cloud_backups():

    os.makedirs("cloud_storage", exist_ok=True)

    files = os.listdir("cloud_storage")

    return files


@app.get(
    "/backups",
    tags=["Backups"]
)
def get_backups():

    db = SessionLocal()

    backups = db.query(
        BackupLog
    ).all()

    db.close()

    return backups

# =========================
# REPLICATION MODULE
# =========================

@app.post(
    "/generate_replication",
    tags=["Replicación"]
)
def generate_replication():

    db = SessionLocal()

    statuses = [
        "ACCEPTABLE",
        "WARNING",
        "CRITICAL"
    ]

    lag_levels = [
        2,
        5,
        20
    ]

    cap_modes = [
        "CP",
        "AP",
        "CA"
    ]

    critical_replications = 0

    for i in range(15):

        lag = random.choice(
            lag_levels
        )

        if lag <= 2:

            status = "ACCEPTABLE"

        elif lag <= 5:

            status = "WARNING"

        else:

            status = "CRITICAL"

            critical_replications += 1

        replication = ReplicationLog(

            primary_node=f"PRIMARY_{i}",

            replica_node=f"REPLICA_{i}",

            replication_lag=lag,

            status=status,

            cap_theorem=random.choice(
                cap_modes
            )
        )

        db.add(replication)

    if critical_replications > 3:

        alert = Alert(

            title="REPLICATION LAG CRÍTICO",

            severity="HIGH",

            message=f"{critical_replications} nodos con lag crítico",

            source="REPLICATION MODULE",

            trigger_condition="replication_lag > 5",

            affected_engine="PostgreSQL Cluster",

            resolution_status="OPEN"
        )

        db.add(alert)

    db.commit()

    db.close()

    return {

        "message":
            "Replicación generada",

        "critical_replications":
            critical_replications
    }

@app.get(
    "/replication",
    tags=["Replicación"]
)
def get_replication():

    db = SessionLocal()

    replication = db.query(
        ReplicationLog
    ).all()

    db.close()

    return replication


# =========================
# REDIS CACHE MODULE
# =========================

@app.post(
    "/generate_cache",
     tags=["Cache Redis"]
)
def generate_cache():

    db = SessionLocal()

    statuses = [
        "HIT",
        "MISS"
    ]

    hits = 0

    misses = 0

    for i in range(30):

        status = random.choice(
            statuses
        )

        if status == "HIT":

            hits += 1

        else:

            misses += 1

        cache = CacheLog(

            cache_key=f"KEY_{i}",

            cache_status=status,

            ttl=random.randint(
                30,
                3600
            ),

            hit_ratio=round(
                random.uniform(70, 99),
                2
            ),

            cache_size=round(
                random.uniform(1, 50),
                2
            )
        )

        db.add(cache)

        redis_client.set(
            f"KEY_{i}",
            f"VALUE_{i}",
            ex=3600
        )

    if misses > 10:

        alert = Alert(

            title="CACHE MISS ELEVADO",

            severity="MEDIUM",

            message=f"Se detectaron {misses} cache misses",

            source="REDIS CACHE",

            trigger_condition="cache_miss > 10",

            affected_engine="Redis",

            resolution_status="OPEN"
        )

        db.add(alert)

    db.commit()

    db.close()

    return {

        "message":
            "Cache generada",

        "hits":
            hits,

        "misses":
            misses
    }


@app.get(
    "/cache",
    tags=["Cache Redis"]
)
def get_cache():

    db = SessionLocal()

    cache = db.query(
        CacheLog
    ).all()

    db.close()

    return cache


@app.delete(
    "/clear_cache",
    tags=["Cache Redis"]
)
def clear_cache():

    redis_client.flushall()

    return {
        "message":
            "Cache limpiada"
    }


# =========================
# ALERT ENGINE
# =========================

@app.get(
    "/alerts",
    tags=["Alertas"]
)
def get_alerts():

    db = SessionLocal()

    alerts = db.query(
        Alert
    ).all()

    db.close()

    return alerts


@app.post(
    "/generate_alerts",
    tags=["Alertas"]
)
def generate_alerts():

    db = SessionLocal()

    alerts = [

        Alert(
            message="CPU superior al 90%",
            severity="CRITICAL"
        ),

        Alert(
            message="Deadlock detectado",
            severity="WARNING"
        ),

        Alert(
            message="Backup fallido en servidor secundario",
            severity="HIGH"
        )
    ]

    for alert in alerts:
        db.add(alert)

    db.commit()

    db.close()

    return {
        "message": "Alertas generadas"
    }


# =========================
# AI ADVISOR
# =========================


# =========================
# AI ADVISOR
# =========================

@app.post(
    "/generate_ai_recommendations",
    tags=["IA"]
)
def generate_ai_recommendations():

    db = SessionLocal()

    recommendations = [

        {
            "title": "Optimizar índices",
            "recommendation":
                "Agregar índices en tablas críticas",
            "severity": "HIGH",
            "category": "QUERY"
        },

        {
            "title": "Reducir deadlocks",
            "recommendation":
                "Aplicar aislamiento READ COMMITTED",
            "severity": "MEDIUM",
            "category": "CONCURRENCY"
        },

        {
            "title": "Optimizar backups",
            "recommendation":
                "Mover backups a almacenamiento frío",
            "severity": "LOW",
            "category": "BACKUP"
        }
    ]

    for rec in recommendations:

        recommendation = AIRecommendation(

            title=rec["title"],

            recommendation=rec["recommendation"],

            severity=rec["severity"],

            category=rec["category"]
        )

        db.add(recommendation)

    db.commit()

    db.close()

    return {
        "message":
            "Recomendaciones generadas"
    }


@app.get(
    "/ai_recommendations",
    tags=["IA"]
)
def get_ai_recommendations():

    db = SessionLocal()

    recommendations = db.query(
        AIRecommendation
    ).all()

    db.close()

    return recommendations


# =========================
# HEALTH MONITORING
# =========================

@app.get(
    "/health",
    tags=["Monitoreo"]
)
def health_check():

    return {

        "status":
            "HEALTHY",

        "database":
            "CONNECTED",

        "redis":
            "CONNECTED",

        "api":
            "ONLINE",

        "timestamp":
            datetime.utcnow()
    }


# =========================
# TOP QUERIES
# =========================

@app.get(
    "/top_queries",
    tags=["Consultas SQL"]
)
def top_queries():

    db = SessionLocal()

    queries = db.query(
        QueryLog
    ).order_by(
        QueryLog.duration_ms.desc()
    ).limit(10).all()

    db.close()

    return queries