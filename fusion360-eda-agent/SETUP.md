# Quick Setup Guide

## Prerequisites

- Node.js 18+ and npm
- Firebase account
- Google Gemini API key

## Step-by-Step Setup

### 1. Install Dependencies

```bash
cd fusion360-eda-agent
npm install
```

### 2. Firebase Setup

1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Create a new project (or use existing)
3. Enable **Firestore Database**:
   - Go to Firestore Database
   - Click "Create database"
   - Start in test mode (we'll add security rules)
4. Enable **Authentication**:
   - Go to Authentication
   - Click "Get started"
   - Enable "Anonymous" sign-in method
5. Get your Firebase config:
   - Go to Project Settings (gear icon)
   - Scroll to "Your apps"
   - Click "Web" icon (</>)
   - Copy the config values

### 3. Firestore Security Rules

Go to Firestore Database → Rules and paste:

```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    match /artifacts/{appId}/users/{userId}/ece_designs_fusion/{document=**} {
      allow read, write: if request.auth != null && request.auth.uid == userId;
    }
  }
}
```

### 4. Get Gemini API Key

1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Click "Create API Key"
3. Copy the key

### 5. Create .env File

Create a `.env` file in the root directory:

```env
VITE_FIREBASE_API_KEY=your_firebase_api_key_here
VITE_FIREBASE_AUTH_DOMAIN=your-project.firebaseapp.com
VITE_FIREBASE_PROJECT_ID=your-project-id
VITE_FIREBASE_STORAGE_BUCKET=your-project.appspot.com
VITE_FIREBASE_MESSAGING_SENDER_ID=123456789
VITE_FIREBASE_APP_ID=1:123456789:web:abcdef
VITE_GEMINI_API_KEY=your_gemini_api_key_here
VITE_GEMINI_MODEL=gemini-1.5-flash
VITE_APP_ID=fusion360-eda-agent
```

### 6. Run the Application

```bash
npm run dev
```

The app will open at `http://localhost:3000`

## Testing

1. Enter a circuit description like: "a 5V 555-timer astable circuit with 1kHz frequency"
2. Click "Generate Design"
3. Review the structured netlist
4. Copy the Fusion 360 script
5. Test in Fusion 360 (see README.md for instructions)

## Troubleshooting

### "GEMINI_API_KEY is not configured"
- Make sure your `.env` file exists in the root directory
- Restart the dev server after creating/editing `.env`
- Check that variable names start with `VITE_`

### Firebase authentication errors
- Verify all Firebase config values in `.env` are correct
- Check that Anonymous auth is enabled in Firebase Console
- Check browser console for detailed error messages

### Firestore permission errors
- Verify security rules are deployed
- Check that you're authenticated (should happen automatically)
- Verify the collection path matches: `artifacts/{appId}/users/{userId}/ece_designs_fusion`

### Gemini API errors
- Verify your API key is valid
- Check API quota/limits in Google AI Studio
- Try a different model name in `VITE_GEMINI_MODEL` (e.g., `gemini-1.5-pro`)

