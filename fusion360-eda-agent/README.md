# Advanced AI EDA Agent for Fusion 360

A professional-grade, web-based engineering tool that translates natural language circuit descriptions directly into runnable Fusion 360 Python scripts.

## Features

- **Multi-Step AI Agent Workflow**: Two-step generative pipeline with structured planning and script generation
- **Persistent Design History**: Automatic saving to Firebase Firestore with real-time updates
- **Audit Trail**: Review structured netlists before script generation
- **Complete BOM & Netlist**: Automatic component selection and pin-by-pin netlisting
- **DFM Notes**: Design for Manufacturability warnings and recommendations

## Technology Stack

- **Frontend**: React 18 with functional components and hooks
- **Styling**: Tailwind CSS (via CDN)
- **AI Engine**: Google Gemini API (configurable model)
- **Database**: Google Firebase Firestore
- **Authentication**: Firebase Anonymous Auth

## Setup Instructions

### 1. Install Dependencies

```bash
npm install
```

### 2. Configure Environment Variables

Create a `.env` file in the root directory:

```env
VITE_FIREBASE_API_KEY=your_firebase_api_key
VITE_FIREBASE_AUTH_DOMAIN=your_project.firebaseapp.com
VITE_FIREBASE_PROJECT_ID=your_project_id
VITE_FIREBASE_STORAGE_BUCKET=your_project.appspot.com
VITE_FIREBASE_MESSAGING_SENDER_ID=your_sender_id
VITE_FIREBASE_APP_ID=your_app_id
VITE_GEMINI_API_KEY=your_gemini_api_key
VITE_APP_ID=fusion360-eda-agent
```

### 3. Firebase Setup

1. Create a Firebase project at [Firebase Console](https://console.firebase.google.com/)
2. Enable **Firestore Database** and **Authentication**
3. In Authentication, enable **Anonymous** sign-in method
4. In Firestore, set up security rules (see below)
5. Copy your Firebase config values to `.env`

#### Firestore Security Rules

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
2. Create a new API key
3. Add it to your `.env` file

### 5. Run the Application

```bash
npm run dev
```

The application will open at `http://localhost:3000`

## Usage

### Creating a New Design

1. Enter a natural language description of your circuit (e.g., "a 5V 555-timer astable circuit with 1kHz frequency")
2. Click "Generate Design"
3. Review the structured netlist (BOM, connections, DFM notes)
4. Copy the generated Fusion 360 Python script

### Using the Script in Fusion 360

1. Click the "Copy Script" button in the app
2. Open Autodesk Fusion 360
3. Open an Electronics Design workspace
4. Go to **Utilities** → **Scripts and Add-Ins**
5. Click **Create** to create a new script
6. Paste the copied code
7. Click **Run**

The script will automatically build the schematic with all components, nets, and connections.

### Loading Previous Designs

- All designs are automatically saved to your private Firestore collection
- Click any design in the **Design History** panel to reload it
- Designs are sorted by date (newest first)

## Project Structure

```
fusion360-eda-agent/
├── src/
│   ├── components/
│   │   ├── DesignHistory.jsx    # Left sidebar with design history
│   │   ├── NetlistDisplay.jsx   # BOM and netlist visualization
│   │   └── ScriptDisplay.jsx    # Fusion 360 script display with copy
│   ├── config/
│   │   ├── constants.js         # JSON schemas and prompts
│   │   └── firebase.js          # Firebase initialization
│   ├── services/
│   │   ├── geminiService.js     # Gemini API integration
│   │   └── firestoreService.js  # Firestore operations
│   ├── App.jsx                  # Main application component
│   ├── main.jsx                 # React entry point
│   └── index.css                # Global styles
├── index.html
├── package.json
├── vite.config.js
└── README.md
```

## How It Works

### Step 1: Audit Check (Structured Planning)

The user's prompt is sent to Gemini API with a strict JSON Schema (`NETLIST_SCHEMA`). The AI returns:
- Complete Bill of Materials (BOM)
- Pin-by-pin netlist
- Design for Manufacturability (DFM) notes

This structured data is displayed for user review before script generation.

### Step 2: Script Generation

The validated JSON is sent back to Gemini API with a specialized system prompt (`FUSION_SCRIPT_SYSTEM_PROMPT`). The AI generates a complete Python script that:
- Adds all components from the BOM
- Creates all nets from the netlist
- Connects all pins according to the netlist

### Data Persistence

Every successfully generated design is automatically saved to:
```
artifacts/{appId}/users/{userId}/ece_designs_fusion/{designId}
```

The Design History panel uses Firestore's `onSnapshot` for real-time updates.

## Building for Production

```bash
npm run build
```

The production build will be in the `dist/` directory.

## License

MIT

## Support

For issues or questions, please open an issue on the repository.

