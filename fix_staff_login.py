import hashlib
import pyodbc
from config import Config

def main():
    print("Fixing staff login password hash...")
    
    # Connect to the database
    conn = pyodbc.connect(Config.CONNECTION_STRING)
    cursor = conn.cursor()
    
    # The correct hash should be generated using our app's hash function
    staff_password = "staff123"
    correct_hash = hashlib.sha256(staff_password.encode()).hexdigest()
    print(f"Generated hash for 'staff123': {correct_hash}")
    
    # Check the existing hash in the database
    cursor.execute("""
        SELECT UserID, UserName, PasswordHash, Email, Active
        FROM Users_198 
        WHERE UserName = 'staff'
    """)
    
    row = cursor.fetchone()
    if not row:
        print("Staff account not found in the database! Creating it...")
        
        # Get Staff role ID
        cursor.execute("SELECT RoleID FROM Roles_198 WHERE RoleName = 'Staff'")
        role_id = cursor.fetchone()[0]
        
        # Create staff user with correct hash
        cursor.execute("""
            INSERT INTO Users_198 (UserName, PasswordHash, Email, RoleID, Active)
            VALUES ('staff', ?, 'staff@school.edu', ?, 1)
        """, correct_hash, role_id)
        
        conn.commit()
        print("Staff account created successfully with correct hash!")
    else:
        user_id, username, existing_hash, email, active = row
        print(f"Found staff account: {username}")
        print(f"Current hash in DB: {existing_hash}")
        
        if existing_hash != correct_hash:
            print("Hash mismatch detected! Updating to correct hash...")
            
            # Update the hash
            cursor.execute("""
                UPDATE Users_198
                SET PasswordHash = ?
                WHERE UserID = ?
            """, correct_hash, user_id)
            
            conn.commit()
            print("Staff password hash updated successfully!")
        else:
            print("Hash is already correct.")
        
        # Make sure account is active
        if not active:
            print("Staff account is inactive. Activating...")
            cursor.execute("UPDATE Users_198 SET Active = 1 WHERE UserID = ?", user_id)
            conn.commit()
            print("Staff account activated.")
    
    print("\n--- Staff Login Credentials ---")
    print("Username: staff")
    print("Password: staff123")
    
    cursor.close()
    conn.close()
    print("Process completed successfully!")

if __name__ == "__main__":
    main()
