# Firebase Setup Guide for Portfolio Cloud Storage

## Overview
This guide will help you set up Firebase Firestore for persistent cloud storage of your portfolio data.

## Prerequisites
- Google account
- Firebase project (free tier available)
- Streamlit Community Cloud deployment

## Step 1: Create Firebase Project

1. Go to [Firebase Console](https://console.firebase.google.com)
2. Click "Add project"
3. Enter project name (e.g., "stock-portfolio-app")
4. Enable Google Analytics (optional)
5. Click "Create project"

## Step 2: Set Up Firestore Database

1. In Firebase console, go to "Firestore Database" in the left menu
2. Click "Create database"
3. Choose "Start in test mode" (for development)
4. Select a location (choose closest to your users)
5. Click "Create database"

## Step 3: Get Service Account Key

1. Go to Project Settings (⚙️ icon) > Service accounts
2. Click "Generate new private key"
3. Select JSON format
4. Click "Create"
5. Download the JSON file (keep it secure!)

## Step 4: Configure Streamlit Secrets

### Option A: Streamlit Community Cloud
1. Go to your app's dashboard on Streamlit Cloud
2. Click "Settings" > "Secrets"
3. Add this secret:

```toml
FIREBASE_SERVICE_ACCOUNT = '''
{
  "type": "service_account",
  "project_id": "your-project-id",
  "private_key_id": "...",
  "private_key": "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n",
  "client_email": "firebase-adminsdk-...@your-project.iam.gserviceaccount.com",
  "client_id": "...",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-...%40your-project.iam.gserviceaccount.com"
}
'''
```

### Option B: Local Development
Create a `.streamlit/secrets.toml` file:

```toml
FIREBASE_SERVICE_ACCOUNT = '''
{
  "type": "service_account",
  "project_id": "your-project-id",
  "private_key_id": "...",
  "private_key": "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n",
  "client_email": "firebase-adminsdk-...@your-project.iam.gserviceaccount.com",
  "client_id": "...",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-...%40your-project.iam.gserviceaccount.com"
}
'''
```

## Step 5: Update Requirements

Add to your `requirements.txt`:

```txt
firebase-admin>=6.0.0
```

## Step 6: Security Rules (Optional)

For production, update Firestore security rules:

1. Go to Firestore Database > Rules
2. Replace default rules with:

```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    // Users can only access their own data
    match /portfolios/{userId} {
      allow read, write: if request.auth != null && request.auth.uid == userId;
    }
    match /watchlists/{userId} {
      allow read, write: if request.auth != null && request.auth.uid == userId;
    }
    match /recommendations/{userId}_{source} {
      allow read, write: if request.auth != null && request.auth.uid == userId;
    }
    match /backups/{userId} {
      allow read, write: if request.auth != null && request.auth.uid == userId;
    }
  }
}
```

## Step 7: Test the Integration

1. Deploy your app to Streamlit Cloud
2. Go to the Portfolio page
3. Check the sync status - it should show "Firebase" instead of "Mock"
4. Add some stocks to your portfolio
5. Check the "Cloud Backup" tab for sync status

## Features Available

✅ **Real-time cloud sync** - Portfolio data syncs to Firebase
✅ **Cross-device access** - Same portfolio on multiple devices  
✅ **Data persistence** - Survives app restarts and deployments
✅ **Import/Export** - Backup and restore portfolio data
✅ **User isolation** - Each user gets separate data
✅ **Automatic fallback** - Works even if Firebase is down

## Troubleshooting

### Firebase Not Connecting
- Check service account key format
- Verify Firestore database is created
- Ensure secrets are properly formatted

### Permission Errors
- Make sure service account has "Firestore Admin" role
- Check security rules if implemented

### Data Not Syncing
- Check network connection
- Verify Firebase project is active
- Look at app logs for error messages

## Cost

Firebase Firestore free tier includes:
- 1 GiB storage
- 50,000 document reads/day
- 20,000 document writes/day
- 20,000 document deletes/day

This should be sufficient for most portfolio applications.

## Next Steps

1. **Production Setup**: Implement proper authentication
2. **Security**: Add user authentication with Firebase Auth
3. **Monitoring**: Set up Firebase usage monitoring
4. **Backup**: Regular data exports for additional safety

## Support

If you encounter issues:
1. Check Firebase console for error messages
2. Review Streamlit app logs
3. Verify service account permissions
4. Test with a simple Firebase connection first
