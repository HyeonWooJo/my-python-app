from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import os
import uuid

app = FastAPI()

# Todo 모델 정의
class TodoCreate(BaseModel):
    title: str
    description: Optional[str] = None

class TodoUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    completed: Optional[bool] = None

class Todo(BaseModel):
    id: str
    title: str
    description: Optional[str] = None
    completed: bool = False
    created_at: str
    updated_at: str

# 인메모리 저장소 (실제 환경에서는 데이터베이스 사용)
todos_db: dict[str, Todo] = {}

@app.get("/")
def read_root():
    # 환경 변수를 통해 어떤 환경(Dev/Prod)인지 출력
    env = os.getenv("APP_ENV", "local")
    return {"Hello": "World", "Environment": env}

@app.get("/healthz")
def health_check():
    return {"status": "ok"}

@app.get("/version")
def version():
    return {"version": "1.0.0"}

# Todo API 엔드포인트
@app.post("/todos", response_model=Todo, status_code=201)
def create_todo(todo: TodoCreate):
    """새로운 할일 생성"""
    todo_id = str(uuid.uuid4())
    now = datetime.now().isoformat()
    
    new_todo = Todo(
        id=todo_id,
        title=todo.title,
        description=todo.description,
        completed=False,
        created_at=now,
        updated_at=now
    )
    todos_db[todo_id] = new_todo
    return new_todo

@app.get("/todos", response_model=List[Todo])
def get_todos(completed: Optional[bool] = None):
    """할일 목록 조회 (completed 필터 옵션)"""
    todos = list(todos_db.values())
    
    if completed is not None:
        todos = [todo for todo in todos if todo.completed == completed]
    
    return todos

@app.get("/todos/{todo_id}", response_model=Todo)
def get_todo(todo_id: str):
    """특정 할일 조회"""
    if todo_id not in todos_db:
        raise HTTPException(status_code=404, detail="Todo not found")
    return todos_db[todo_id]

@app.put("/todos/{todo_id}", response_model=Todo)
def update_todo(todo_id: str, todo_update: TodoUpdate):
    """할일 수정"""
    if todo_id not in todos_db:
        raise HTTPException(status_code=404, detail="Todo not found")
    
    todo = todos_db[todo_id]
    
    if todo_update.title is not None:
        todo.title = todo_update.title
    if todo_update.description is not None:
        todo.description = todo_update.description
    if todo_update.completed is not None:
        todo.completed = todo_update.completed
    
    todo.updated_at = datetime.now().isoformat()
    todos_db[todo_id] = todo
    
    return todo

@app.patch("/todos/{todo_id}/complete", response_model=Todo)
def complete_todo(todo_id: str):
    """할일 완료 처리"""
    if todo_id not in todos_db:
        raise HTTPException(status_code=404, detail="Todo not found")
    
    todo = todos_db[todo_id]
    todo.completed = True
    todo.updated_at = datetime.now().isoformat()
    todos_db[todo_id] = todo
    
    return todo

@app.delete("/todos/{todo_id}", status_code=204)
def delete_todo(todo_id: str):
    """할일 삭제"""
    if todo_id not in todos_db:
        raise HTTPException(status_code=404, detail="Todo not found")
    
    del todos_db[todo_id]
    return None