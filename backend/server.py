from fastapi import FastAPI, APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from database import get_db
from models import User, Project, Task, Comment, project_members
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional
import uuid
from datetime import datetime, timedelta, timezone
import jwt
from passlib.context import CryptContext

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# Import config
from config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES, CORS_ORIGINS

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Helper functions
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception
    
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise credentials_exception
    return user

# Data Models
class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: str
    name: str
    email: str
    avatar_url: Optional[str] = None
    created_at: datetime

class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse

class ProjectCreate(BaseModel):
    name: str
    description: Optional[str] = None
    deadline: Optional[datetime] = None

class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    deadline: Optional[datetime] = None

class ProjectResponse(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    created_by: str
    created_by_name: Optional[str] = None
    deadline: Optional[datetime] = None
    created_at: datetime
    members: List[str] = []
    member_details: List[UserResponse] = []
    task_count: int = 0

class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    assignee_id: Optional[str] = None
    due_date: Optional[datetime] = None
    status: str = "To-Do"

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    assignee_id: Optional[str] = None
    due_date: Optional[datetime] = None
    status: Optional[str] = None

class TaskResponse(BaseModel):
    id: str
    project_id: str
    title: str
    description: Optional[str] = None
    assignee_id: Optional[str] = None
    assignee_name: Optional[str] = None
    due_date: Optional[datetime] = None
    status: str
    created_by: str
    created_at: datetime
    updated_at: datetime

class CommentCreate(BaseModel):
    message: str

class CommentResponse(BaseModel):
    id: str
    project_id: str
    user_id: str
    user_name: str
    message: str
    timestamp: datetime

class AddMemberRequest(BaseModel):
    email: str

# Authentication Routes
@api_router.post("/auth/register", response_model=Token)
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Hash password and create user
    hashed_password = get_password_hash(user_data.password)
    user = User(
        name=user_data.name,
        email=user_data.email,
        password=hashed_password
    )
    
    # Save to database
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.id}, expires_delta=access_token_expires
    )
    
    user_response = UserResponse(
        id=user.id,
        name=user.name,
        email=user.email,
        avatar_url=user.avatar_url,
        created_at=user.created_at
    )
    
    return Token(access_token=access_token, token_type="bearer", user=user_response)

@api_router.post("/auth/login", response_model=Token)
async def login(user_data: UserLogin, db: Session = Depends(get_db)):
    # Find user
    user = db.query(User).filter(User.email == user_data.email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Verify password
    if not verify_password(user_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.id}, expires_delta=access_token_expires
    )
    
    user_response = UserResponse(
        id=user.id,
        name=user.name,
        email=user.email,
        avatar_url=user.avatar_url,
        created_at=user.created_at
    )
    
    return Token(access_token=access_token, token_type="bearer", user=user_response)

@api_router.get("/auth/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    return UserResponse(
        id=current_user.id,
        name=current_user.name,
        email=current_user.email,
        avatar_url=current_user.avatar_url,
        created_at=current_user.created_at
    )

# Project Routes
@api_router.post("/projects", response_model=ProjectResponse)
async def create_project(project_data: ProjectCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    project = Project(
        name=project_data.name,
        description=project_data.description,
        deadline=project_data.deadline,
        created_by=current_user.id
    )
    
    # Add creator as member
    project.members.append(current_user)
    
    db.add(project)
    db.commit()
    db.refresh(project)
    
    # Get member details
    member_details = [UserResponse(
        id=member.id,
        name=member.name,
        email=member.email,
        avatar_url=member.avatar_url,
        created_at=member.created_at
    ) for member in project.members]
    
    # Get task count
    task_count = db.query(Task).filter(Task.project_id == project.id).count()
    
    return ProjectResponse(
        id=project.id,
        name=project.name,
        description=project.description,
        created_by=project.created_by,
        created_by_name=current_user.name,
        deadline=project.deadline,
        created_at=project.created_at,
        members=[member.id for member in project.members],
        member_details=member_details,
        task_count=task_count
    )

@api_router.get("/projects", response_model=List[ProjectResponse])
async def get_projects(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    projects = db.query(Project).filter(Project.members.any(User.id == current_user.id)).all()
    
    project_responses = []
    for project in projects:
        # Get member details
        member_details = [UserResponse(
            id=member.id,
            name=member.name,
            email=member.email,
            avatar_url=member.avatar_url,
            created_at=member.created_at
        ) for member in project.members]
        
        # Get creator name
        creator = db.query(User).filter(User.id == project.created_by).first()
        created_by_name = creator.name if creator else "Unknown"
        
        # Get task count
        task_count = db.query(Task).filter(Task.project_id == project.id).count()
        
        project_responses.append(ProjectResponse(
            id=project.id,
            name=project.name,
            description=project.description,
            created_by=project.created_by,
            created_by_name=created_by_name,
            deadline=project.deadline,
            created_at=project.created_at,
            members=[member.id for member in project.members],
            member_details=member_details,
            task_count=task_count
        ))
    
    return project_responses

@api_router.get("/projects/{project_id}", response_model=ProjectResponse)
async def get_project(project_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Check if user is a member
    if current_user not in project.members:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Get member details
    member_details = [UserResponse(
        id=member.id,
        name=member.name,
        email=member.email,
        avatar_url=member.avatar_url,
        created_at=member.created_at
    ) for member in project.members]
    
    # Get creator name
    creator = db.query(User).filter(User.id == project.created_by).first()
    created_by_name = creator.name if creator else "Unknown"
    
    # Get task count
    task_count = db.query(Task).filter(Task.project_id == project.id).count()
    
    return ProjectResponse(
        id=project.id,
        name=project.name,
        description=project.description,
        created_by=project.created_by,
        created_by_name=created_by_name,
        deadline=project.deadline,
        created_at=project.created_at,
        members=[member.id for member in project.members],
        member_details=member_details,
        task_count=task_count
    )

@api_router.put("/projects/{project_id}", response_model=ProjectResponse)
async def update_project(project_id: str, project_data: ProjectUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Check if user is the creator
    if project.created_by != current_user.id:
        raise HTTPException(status_code=403, detail="Only project creator can update project")
    
    # Update project fields
    if project_data.name is not None:
        project.name = project_data.name
    if project_data.description is not None:
        project.description = project_data.description
    if project_data.deadline is not None:
        project.deadline = project_data.deadline
    
    db.commit()
    db.refresh(project)
    
    # Get member details
    member_details = [UserResponse(
        id=member.id,
        name=member.name,
        email=member.email,
        avatar_url=member.avatar_url,
        created_at=member.created_at
    ) for member in project.members]
    
    # Get task count
    task_count = db.query(Task).filter(Task.project_id == project_id).count()
    
    return ProjectResponse(
        id=project.id,
        name=project.name,
        description=project.description,
        created_by=project.created_by,
        created_by_name=current_user.name,
        deadline=project.deadline,
        created_at=project.created_at,
        members=[member.id for member in project.members],
        member_details=member_details,
        task_count=task_count
    )

@api_router.delete("/projects/{project_id}")
async def delete_project(project_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Check if user is the creator
    if project.created_by != current_user.id:
        raise HTTPException(status_code=403, detail="Only project creator can delete project")
    
    # Delete the project (cascade will handle tasks and comments)
    db.delete(project)
    db.commit()
    
    return {"message": "Project deleted successfully"}

@api_router.post("/projects/{project_id}/members")
async def add_member(project_id: str, member_data: AddMemberRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Check if current user is the creator
    if project.created_by != current_user.id:
        raise HTTPException(status_code=403, detail="Only project creator can add members")
    
    # Find user by email
    user = db.query(User).filter(User.email == member_data.email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Add to members if not already a member
    if user not in project.members:
        project.members.append(user)
        db.commit()
    
    return {"message": "Member added successfully"}

# Task Routes
@api_router.post("/projects/{project_id}/tasks", response_model=TaskResponse)
async def create_task(project_id: str, task_data: TaskCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    # Check if project exists and user is a member
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    if current_user not in project.members:
        raise HTTPException(status_code=403, detail="Access denied")
    
    task = Task(
        project_id=project_id,
        title=task_data.title,
        description=task_data.description,
        assignee_id=task_data.assignee_id,
        due_date=task_data.due_date,
        status=task_data.status,
        created_by=current_user.id
    )
    
    db.add(task)
    db.commit()
    db.refresh(task)
    
    # Get assignee name if assigned
    assignee_name = None
    if task.assignee_id:
        assignee = db.query(User).filter(User.id == task.assignee_id).first()
        if assignee:
            assignee_name = assignee.name
    
    return TaskResponse(
        id=task.id,
        project_id=task.project_id,
        title=task.title,
        description=task.description,
        assignee_id=task.assignee_id,
        assignee_name=assignee_name,
        due_date=task.due_date,
        status=task.status,
        created_by=task.created_by,
        created_at=task.created_at,
        updated_at=task.updated_at
    )

@api_router.get("/projects/{project_id}/tasks", response_model=List[TaskResponse])
async def get_tasks(project_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    # Check if project exists and user is a member
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    if current_user not in project.members:
        raise HTTPException(status_code=403, detail="Access denied")
    
    tasks = db.query(Task).filter(Task.project_id == project_id).all()
    
    task_responses = []
    for task in tasks:
        # Get assignee name if assigned
        assignee_name = None
        if task.assignee_id:
            assignee = db.query(User).filter(User.id == task.assignee_id).first()
            if assignee:
                assignee_name = assignee.name
        
        task_responses.append(TaskResponse(
            id=task.id,
            project_id=task.project_id,
            title=task.title,
            description=task.description,
            assignee_id=task.assignee_id,
            assignee_name=assignee_name,
            due_date=task.due_date,
            status=task.status,
            created_by=task.created_by,
            created_at=task.created_at,
            updated_at=task.updated_at
        ))
    
    return task_responses

@api_router.put("/tasks/{task_id}", response_model=TaskResponse)
async def update_task(task_id: str, task_data: TaskUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Check if user is a member of the project
    project = db.query(Project).filter(Project.id == task.project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    if current_user not in project.members:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Update task fields
    if task_data.title is not None:
        task.title = task_data.title
    if task_data.description is not None:
        task.description = task_data.description
    if task_data.assignee_id is not None:
        task.assignee_id = task_data.assignee_id
    if task_data.due_date is not None:
        task.due_date = task_data.due_date
    if task_data.status is not None:
        task.status = task_data.status
    
    task.updated_at = datetime.now(timezone.utc)
    
    db.commit()
    db.refresh(task)
    
    # Get assignee name if assigned
    assignee_name = None
    if task.assignee_id:
        assignee = db.query(User).filter(User.id == task.assignee_id).first()
        if assignee:
            assignee_name = assignee.name
    
    return TaskResponse(
        id=task.id,
        project_id=task.project_id,
        title=task.title,
        description=task.description,
        assignee_id=task.assignee_id,
        assignee_name=assignee_name,
        due_date=task.due_date,
        status=task.status,
        created_by=task.created_by,
        created_at=task.created_at,
        updated_at=task.updated_at
    )

@api_router.delete("/tasks/{task_id}")
async def delete_task(task_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Check if user is a member of the project
    project = db.query(Project).filter(Project.id == task.project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    if current_user not in project.members:
        raise HTTPException(status_code=403, detail="Access denied")
    
    db.delete(task)
    db.commit()
    return {"message": "Task deleted successfully"}

# Comment Routes
@api_router.post("/projects/{project_id}/comments", response_model=CommentResponse)
async def create_comment(project_id: str, comment_data: CommentCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    # Check if project exists and user is a member
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    if current_user not in project.members:
        raise HTTPException(status_code=403, detail="Access denied")
    
    comment = Comment(
        project_id=project_id,
        user_id=current_user.id,
        message=comment_data.message
    )
    
    db.add(comment)
    db.commit()
    db.refresh(comment)
    
    return CommentResponse(
        id=comment.id,
        project_id=comment.project_id,
        user_id=comment.user_id,
        user_name=current_user.name,
        message=comment.message,
        timestamp=comment.timestamp
    )

@api_router.get("/projects/{project_id}/comments", response_model=List[CommentResponse])
async def get_comments(project_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    # Check if project exists and user is a member
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    if current_user not in project.members:
        raise HTTPException(status_code=403, detail="Access denied")
    
    comments = db.query(Comment).filter(Comment.project_id == project_id).all()
    
    comment_responses = []
    for comment in comments:
        user = db.query(User).filter(User.id == comment.user_id).first()
        user_name = user.name if user else "Unknown User"
        
        comment_responses.append(CommentResponse(
            id=comment.id,
            project_id=comment.project_id,
            user_id=comment.user_id,
            user_name=user_name,
            message=comment.message,
            timestamp=comment.timestamp
        ))
    
    return comment_responses

# Get user's tasks
@api_router.get("/users/me/tasks", response_model=List[TaskResponse])
async def get_my_tasks(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    tasks = db.query(Task).filter(Task.assignee_id == current_user.id).all()
    
    task_responses = []
    for task in tasks:
        task_responses.append(TaskResponse(
            id=task.id,
            project_id=task.project_id,
            title=task.title,
            description=task.description,
            assignee_id=task.assignee_id,
            assignee_name=current_user.name,
            due_date=task.due_date,
            status=task.status,
            created_by=task.created_by,
            created_at=task.created_at,
            updated_at=task.updated_at
        ))
    
    return task_responses

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=CORS_ORIGINS,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)