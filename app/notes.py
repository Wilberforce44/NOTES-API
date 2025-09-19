from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from .db import get_db
from . import models, schemas
from .deps import get_current_user

router = APIRouter(prefix="/notes", tags=["notes"])

@router.post("", response_model=schemas.NotePublic, status_code=status.HTTP_201_CREATED)
def create_note(
    note_in: schemas.NoteCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    note = models.Note(
        owner_id=current_user.id,
        title=note_in.title,
        content=note_in.content,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    db.add(note)
    db.commit()
    db.refresh(note)
    return note

@router.get("", response_model=list[schemas.NotePublic])
def list_notes(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    notes = (
        db.query(models.Note)
        .filter(models.Note.owner_id == current_user.id)
        .order_by(models.Note.created_at.desc())
        .all()
    )
    return notes
@router.get("/{note_id}", response_model=schemas.NotePublic)
def get_note(
    note_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    note = (
        db.query(models.Note)
        .filter(models.Note.id == note_id, models.Note.owner_id == current_user.id)
        .first()
    )
    if not note:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")
    return note


@router.put("/{note_id}", response_model=schemas.NotePublic)
def update_note(
    note_id: int,
    note_in: schemas.NoteUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    note = (
        db.query(models.Note)
        .filter(models.Note.id == note_id, models.Note.owner_id == current_user.id)
        .first()
    )
    if not note:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")

    if note_in.title is not None:
        note.title = note_in.title
    if note_in.content is not None:
        note.content = note_in.content
    if note_in.is_archived is not None:
        note.is_archived = note_in.is_archived

    note.updated_at = datetime.utcnow()
    db.add(note)
    db.commit()
    db.refresh(note)
    return note


@router.delete("/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_note(
    note_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    note = (
        db.query(models.Note)
        .filter(models.Note.id == note_id, models.Note.owner_id == current_user.id)
        .first()
    )
    if not note:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")

    db.delete(note)
    db.commit()
    return
