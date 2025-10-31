"""
Migration script to add 'name' column to users table
"""
from app import create_app
from models import db

def migrate():
    app = create_app()
    
    with app.app_context():
        # Check if column already exists
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        columns = [col['name'] for col in inspector.get_columns('users')]
        
        if 'name' in columns:
            print("Column 'name' already exists in users table. Skipping migration.")
            return
        
        # Add the name column
        print("Adding 'name' column to users table...")
        db.engine.execute('ALTER TABLE users ADD COLUMN name VARCHAR(100)')
        
        # Update existing organizers: set name = username as default
        print("Updating existing organizers with default name...")
        db.engine.execute("UPDATE users SET name = username WHERE role = 'organizer' AND name IS NULL")
        
        print("Migration completed successfully!")

if __name__ == '__main__':
    migrate()
