"""
AtmoSync Control Deck
A lightweight, dependency-free (no Docker/Kafka/Superset) local dashboard
that reads directly from atmosync.db and serves a live cold-chain view.

Run:
    pip install flask
    python app.py
Then open http://localhost:5000
"""

from flask import Flask, jsonify, render_template
import sqlite3
import os

app = Flask(__name__)

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "atmosync.db")


def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def table_exists(conn, name):
    row = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name=?", (name,)
    ).fetchone()
    return row is not None


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/containers")
def containers():
    """Latest sensor reading + latest decay info per container."""
    conn = get_conn()
    try:
        rows = conn.execute(
            """
            SELECT s.*
            FROM sensor_data s
            INNER JOIN (
                SELECT container_id, MAX(id) AS max_id
                FROM sensor_data
                GROUP BY container_id
            ) latest ON s.container_id = latest.container_id AND s.id = latest.max_id
            ORDER BY s.container_id
            """
        ).fetchall()
        containers_out = [dict(r) for r in rows]

        # Attach decay info if the dbt model has been built
        if table_exists(conn, "spoilage_degradation"):
            decay_rows = conn.execute(
                """
                SELECT d.*
                FROM spoilage_degradation d
                INNER JOIN (
                    SELECT container_id, MAX(reading_seq) AS max_seq
                    FROM spoilage_degradation
                    GROUP BY container_id
                ) latest ON d.container_id = latest.container_id AND d.reading_seq = latest.max_seq
                """
            ).fetchall()
            decay_by_container = {r["container_id"]: dict(r) for r in decay_rows}
            for c in containers_out:
                decay = decay_by_container.get(c["container_id"])
                if decay:
                    c["quality_remaining_pct"] = decay["quality_remaining_pct"]
                    c["quality_tier"] = decay["quality_tier"]
                    c["cumulative_decay_pct"] = decay["cumulative_decay_pct"]

        return jsonify({"ok": True, "containers": containers_out})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e), "containers": []})
    finally:
        conn.close()


@app.route("/api/history/<container_id>")
def history(container_id):
    """Quality-remaining curve over time for one container, for the chart."""
    conn = get_conn()
    try:
        if not table_exists(conn, "spoilage_degradation"):
            return jsonify({"ok": True, "points": []})
        rows = conn.execute(
            """
            SELECT reading_seq, quality_remaining_pct, temperature_c, event_timestamp
            FROM spoilage_degradation
            WHERE container_id = ?
            ORDER BY reading_seq ASC
            """,
            (container_id,),
        ).fetchall()
        return jsonify({"ok": True, "points": [dict(r) for r in rows]})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e), "points": []})
    finally:
        conn.close()


@app.route("/api/arbitrage")
def arbitrage():
    """Reroute recommendations from spoilage_arbitrage, best opportunities first."""
    conn = get_conn()
    try:
        if not table_exists(conn, "spoilage_arbitrage"):
            return jsonify({"ok": True, "rows": []})
        rows = conn.execute(
            """
            SELECT *
            FROM spoilage_arbitrage
            ORDER BY reroute_recommended DESC, net_arbitrage_value_per_kg DESC
            """
        ).fetchall()
        return jsonify({"ok": True, "rows": [dict(r) for r in rows]})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e), "rows": []})
    finally:
        conn.close()


if __name__ == "__main__":
    app.run(debug=True, port=5000)
