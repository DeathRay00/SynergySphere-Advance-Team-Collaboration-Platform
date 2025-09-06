from database import engine, Base
from models import User, Project, Task, Comment, project_members
from passlib.context import CryptContext
import os

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def init_db():
    """Initialize the database with tables"""
    # Create all tables
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully!")

def create_sample_data():
    """Create sample data for testing"""
    from sqlalchemy.orm import sessionmaker
    from database import engine
    
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # Check if users already exist
        if db.query(User).first():
            print("Sample data already exists!")
            return
        
        # Create sample users
        hashed_password = pwd_context.hash("password123")
        
        user1 = User(
            name="John Doe",
            email="john@example.com",
            password=hashed_password
        )
        user2 = User(
            name="Jane Smith",
            email="jane@example.com",
            password=hashed_password
        )
        
        db.add(user1)
        db.add(user2)
        db.commit()
        
        # Create sample project
        project = Project(
            name="Sample Project",
            description="This is a sample project for testing",
            created_by=user1.id,
            members=[user1, user2]
        )
        
        db.add(project)
        db.commit()
        
        # Create sample tasks
        task1 = Task(
            project_id=project.id,
            title="Setup database",
            description="Initialize the database with proper schema",
            assignee_id=user1.id,
            created_by=user1.id,
            status="Done"
        )
        
        task2 = Task(
            project_id=project.id,
            title="Create API endpoints",
            description="Implement all necessary API endpoints",
            assignee_id=user2.id,
            created_by=user1.id,
            status="In Progress"
        )
        
        db.add(task1)
        db.add(task2)
        db.commit()
        
        # Create sample comment
        comment = Comment(
            project_id=project.id,
            user_id=user1.id,
            message="Great progress on the project setup!"
        )
        
        db.add(comment)
        db.commit()
        
        print("Sample data created successfully!")
        print("Sample users:")
        print("- john@example.com / password123")
        print("- jane@example.com / password123")
        
    except Exception as e:
        print(f"Error creating sample data: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    init_db()
    create_sample_data()
