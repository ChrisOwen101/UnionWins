from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

from src.database import get_db, SessionLocal
from src.models import ScrapeSourceDB
from src.services import scraping_service

router = APIRouter(prefix="/api/scraping", tags=["scraping"])

class ScrapeSourceCreate(BaseModel):
    url: str
    organization_name: Optional[str] = None

class ScrapeSourceResponse(BaseModel):
    id: int
    url: str
    organization_name: Optional[str]
    last_scraped_at: Optional[datetime]
    is_active: int
    created_at: datetime
    
    class Config:
        from_attributes = True

def _background_scrape_source(source_id: int):
    db = SessionLocal()
    try:
        scraping_service.run_scrape_for_source(db, source_id)
    except Exception as e:
        print(f"Error in background scrape for {source_id}: {e}")
    finally:
        db.close()

def _background_scrape_all():
    db = SessionLocal()
    try:
        scraping_service.run_all_scrapes(db)
    except Exception as e:
        print(f"Error in background scrape all: {e}")
    finally:
        db.close()

@router.get("/sources", response_model=List[ScrapeSourceResponse])
def get_sources(db: Session = Depends(get_db)):
    return db.query(ScrapeSourceDB).filter(ScrapeSourceDB.is_active == 1).all()

@router.post("/sources", response_model=ScrapeSourceResponse)
def add_source(source: ScrapeSourceCreate, db: Session = Depends(get_db)):
    # Check if exists (active or inactive)
    existing = db.query(ScrapeSourceDB).filter(ScrapeSourceDB.url == source.url).first()
    if existing:
        if existing.is_active == 0:
            existing.is_active = 1
            existing.organization_name = source.organization_name
            db.commit()
            db.refresh(existing)
            return existing
        raise HTTPException(status_code=400, detail="Source already exists")
    
    new_source = ScrapeSourceDB(
        url=source.url,
        organization_name=source.organization_name
    )
    db.add(new_source)
    db.commit()
    db.refresh(new_source)
    return new_source

@router.delete("/sources/{source_id}")
def delete_source(source_id: int, db: Session = Depends(get_db)):
    source = db.query(ScrapeSourceDB).filter(ScrapeSourceDB.id == source_id).first()
    if not source:
        raise HTTPException(status_code=404, detail="Source not found")
    
    # Soft delete
    source.is_active = 0
    db.commit()
    return {"status": "success"}

@router.post("/run/{source_id}")
def run_scrape(source_id: int, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    source = db.query(ScrapeSourceDB).filter(ScrapeSourceDB.id == source_id).first()
    if not source:
        raise HTTPException(status_code=404, detail="Source not found")
        
    background_tasks.add_task(_background_scrape_source, source_id)
    return {"status": "started", "message": f"Scraping started for {source.url}"}

@router.post("/run-all")
def run_all_scrapes(background_tasks: BackgroundTasks):
    background_tasks.add_task(_background_scrape_all)
    return {"status": "started", "message": "Scraping all sources"}
