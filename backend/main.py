from redis_config import redis_client
import random
import threading
import time

from datetime import datetime, timedelta

from jose import jwt

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import engine, SessionLocal

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

app = FastAPI()

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


@app.get("/")
def home():

    return {
        "message": "DataOps Control Center funcionando"
    }


# =========================
# AUTH SYSTEM
# =========================

@app.post("/register")
def register_user(user: UserLogin):

    db = SessionLocal()

    existing_user = db.query(User).filter(
        User.username == user.username
    ).first()

    if existing_user:

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

    return {
        "message": "Usuario registrado"
    }


@app.post("/login")
def login(user: UserLogin):

    db = SessionLocal()

    existing_user = db.query(User).filter(
        User.username == user.username,
        User.password == user.password
    ).first()

    if not existing_user:

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

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "username": existing_user.username,
        "role": existing_user.role
    }


# =========================
# CONNECTIONS
# =========================

@app.post("/connections")
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

    return {
        "message": "Conexión creada correctamente",
        "id": new_connection.id
    }


@app.get("/connections")
def get_connections():

    db = SessionLocal()

    connections = db.query(Connection).all()

    return connections


@app.delete("/connections/{connection_id}")
def delete_connection(connection_id: int):

    db = SessionLocal()

    connection = db.query(Connection).filter(
        Connection.id == connection_id
    ).first()

    if not connection:

        return {
            "error": "Conexión no encontrada"
        }

    db.delete(connection)

    db.commit()

    return {
        "message": "Conexión eliminada"
    }


# =========================
# METRICS
# =========================

@app.post("/generate_metrics")
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

    return {
        "message": "Métricas generadas"
    }


@app.get("/metrics")
def get_metrics():

    db = SessionLocal()

    metrics = db.query(DBMetric).all()

    return metrics


# =========================
# QUERY ANALYZER
# =========================

@app.post("/generate_queries")
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

    return {
        "message": "Queries generadas"
    }


@app.get("/queries")
def get_queries():

    db = SessionLocal()

    queries = db.query(QueryLog).all()

    return queries


# =========================
# CONCURRENCY MODULE
# =========================

@app.post("/generate_transactions")
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

    return {
        "message": "100 transacciones generadas",
        "deadlocks": deadlocks,
        "timeouts": timeouts
    }


@app.get("/transactions")
def get_transactions():

    db = SessionLocal()

    transactions = db.query(
        TXLog
    ).all()

    return transactions


# =========================
# BACKUP & RECOVERY MODULE
# =========================

@app.post("/generate_backups")
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


@app.post("/restore_backup")
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


@app.get("/backups")
def get_backups():

    db = SessionLocal()

    backups = db.query(
        BackupLog
    ).all()

    return backups