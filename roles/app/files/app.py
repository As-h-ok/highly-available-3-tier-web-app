import os
import socket

import psycopg
from flask import Flask, jsonify

app = Flask(__name__)
DB_DSN = os.environ["DB_DSN"]
VERSION = os.environ.get("APP_VERSION", "dev")
HOST = socket.gethostname()


def get_connection():
    return psycopg.connect(DB_DSN, connect_timeout=2)


@app.get("/health")
def health():
    return jsonify(status="ok", server=HOST, version=VERSION)


@app.get("/health/db")
def health_db():
    try:
        with get_connection() as conn:
            conn.execute("SELECT 1")
    except psycopg.Error:
        return jsonify(status="database unreachable", server=HOST), 503
    return jsonify(status="ok", server=HOST)


@app.get("/")
def index():
    try:
        with get_connection() as conn:
            conn.execute("INSERT INTO visits (served_by) VALUES (%s)", (HOST,))
            total = conn.execute("SELECT count(*) FROM visits").fetchone()[0]
    except psycopg.Error:
        return f"Served by {HOST}: database unavailable\n", 503
    return f"Served by {HOST} | version {VERSION} | visits {total}\n"
