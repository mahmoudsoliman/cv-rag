import os
import sqlite3
import shutil

def delete_sqlite_data(db_path="api/data/candidates.db"):
    """Delete all data from SQLite database tables."""
    print(f"Deleting SQLite data from {db_path}...")
    
    if not os.path.exists(db_path):
        print(f"SQLite database {db_path} not found.")
        return
    
    try:
        con = sqlite3.connect(db_path)
        con.execute("PRAGMA foreign_keys=ON;")
        
        # Delete all data from tables (order matters due to foreign keys)
        tables = [
            'links',
            'education', 
            'experience',
            'skills',
            'certifications',
            'candidates'
        ]
        
        for table in tables:
            result = con.execute(f"DELETE FROM {table}")
            rows_deleted = result.rowcount
            print(f"  Deleted {rows_deleted} rows from {table}")
        
        con.commit()
        con.close()
            
        print("SQLite data deletion completed.")
        
    except Exception as e:
        print(f"Error deleting SQLite data: {e}")

def delete_chroma_data(chroma_dir="api/data/chroma_resumes"):
    """Delete all data from Chroma vector store."""
    print(f"Deleting Chroma data from {chroma_dir}...")
    
    if not os.path.exists(chroma_dir):
        print(f"Chroma directory {chroma_dir} not found.")
        return
    
    try:
        shutil.rmtree(chroma_dir)
        print(f"  Removed entire Chroma directory: {chroma_dir}")
        print("Chroma data deletion completed.")
        
    except Exception as e:
        print(f"Error deleting Chroma data: {e}")

def main():
    """Main function to delete all database data."""
    print("=" * 50)
    print("DELETING ALL DATABASE DATA")
    print("=" * 50)
    print()
    
    # Change to the workspace directory
    workspace_dir = "/Users/mahmoudsoliman/workspace/cv-search-challenge"
    os.chdir(workspace_dir)
    
    
    print("\nStarting database data deletion...")
    print()
    
    # Delete SQLite data
    delete_sqlite_data()
    print()
    
    # Delete Chroma vector store
    delete_chroma_data()
    print()
    
    print("=" * 50)
    print("DATABASE DATA DELETION COMPLETED")
    print("=" * 50)
    print("\nThe following has been cleared:")
    print("- SQLite database (candidates, links, education, experience, skills, certifications)")
    print("- Chroma vector store")

if __name__ == "__main__":
    main()