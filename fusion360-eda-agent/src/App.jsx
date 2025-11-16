import React, { useState, useEffect } from 'react'
import { initializeAuth } from './config/firebase'
import { generateNetlist, generateFusionScript } from './services/geminiService'
import { saveDesign, subscribeToDesignHistory } from './services/firestoreService'
import DesignHistory from './components/DesignHistory'
import NetlistDisplay from './components/NetlistDisplay'
import ScriptDisplay from './components/ScriptDisplay'

function App() {
  const [user, setUser] = useState(null)
  const [userPrompt, setUserPrompt] = useState('')
  const [structuredNetlist, setStructuredNetlist] = useState(null)
  const [fusionScript, setFusionScript] = useState(null)
  const [designs, setDesigns] = useState([])
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState(null)
  const [currentStep, setCurrentStep] = useState(0) // 0: input, 1: netlist review, 2: script ready

  // Initialize Firebase auth
  useEffect(() => {
    const initAuth = async () => {
      try {
        const currentUser = await initializeAuth()
        setUser(currentUser)
      } catch (err) {
        console.error('Auth initialization error:', err)
        setError('Failed to initialize authentication. Please check your Firebase configuration.')
      }
    }
    initAuth()
  }, [])

  // Subscribe to design history
  useEffect(() => {
    if (!user) return

    const unsubscribe = subscribeToDesignHistory(user.uid, (designsList) => {
      setDesigns(designsList)
    })

    return () => unsubscribe()
  }, [user])

  const handleGenerate = async () => {
    if (!userPrompt.trim()) {
      setError('Please enter a circuit description')
      return
    }

    setIsLoading(true)
    setError(null)
    setStructuredNetlist(null)
    setFusionScript(null)
    setCurrentStep(1)

    try {
      // Step 1: Generate structured netlist
      const netlist = await generateNetlist(userPrompt)
      setStructuredNetlist(netlist)
      setCurrentStep(2)

      // Step 2: Generate Fusion 360 script
      const script = await generateFusionScript(userPrompt, netlist)
      setFusionScript(script)

      // Save to Firestore
      if (user) {
        await saveDesign(user.uid, {
          prompt: userPrompt,
          structuredNetlist: netlist,
          fusionScript: script,
        })
      }
    } catch (err) {
      console.error('Generation error:', err)
      setError(err.message || 'An error occurred while generating the design')
      setCurrentStep(0)
    } finally {
      setIsLoading(false)
    }
  }

  const handleLoadDesign = async (design) => {
    try {
      setUserPrompt(design.prompt)
      setStructuredNetlist(design.structuredNetlist)
      setFusionScript(design.fusionScript)
      setCurrentStep(2)
      setError(null)
      
      // Scroll to top
      window.scrollTo({ top: 0, behavior: 'smooth' })
    } catch (err) {
      console.error('Load design error:', err)
      setError('Failed to load design')
    }
  }

  const handleReset = () => {
    setUserPrompt('')
    setStructuredNetlist(null)
    setFusionScript(null)
    setCurrentStep(0)
    setError(null)
  }

  return (
    <div className="min-h-screen bg-gray-100 flex">
      {/* Design History Sidebar */}
      <div className="w-80 flex-shrink-0">
        <DesignHistory 
          designs={designs} 
          onLoadDesign={handleLoadDesign}
          isLoading={!user}
        />
      </div>

      {/* Main Content */}
      <div className="flex-1 flex flex-col">
        {/* Header */}
        <header className="bg-white border-b border-gray-200 px-6 py-4">
          <h1 className="text-2xl font-bold text-gray-900">Advanced AI EDA Agent</h1>
          <p className="text-sm text-gray-600 mt-1">Natural Language to Fusion 360 Circuit Design</p>
        </header>

        {/* Main Content Area */}
        <main className="flex-1 overflow-y-auto p-6">
          <div className="max-w-5xl mx-auto space-y-6">
            {/* Input Section */}
            <div className="bg-white rounded-lg border border-gray-200 p-6">
              <h2 className="text-xl font-semibold text-gray-800 mb-4">Circuit Description</h2>
              <textarea
                value={userPrompt}
                onChange={(e) => setUserPrompt(e.target.value)}
                placeholder="Describe your circuit design... (e.g., 'a 5V 555-timer astable circuit with 1kHz frequency')"
                className="w-full h-32 px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
                disabled={isLoading}
              />
              <div className="mt-4 flex gap-3">
                <button
                  onClick={handleGenerate}
                  disabled={isLoading || !userPrompt.trim()}
                  className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors font-medium"
                >
                  {isLoading ? (
                    <span className="flex items-center gap-2">
                      <svg className="animate-spin h-4 w-4" fill="none" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                      </svg>
                      Generating...
                    </span>
                  ) : (
                    'Generate Design'
                  )}
                </button>
                {(structuredNetlist || fusionScript) && (
                  <button
                    onClick={handleReset}
                    className="px-6 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors font-medium"
                  >
                    Reset
                  </button>
                )}
              </div>
            </div>

            {/* Error Display */}
            {error && (
              <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                <div className="flex items-center gap-2">
                  <svg className="w-5 h-5 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  <p className="text-red-800 font-medium">Error</p>
                </div>
                <p className="text-red-700 mt-1">{error}</p>
              </div>
            )}

            {/* Progress Indicator */}
            {isLoading && (
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                <div className="flex items-center gap-3">
                  <svg className="animate-spin h-5 w-5 text-blue-600" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                  </svg>
                  <div>
                    <p className="text-blue-800 font-medium">
                      {currentStep === 1 ? 'Step 1/2: Analyzing circuit and generating netlist...' : 'Step 2/2: Generating Fusion 360 script...'}
                    </p>
                  </div>
                </div>
              </div>
            )}

            {/* Structured Netlist Display */}
            {structuredNetlist && <NetlistDisplay structuredNetlist={structuredNetlist} />}

            {/* Fusion Script Display */}
            {fusionScript && <ScriptDisplay fusionScript={fusionScript} />}
          </div>
        </main>

        {/* Footer */}
        <footer className="bg-white border-t border-gray-200 px-6 py-4 text-center text-sm text-gray-600">
          <p>Powered by Google Gemini 2.5 Flash API • Built for Autodesk Fusion 360</p>
        </footer>
      </div>
    </div>
  )
}

export default App

