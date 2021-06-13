import sqlite3


def connect():
    conn = sqlite3.connect('a4.db')
    conn.row_factory = sqlite3.Row
    return conn


def resetDB():

    with connect() as db:
        db.execute("DROP TABLE IF EXISTS MCOption")
        db.execute("""
                  CREATE TABLE MCOption (
                    id INTEGER PRIMARY KEY,
                    is_true INTEGER,
                    option_text TEXT,
                    qid INTEGER,
                    FOREIGN KEY(qid) REFERENCES Question(id)
                  )
        """)

    with connect() as db:
        db.execute("DROP TABLE IF EXISTS Rubric")
        db.execute("""
                  CREATE TABLE Rubric (
                    id INTEGER PRIMARY KEY,
                    rubric_text TEXT,
                    points REAL,
                    qid INTEGER,
                    FOREIGN KEY(qid) REFERENCES Question(id)
                  )
        """)

    with connect() as db:
        db.execute("DROP TABLE IF EXISTS Setup")
        db.execute("""
                  CREATE TABLE Setup (
                    id INTEGER PRIMARY KEY,
                    setup_text TEXT
                  )
        """)

    # new code
    with connect() as db:
        db.execute("DROP TABLE IF EXISTS Question")
        db.execute("""
                  CREATE TABLE Question (
                    id INTEGER PRIMARY KEY,
                    type TEXT,
                    question_text TEXT,
                    points REAL,
                    setup INTEGER DEFAULT NULL,
                    FOREIGN KEY(setup) REFERENCES Question(id)

                  )
      """)

    with connect() as db:
        db.execute("DROP TABLE IF EXISTS Answer")
        db.execute("""
                  CREATE TABLE Answer (
                    id INTEGER PRIMARY KEY,
                    answer_text TEXT,
                    qid INTEGER,
                    FOREIGN KEY(qid) REFERENCES Question(id)
                  )
      """)


if __name__ == "__main__":
    print("Resetting database")
    resetDB()
