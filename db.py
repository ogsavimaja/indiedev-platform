import sqlite3
from flask import g

# Creates a connection to the database
def get_connection():
    con = sqlite3.connect("database.db")
    con.execute("PRAGMA foreign_keys = ON")
    con.row_factory = sqlite3.Row
    return con

# Executes a SQLite statement that modifies the database
def execute(sql, params=[]):
    con = get_connection()
    result = con.execute(sql, params)
    con.commit()
    g.last_insert_id = result.lastrowid
    con.close()

# Returns the last inserted id
def last_insert_id():
    return g.last_insert_id

# Executes a SQLite query that returns a result
def query(sql, params=[]):
    con = get_connection()
    result = con.execute(sql, params).fetchall()
    con.close()
    return result
