from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from config import settings
from models.base import Base

# Create database engine
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {}
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db() -> Session:
    """Dependency for getting database session in FastAPI"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def run_safe_migrations():
    """Safely apply column migrations on SQLite database without deleting tables"""
    from sqlalchemy import inspect
    inspector = inspect(engine)
    
    # Check if tables exist
    table_names = inspector.get_table_names()
    
    if "users" in table_names:
        cols_info = inspector.get_columns("users")
        id_col = next((c for c in cols_info if c["name"] == "id"), None)
        
        # Check if the existing ID column is an INTEGER
        if id_col and "INT" in str(id_col["type"]).upper():
            print("Migration: Converting SQLite users.id column to VARCHAR for UUID support...")
            with engine.connect() as conn:
                # 1. Rename existing users table
                conn.execute(text("ALTER TABLE users RENAME TO users_old"))
                conn.commit()
                
                # 2. Drop legacy indices if they exist to prevent name collisions
                try:
                    conn.execute(text("DROP INDEX IF EXISTS ix_users_email"))
                    conn.execute(text("DROP INDEX IF EXISTS ix_users_username"))
                    conn.commit()
                except Exception as index_err:
                    print(f"Index drop warning: {index_err}")
                
                # 3. Create new tables matching the new schema
                Base.metadata.create_all(bind=engine)
                
                # 4. Copy records with ID casting
                conn.execute(text("""
                    INSERT INTO users (id, email, username, hashed_password, is_active, created_at, updated_at)
                    SELECT CAST(id AS TEXT), email, username, hashed_password, is_active, created_at, updated_at
                    FROM users_old
                """))
                conn.commit()
                
                # 5. Drop legacy table
                conn.execute(text("DROP TABLE users_old"))
                conn.commit()
                
            # Re-initialize inspector with new table state
            inspector = inspect(engine)
            table_names = inspector.get_table_names()
            
        columns = [col["name"] for col in inspector.get_columns("users")]
        
        # Add last_login to users if missing
        if "last_login" not in columns:
            print("Migration: Adding last_login column to users table...")
            with engine.connect() as conn:
                conn.execute(text("ALTER TABLE users ADD COLUMN last_login TIMESTAMP"))
                conn.commit()
                
        # Add remember_token to users if missing
        if "remember_token" not in columns:
            print("Migration: Adding remember_token column to users table...")
            with engine.connect() as conn:
                conn.execute(text("ALTER TABLE users ADD COLUMN remember_token VARCHAR(64)"))
                conn.commit()

    if "medications" in table_names:
        columns = [col["name"] for col in inspector.get_columns("medications")]
        
        # Add notes to medications if missing
        if "notes" not in columns:
            print("Migration: Adding notes column to medications table...")
            with engine.connect() as conn:
                conn.execute(text("ALTER TABLE medications ADD COLUMN notes TEXT"))
                conn.commit()

        # Add prescribed_by to medications if missing
        if "prescribed_by" not in columns:
            print("Migration: Adding prescribed_by column to medications table...")
            with engine.connect() as conn:
                conn.execute(text("ALTER TABLE medications ADD COLUMN prescribed_by VARCHAR(255)"))
                conn.commit()

def init_db():
    """Initialize database tables and run safe column migrations"""
    # 1. Run migrations first on existing tables
    try:
        run_safe_migrations()
    except Exception as e:
        print(f"Safe migrations encountered an error: {e}")
        
    # 2. Create all missing tables
    Base.metadata.create_all(bind=engine)

def drop_db():
    """Drop all database tables (for testing/reset)"""
    Base.metadata.drop_all(bind=engine)
