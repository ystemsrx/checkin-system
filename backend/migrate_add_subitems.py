"""
Database migration script to add sub_items column to activities table
and sub_item column to registrations table.

Run this script to update the database schema.
"""

from app import create_app
from models import db
from sqlalchemy import text

def migrate():
    app = create_app()
    with app.app_context():
        try:
            # Add sub_items column to activities table
            with db.engine.connect() as conn:
                # Check if column exists
                result = conn.execute(text(
                    "SELECT COUNT(*) FROM pragma_table_info('activities') WHERE name='sub_items'"
                ))
                if result.scalar() == 0:
                    conn.execute(text("ALTER TABLE activities ADD COLUMN sub_items TEXT"))
                    conn.commit()
                    print("✓ Added sub_items column to activities table")
                else:
                    print("✓ sub_items column already exists in activities table")
                
                # Check if sub_item column exists in registrations
                result = conn.execute(text(
                    "SELECT COUNT(*) FROM pragma_table_info('registrations') WHERE name='sub_item'"
                ))
                if result.scalar() == 0:
                    conn.execute(text("ALTER TABLE registrations ADD COLUMN sub_item VARCHAR(100)"))
                    conn.commit()
                    print("✓ Added sub_item column to registrations table")
                else:
                    print("✓ sub_item column already exists in registrations table")
            
            print("\n✓ Migration completed successfully!")
            
        except Exception as e:
            print(f"\n✗ Migration failed: {str(e)}")
            raise

if __name__ == '__main__':
    print("Starting database migration...")
    print("=" * 50)
    migrate()
