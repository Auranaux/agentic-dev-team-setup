from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List
import uuid
from datetime import datetime
from app.backend.models import Draft
from app.backend.deps import get_db
from pydantic import BaseModel

router = APIRouter()

class DraftCreate(BaseModel):
    owner: str
    payload: dict

class DraftUpdate(BaseModel):
    owner: str = None
    payload: dict = None

class DraftResponse(BaseModel):
    id: str
    owner: str
    payload: dict
    updated_at: datetime
    
    class Config:
        from_attributes = True

@router.get("/drafts", response_model=List[DraftResponse])
def list_drafts(db: Session = Depends(get_db)):
    """List all drafts"""
    drafts = db.query(Draft).all()
    return drafts

@router.post("/drafts", response_model=DraftResponse, status_code=201)
def create_draft(draft: DraftCreate, db: Session = Depends(get_db)):
    """Create a new draft"""
    db_draft = Draft(
        id=str(uuid.uuid4()),
        owner=draft.owner,
        payload=draft.payload,
        updated_at=datetime.utcnow()
    )
    db.add(db_draft)
    db.commit()
    db.refresh(db_draft)
    return db_draft

@router.get("/drafts/{id}", response_model=DraftResponse)
def get_draft(id: str, db: Session = Depends(get_db)):
    """Get a draft by ID"""
    draft = db.query(Draft).filter(Draft.id == id).first()
    if not draft:
        raise HTTPException(status_code=404, detail="Draft not found")
    return draft

@router.put("/drafts/{id}", response_model=DraftResponse)
def update_draft(id: str, draft_update: DraftUpdate, db: Session = Depends(get_db)):
    """Update a draft"""
    draft = db.query(Draft).filter(Draft.id == id).first()
    if not draft:
        raise HTTPException(status_code=404, detail="Draft not found")
    
    if draft_update.owner is not None:
        draft.owner = draft_update.owner
    if draft_update.payload is not None:
        draft.payload = draft_update.payload
    
    draft.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(draft)
    return draft

@router.delete("/drafts/{id}", status_code=204)
def delete_draft(id: str, db: Session = Depends(get_db)):
    """Delete a draft"""
    draft = db.query(Draft).filter(Draft.id == id).first()
    if not draft:
        raise HTTPException(status_code=404, detail="Draft not found")
    
    db.delete(draft)
    db.commit()
    return None
