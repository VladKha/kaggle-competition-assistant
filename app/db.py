import os
import psycopg2
from psycopg2.extras import DictCursor
from datetime import datetime
from zoneinfo import ZoneInfo

RUN_TIMEZONE_CHECK = os.getenv('RUN_TIMEZONE_CHECK', '1') == '1'

TZ_INFO = os.getenv("TZ", "Europe/Berlin")
tz = ZoneInfo(TZ_INFO)


def get_db_connection():
    return psycopg2.connect(
        host=os.getenv("POSTGRES_HOST", "postgres"),
        port=os.getenv("POSTGRES_PORT", "5432"),
        database=os.getenv("POSTGRES_DB", "kaggle_assistant"),
        user=os.getenv("POSTGRES_USER", "your_username"),
        password=os.getenv("POSTGRES_PASSWORD", "your_password")
    )


def init_db():
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("DROP TABLE IF EXISTS feedback")
            cur.execute("DROP TABLE IF EXISTS conversations")

            cur.execute("""
                CREATE TABLE conversations (
                    id TEXT PRIMARY KEY,
                    question TEXT NOT NULL,
                    answer TEXT NOT NULL,
                    competition_slug TEXT NOT NULL,
                    assistant_model TEXT NOT NULL,
                    response_time FLOAT NOT NULL,
                    relevance TEXT NOT NULL,
                    relevance_explanation TEXT NOT NULL,
                    prompt_tokens INTEGER NOT NULL,
                    completion_tokens INTEGER NOT NULL,
                    total_tokens INTEGER NOT NULL,
                    relevance_prompt_tokens INTEGER NOT NULL,
                    relevance_completion_tokens INTEGER NOT NULL,
                    relevance_total_tokens INTEGER NOT NULL,
                    llm_cost FLOAT NOT NULL,
                    timestamp TIMESTAMP WITH TIME ZONE NOT NULL
                )
            """)
            cur.execute("""
                CREATE TABLE feedback (
                    id SERIAL PRIMARY KEY,
                    conversation_id TEXT REFERENCES conversations(id),
                    feedback INTEGER NOT NULL,
                    timestamp TIMESTAMP WITH TIME ZONE NOT NULL
                )
            """)
        conn.commit()
    finally:
        conn.close()


def save_conversation(conversation_id, question, answer_data, competition_slug, timestamp=None):
    if timestamp is None:
        timestamp = datetime.now(tz)

    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO conversations 
                (id, question, answer, competition_slug, assistant_model, response_time, relevance, 
                relevance_explanation, prompt_tokens, completion_tokens, total_tokens, 
                relevance_prompt_tokens, relevance_completion_tokens, relevance_total_tokens, llm_cost, timestamp)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, COALESCE(%s, CURRENT_TIMESTAMP))
            """,
                (
                    conversation_id,
                    question,
                    answer_data["answer"],
                    competition_slug,
                    answer_data["assistant_model"],
                    answer_data["response_time"],
                    answer_data["relevance"],
                    answer_data["relevance_explanation"],
                    answer_data["prompt_tokens"],
                    answer_data["completion_tokens"],
                    answer_data["total_tokens"],
                    answer_data["relevance_prompt_tokens"],
                    answer_data["relevance_completion_tokens"],
                    answer_data["relevance_total_tokens"],
                    answer_data["llm_cost"],
                    timestamp,
                ),
            )
        conn.commit()
    finally:
        conn.close()


def save_feedback(conversation_id, feedback, timestamp=None):
    if timestamp is None:
        timestamp = datetime.now(tz)

    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO feedback (conversation_id, feedback, timestamp) VALUES (%s, %s, COALESCE(%s, CURRENT_TIMESTAMP))",
                (conversation_id, feedback, timestamp),
            )
        conn.commit()
    finally:
        conn.close()


def get_recent_conversations(limit=5, relevance=None):
    conn = get_db_connection()

    try:
        with conn.cursor(cursor_factory=DictCursor) as cur:
            query = """
                SELECT c.*, f.feedback
                FROM conversations c
                LEFT JOIN feedback f ON c.id = f.conversation_id
            """
            if relevance:
                query += f" WHERE c.relevance = '{relevance}'"
            query += " ORDER BY c.timestamp DESC LIMIT %s"

            cur.execute(query, (limit,))
            return cur.fetchall()
    finally:
        conn.close()


def get_feedback_stats():
    conn = get_db_connection()
    try:
        with conn.cursor(cursor_factory=DictCursor) as cur:
            cur.execute("""
                SELECT 
                    SUM(CASE WHEN feedback > 0 THEN 1 ELSE 0 END) as thumbs_up,
                    SUM(CASE WHEN feedback < 0 THEN 1 ELSE 0 END) as thumbs_down
                FROM feedback
            """)
            return cur.fetchone()
    finally:
        conn.close()
