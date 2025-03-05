import hashlib
import pyodbc
from config import Config

# Connect to the database
conn = pyodbc.connect(Config.CONNECTION_STRING)
cursor = conn.cursor()

# Check if alex.johnson exists and is active
print("Checking if user exists...")
cursor.execute("""
    SELECT u.UserID, u.UserName, u.PasswordHash, u.Email, u.Active, r.RoleName
    FROM Users_198 u
    JOIN Roles_198 r ON u.RoleID = r.RoleID
    WHERE u.UserName = 'alex.johnson'
""")

row = cursor.fetchone()
if not row:
    print("User alex.johnson doesn't exist in the database!")
    # Get the Student role ID
    cursor.execute("SELECT RoleID FROM Roles_198 WHERE RoleName = 'Student'")
    role_id = cursor.fetchone()[0]
    
    # Create the user with the correct hash
    password = "student123"
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    print(f"Creating user with hash: {hashed_password}")
    
    cursor.execute("""
        INSERT INTO Users_198 (UserName, PasswordHash, Email, RoleID, Active)
        VALUES ('alex.johnson', ?, 'alex.johnson@umat.edu.gh', ?, 1)
    """, hashed_password, role_id)
    conn.commit()
    print("User created successfully!")
else:
    user_id, username, password_hash, email, active, role = row
    print(f"User found: {username}")
    print(f"Email: {email}")
    print(f"Role: {role}")
    print(f"Active: {active}")
    print(f"Current hash: {password_hash}")
    
    # Test our hash function
    test_password = "student123"
    calculated_hash = hashlib.sha256(test_password.encode()).hexdigest()
    print(f"Calculated hash for 'student123': {calculated_hash}")
    
    if password_hash != calculated_hash:
        print("Hash mismatch! Updating the hash...")
        
        # Update the hash
        cursor.execute("""
            UPDATE Users_198
            SET PasswordHash = ?
            WHERE UserID = ?
        """, calculated_hash, user_id)
        conn.commit()
        print("Hash updated successfully!")
    
    # Make sure the user is active
    if active == 0:
        print("User is inactive! Activating...")
        cursor.execute("UPDATE Users_198 SET Active = 1 WHERE UserID = ?", user_id)
        conn.commit()
        print("User activated successfully!")

cursor.close()
conn.close()
print("Debug complete!")
