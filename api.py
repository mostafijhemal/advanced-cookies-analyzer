# api.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from cookie_collector import get_cookies_from_site
from db_handler import init_db, insert_cookie, fetch_all_cookies

app = FastAPI(title="Advanced Cookies Analyzer API", description="Enterprise API for Cookie Analytics")
conn = init_db("output/cookies.db")

class ScanRequest(BaseModel):
    url: str

@app.get("/")
def read_root():
    return {"status": "Online", "message": "Welcome to the Cookies Analyzer API"}

@app.get("/api/v1/cookies")
def get_all_cookies():
    try:
        rows = fetch_all_cookies()
        return {"total_records": len(rows), "data": rows}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/scan")
def scan_website(request: ScanRequest):
    try:
        cookies = get_cookies_from_site(request.url)
        for cookie in cookies:
            insert_cookie(conn, request.url, cookie)
        return {
            "status": "success", 
            "target_url": request.url, 
            "cookies_found": len(cookies),
            "message": "Data successfully saved to database."
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# This API can be used by any developer to integrate your cookie scanning engine into their software or mobile app.