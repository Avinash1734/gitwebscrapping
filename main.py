from fastapi import FastAPI, HTTPException
import mysql.connector
from mysql.connector import Error
 
app = FastAPI()
 
# Database connection setup
def get_db_connection():
    try:
        return mysql.connector.connect(
            host="localhost",
            user="root",
            password="Jio@2024",
            database="newsschema"
        )
    except Error as e:
        raise HTTPException(status_code=500, detail=f"Database connection error: {str(e)}")
 
# API endpoint to get disaster alerts (where 'Published' is NULL)
@app.get("/api/alerts")
async def get_alerts():
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM extractednews WHERE Published IS NULL ORDER BY Published DESC")
        alerts = cursor.fetchall()
        return {"alerts": alerts}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching alerts: {str(e)}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
 
@app.get("/api/featurednews")
async def get_featured_news():
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM extractednews WHERE Published IS NOT NULL ORDER BY Published DESC")
        news = cursor.fetchall()
        return {"featured_news": news}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching featured news: {str(e)}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()