from sqlalchemy import create_engine, text

DB_URL = "mysql+pymysql://root:davidsp@localhost:3306/happiness_db"

REQUIRED_FIELDS = ['country', 'region', 'year', 'gdp', 'family', 'health', 'freedom', 'generosity', 'trust', 'actual_score']
NUMERIC_FIELDS  = ['gdp', 'family', 'health', 'freedom', 'generosity', 'trust', 'actual_score']
FEATURES        = ['gdp', 'family', 'health', 'freedom', 'generosity', 'trust']


def get_engine():
    return create_engine(DB_URL)


# ── Dimensiones ───────────────────────────────────────────────────────────────

def get_or_create_country(conn, country, region=None):
    result = conn.execute(
        text("SELECT country_id FROM dim_country WHERE country = :c"),
        {"c": country}
    ).fetchone()
    if result:
        return result[0]
    res = conn.execute(
        text("INSERT INTO dim_country (country, region) VALUES (:c, :r)"),
        {"c": country, "r": region}
    )
    return res.lastrowid


def get_or_create_date(conn, year):
    result = conn.execute(
        text("SELECT date_id FROM dim_date WHERE year = :y"),
        {"y": year}
    ).fetchone()
    if result:
        return result[0]
    res = conn.execute(
        text("INSERT INTO dim_date (year) VALUES (:y)"),
        {"y": year}
    )
    return res.lastrowid


# ── Raw ───────────────────────────────────────────────────────────────────────

def insert_raw_event(conn, event, status='VALID'):
    res = conn.execute(text("""
        INSERT INTO raw_happiness_events
            (country, region, year, gdp, family, health, freedom, generosity, trust, actual_score, status)
        VALUES
            (:country, :region, :year, :gdp, :family, :health, :freedom, :generosity, :trust, :actual_score, :status)
    """), {**event, 'status': status})
    return res.lastrowid


def insert_dim_raw_event(conn, raw_event_id, status):
    conn.execute(text("""
        INSERT INTO dim_raw_event (raw_event_id, status, received_at)
        SELECT id, status, received_at
        FROM raw_happiness_events
        WHERE id = :id
    """), {"id": raw_event_id})


# ── Fact ─────────────────────────────────────────────────────────────────────

def insert_prediction(conn, raw_event_id, country_id, date_id, predicted_score, actual_score):
    conn.execute(text("""
        INSERT INTO fact_predictions
            (raw_event_id, country_id, date_id, actual_score, predicted_score, prediction_error)
        VALUES
            (:raw_event_id, :country_id, :date_id, :actual_score, :predicted_score, :prediction_error)
    """), {
        "raw_event_id":      raw_event_id,
        "country_id":        country_id,
        "date_id":           date_id,
        "actual_score":      actual_score,
        "predicted_score":   round(predicted_score, 4),
        "prediction_error":  round(abs(predicted_score - actual_score), 4),
    })