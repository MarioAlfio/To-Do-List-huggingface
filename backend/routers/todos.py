from typing import List
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, status
import schemas
import crud
from database import SessionLocal
from transformers import pipeline

router = APIRouter(
    prefix="/todos"
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("", status_code=status.HTTP_201_CREATED)
def create_todo(todo: schemas.ToDoRequest, db: Session = Depends(get_db)):
    todo = crud.create_todo(db, todo)
    return todo

@router.get("", response_model=List[schemas.ToDoResponse])
def get_todos(completed: bool = None, db: Session = Depends(get_db)):
    todos = crud.read_todos(db, completed)
    return todos

@router.get("/{id}")
def get_todo_by_id(id: int, db: Session = Depends(get_db)):
    todo = crud.read_todo(db, id)
    if todo is None:
        raise HTTPException(status_code=404, detail="to do not found")
    return todo

@router.put("/{id}")
def update_todo(id: int, todo: schemas.ToDoRequest, db: Session = Depends(get_db)):
    todo = crud.update_todo(db, id, todo)
    if todo is None:
        raise HTTPException(status_code=404, detail="to do not found")
    return todo

@router.delete("/{id}", status_code=status.HTTP_200_OK)
def delete_todo(id: int, db: Session = Depends(get_db)):
    res = crud.delete_todo(db, id)
    if res is None:
        raise HTTPException(status_code=404, detail="to do not found")

# Use a pipeline for text generation
text_generation_pipeline = pipeline("text-generation", model="openai-community/gpt2-large", truncation=True,pad_token_id=50256)
    
@router.post('/summarize-text')
async def summarize_text(text: str):
    summary = text_generation_pipeline(text, max_length=100, do_sample=False)[0]['generated_text']
    return {'summary': summary}

@router.post("/write-poem/{id}")
async def get_todo_by_id(id: int, db: Session = Depends(get_db)):
    todo = crud.read_todo(db, id)
    if todo is None:
        raise HTTPException(status_code=404, detail="to do not found")
    poem = text_generation_pipeline(todo.name, max_length=50, do_sample=True, temperature=0.7)[0]['generated_text']
    return {'poem': poem}
