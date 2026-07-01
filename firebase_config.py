#!/usr/bin/env python3
"""
Firebase Configuration Setup
Instructions for setting up Firebase for portfolio persistence.
"""

FIREBASE_CONFIG_TEMPLATE = """
{
  "apiKey": "your-api-key",
  "authDomain": "your-project.firebaseapp.com",
  "databaseURL": "https://your-project-default-rtdb.firebaseio.com",
  "projectId": "your-project-id",
  "storageBucket": "your-project.appspot.com",
  "messagingSenderId": "123456789",
  "appId": "your-app-id"
}
"""

SETUP_INSTRUCTIONS = """
# Firebase Setup Instructions

## 1. Create Firebase Project
1. Go to https://console.firebase.google.com
2. Click "Add project"
3. Follow the setup wizard

## 2. Enable Firestore Database
1. In Firebase console, go to "Firestore Database"
2. Click "Create database"
3. Choose "Start in test mode" (for development)
4. Select a location

## 3. Get Configuration
1. Go to Project Settings > General
2. Under "Your apps", click the web app icon
3. Copy the firebaseConfig object

## 4. Set up Streamlit Secrets
Add this to your Streamlit Community Cloud secrets:

```toml
[secrets]
FIREBASE_CONFIG = '{"apiKey": "...", "authDomain": "...", "databaseURL": "..."}'
```

## 5. Install Required Packages
Add to requirements.txt:
- firebase-admin
- google-cloud-firestore

## 6. Update Firebase Integration
Replace the mock implementation with real Firebase calls.
"""

def print_setup_instructions():
    print(SETUP_INSTRUCTIONS)
    
if __name__ == "__main__":
    print_setup_instructions()
