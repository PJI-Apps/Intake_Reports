#!/usr/bin/env python3
"""
🔐 Password Generator for PJI Law Reports
Generate secure hashed passwords for Streamlit authentication
"""

import bcrypt
import getpass

def hash_password(password):
    """Hash a password using bcrypt"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def main():
    print("🔐 PJI Law Reports - Password Generator")
    print("=" * 50)
    print()
    
    print("This script will help you generate secure hashed passwords")
    print("for your Streamlit authentication configuration.")
    print()
    
    while True:
        print("Enter the password you want to hash (or 'quit' to exit):")
        password = getpass.getpass("Password: ")
        
        if password.lower() == 'quit':
            break
            
        if not password:
            print("❌ Password cannot be empty!")
            continue
            
        # Hash the password
        hashed = hash_password(password)
        
        print()
        print("✅ Password hashed successfully!")
        print("=" * 50)
        print("Use this in your TOML secrets file:")
        print(f"password: {hashed}")
        print("=" * 50)
        print()
        
        # Ask if they want to generate another
        another = input("Generate another password? (y/n): ").lower()
        if another != 'y':
            break
    
    print()
    print("📋 TOML Configuration Example:")
    print("=" * 50)
    print("""
[auth_config]
config = \"\"\"
credentials:
  usernames:
    admin:
      email: admin@pji-law.com
      name: PJI Law Admin
      password: $2b$12$hashed_password_from_above
cookie:
  name: pji_law_auth
  key: your_super_secret_cookie_key_here
  expiry_days: 30
\"\"\"
""")
    print("=" * 50)
    print("✅ Done! Copy the hashed password to your TOML file.")

if __name__ == "__main__":
    main()
