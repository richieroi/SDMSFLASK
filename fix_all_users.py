import hashlib
import pyodbc
from config import Config

def main():
    print("Checking and fixing user password hashes...")
    
    # Connect to the database
    conn = pyodbc.connect(Config.CONNECTION_STRING)
    cursor = conn.cursor()
    
    # Get the Student role ID
    cursor.execute("SELECT RoleID FROM Roles_198 WHERE RoleName = 'Student'")
    student_role_id = cursor.fetchone()[0]
    
    # The correct hash for "student123"
    correct_password = "student123"
    correct_hash = hashlib.sha256(correct_password.encode()).hexdigest()
    print(f"Expected hash for '{correct_password}': {correct_hash}")
    
    # Get all students from the Students_198 table
    cursor.execute("SELECT StudentID, FirstName, LastName, Email FROM Students_198")
    students = cursor.fetchall()
    
    student_count = len(students)
    users_fixed = 0
    users_created = 0
    users_ok = 0
    
    print(f"\nFound {student_count} students in Students_198 table.")
    
    for student in students:
        student_id, first_name, last_name, email = student
        # Check if there's a user account with this email
        cursor.execute("SELECT UserID, UserName, PasswordHash, Active FROM Users_198 WHERE Email = ?", email)
        user = cursor.fetchone()
        
        if user:
            user_id, username, current_hash, active = user
            print(f"\nUser found for {first_name} {last_name} ({email}):")
            print(f"  Username: {username}")
            print(f"  Current hash: {current_hash}")
            print(f"  Active: {active}")
            
            # Check if the hash is correct
            if current_hash != correct_hash:
                print("  Hash mismatch! Updating...")
                cursor.execute("UPDATE Users_198 SET PasswordHash = ? WHERE UserID = ?", 
                               correct_hash, user_id)
                conn.commit()
                print("  Password hash updated successfully.")
                users_fixed += 1
            else:
                print("  Password hash is correct.")
                users_ok += 1
            
            # Make sure user is active
            if not active:
                print("  User is inactive. Activating...")
                cursor.execute("UPDATE Users_198 SET Active = 1 WHERE UserID = ?", user_id)
                conn.commit()
                print("  User activated successfully.")
        else:
            # No user account found, create one
            print(f"\nNo user account found for {first_name} {last_name} ({email}). Creating...")
            
            # Create a username from first name and last name
            username = f"{first_name.lower()}.{last_name.lower()}"
            
            # Check if this username already exists
            cursor.execute("SELECT COUNT(*) FROM Users_198 WHERE UserName = ?", username)
            if cursor.fetchone()[0] > 0:
                # Username exists, add a number to make it unique
                i = 1
                while True:
                    new_username = f"{username}{i}"
                    cursor.execute("SELECT COUNT(*) FROM Users_198 WHERE UserName = ?", new_username)
                    if cursor.fetchone()[0] == 0:
                        username = new_username
                        break
                    i += 1
            
            # Create the user
            cursor.execute("""
                INSERT INTO Users_198 (UserName, PasswordHash, Email, RoleID, Active)
                VALUES (?, ?, ?, ?, 1)
            """, username, correct_hash, email, student_role_id)
            conn.commit()
            print(f"  User created with username: {username}")
            users_created += 1
    
    print("\n--- Summary ---")
    print(f"Total students: {student_count}")
    print(f"Users with correct hash: {users_ok}")
    print(f"Users with hash fixed: {users_fixed}")
    print(f"New users created: {users_created}")
    print("All students can now log in with password: student123")
    
    cursor.close()
    conn.close()
    print("\nProcess completed successfully!")

if __name__ == "__main__":
    main()
