from fastapi import FastAPI, HTTPException
import mysql.connector
import logging
from collections import Counter

 
app = FastAPI()
 
# Database connection setup
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",  
        user="root",      
        password="Jio@2024",  
        database="newsschema"  
    )
 
# Configure logging
logging.basicConfig(level=logging.DEBUG)
 
# API endpoint to get featured news
@app.get("/api/featured-news")
async def get_featured_news():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM extractednews WHERE Published IS NOT NULL ORDER BY Published DESC")
        news = cursor.fetchall()
        return {"featured_news": news}
    except Exception as e:
        logging.error(f"Error fetching featured news: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
 

# Run the server using:
# uvicorn app:app --host 0.0.0.0 --port 8000 --reload

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



   # API endpoint for "Knowledge Hub" section
@app.get("/api/knowledge-hub")
async def get_knowledge_hub():
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        # Correct SQL query
        cursor.execute("SELECT * FROM extractednews WHERE Link LIKE '%publication%' ORDER BY Published DESC")
        knowledge_hub = cursor.fetchall()
        return {"knowledge_hub": knowledge_hub}
    except Exception as e:
        logging.error(f"Error fetching knowledge hub: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


# API endpoint for "Around the Globe" section with "preventionweb" filter
@app.get("/api/around-the-globe")
async def get_around_the_globe():
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        # SQL query to filter by both 'news' and 'preventionweb'
        cursor.execute("SELECT * FROM extractednews WHERE Link LIKE '%preventionweb%' AND Link LIKE '%news%' ORDER BY Published DESC")
        globe_news = cursor.fetchall()
        return {"around_the_globe": globe_news}
    except Exception as e:
        logging.error(f"Error fetching around the globe news: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


# API endpoint to get trending news based on the most frequent category keyword
@app.get("/api/trending-news")
async def get_trending_news():
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        
        cursor.execute("SELECT * FROM extractednews ORDER BY Published DESC LIMIT 25")
        news = cursor.fetchall()
        
        
        category_keywords = [row['Category'] for row in news if row['Category']]
        
       
        all_keywords = []
        for keywords in category_keywords:
            all_keywords.extend(keywords.split(','))  
        
       
        keyword_counter = Counter(all_keywords)
        
        
        if not keyword_counter:
            return {"trending_news": []}  
        
        most_common_keyword, _ = keyword_counter.most_common(1)[0]
        
       
        cursor.execute(f"SELECT * FROM extractednews WHERE FIND_IN_SET('{most_common_keyword}', Category) ORDER BY Published DESC")
        trending_news = cursor.fetchall()
        
        return {"trending_news": trending_news}
    
    except Exception as e:
        logging.error(f"Error fetching trending news: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
    
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()            







