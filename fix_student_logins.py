import hashlib
import pyodbc
from config import Config

def main():
    print("Fixing student login accounts...")
    
    # Connect to the database
    conn = pyodbc.connect(Config.CONNECTION_STRING)
    cursor = conn.cursor()
    
    # Get the Student role ID
    cursor.execute("SELECT RoleID FROM Roles_198 WHERE RoleName = 'Student'")
    student_role_id = cursor.fetchone()[0]
    
    # The correct hash for "student123"
    correct_password = "student123"
    correct_hash = hashlib.sha256(correct_password.encode()).hexdigest()
    print(f"All students will be able to log in with password: {correct_password}")
    
    # Get all students from the Students_198 table
    cursor.execute("SELECT StudentID, FirstName, LastName, Email FROM Students_198")
    students = cursor.fetchall()
    
    print(f"\nWorking on {len(students)} student accounts:")
    
    for student in students:
        student_id, first_name, last_name, email = student
        full_name = f"{first_name} {last_name}"
        
        print(f"\nProcessing: {full_name} ({email})")
        
        # Check if there's a user account with this email
        cursor.execute("SELECT UserID, UserName, PasswordHash, Active FROM Users_198 WHERE Email = ?", email)
        user = cursor.fetchone()
        
        if user:
            user_id, username, current_hash, active = user
            print(f"  Found user account: {username}")
            
            # Fix hash and make active
            cursor.execute("""
                UPDATE Users_198 
                SET PasswordHash = ?, Active = 1
                WHERE UserID = ?
            """, correct_hash, user_id)
            
            print(f"  Updated password and set account to active")
            
        else:
            # Create username from firstname.lastname
            username = f"{first_name.lower()}.{last_name.lower()}"
            
            # Check if this username already exists
            cursor.execute("SELECT COUNT(*) FROM Users_198 WHERE UserName = ?", username)
            if cursor.fetchone()[0] > 0:
                # Add a number to make it unique
                i = 1
                while True:
                    new_username = f"{username}{i}"
                    cursor.execute("SELECT COUNT(*) FROM Users_198 WHERE UserName = ?", new_username)
                    if cursor.fetchone()[0] == 0:
                        username = new_username
                        break
                    i += 1
            
            # Create the user account
            cursor.execute("""
                INSERT INTO Users_198 (UserName, PasswordHash, Email, RoleID, Active)
                VALUES (?, ?, ?, ?, 1)
            """, username, correct_hash, email, student_role_id)
            
            print(f"  Created new user account: {username}")
    
    # Commit all changes
    conn.commit()
    
    # Print login instructions
    print("\n----------------------------------")
    print("STUDENT LOGIN INFORMATION")
    print("----------------------------------")
    print("All students can now log in with:")
    print("- Username: firstname.lastname")
    print("- Password: student123")
    print("\nHere's the full list of accounts:")
    
    # Show all student accounts
    cursor.execute("""
        SELECT s.FirstName, s.LastName, u.UserName, s.Email
        FROM Students_198 s
        JOIN Users_198 u ON s.Email = u.Email
        ORDER BY s.LastName
    """)
    
    for row in cursor.fetchall():
        first_name, last_name, username, email = row
        print(f"- {first_name} {last_name}: username = {username}, password = student123")
    
    cursor.close()
    conn.close()
    print("\nStudent accounts fixed successfully!")

if __name__ == "__main__":
    main()
