import { GEMINI_API_KEY, NETLIST_SCHEMA, FUSION_SCRIPT_SYSTEM_PROMPT } from '../config/constants'

// Gemini API endpoint - update model name as needed (e.g., gemini-1.5-flash, gemini-2.0-flash-exp)
const GEMINI_MODEL = import.meta.env.VITE_GEMINI_MODEL || 'gemini-1.5-flash'
const GEMINI_API_URL = `https://generativelanguage.googleapis.com/v1beta/models/${GEMINI_MODEL}:generateContent`

/**
 * Step 1: Audit Check - Generate structured netlist from natural language
 */
export const generateNetlist = async (userPrompt) => {
  if (!GEMINI_API_KEY) {
    throw new Error('GEMINI_API_KEY is not configured. Please set VITE_GEMINI_API_KEY in your .env file.')
  }

  const prompt = `You are an expert electrical engineer. Analyze the following circuit description and generate a complete, accurate netlist and bill of materials.

Circuit Description: "${userPrompt}"

Generate a structured JSON response with:
1. A complete Bill of Materials (BOM) listing all components with their values, packages, and identifiers
2. A detailed pin-by-pin netlist showing all connections
3. Design for Manufacturability (DFM) notes and warnings

Be thorough and accurate. Include all necessary components, power supplies, and connections.`

  const response = await fetch(`${GEMINI_API_URL}?key=${GEMINI_API_KEY}`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      contents: [
        {
          parts: [{ text: prompt }],
        },
      ],
      generationConfig: {
        responseSchema: NETLIST_SCHEMA,
        responseMimeType: 'application/json',
        temperature: 0.3,
      },
    }),
  })

  if (!response.ok) {
    const errorData = await response.text()
    throw new Error(`Gemini API error: ${response.status} - ${errorData}`)
  }

  const data = await response.json()
  
  if (!data.candidates || !data.candidates[0] || !data.candidates[0].content) {
    throw new Error('Invalid response from Gemini API')
  }

  const textContent = data.candidates[0].content.parts[0].text
  
  // Parse JSON response (Gemini returns JSON as text when responseMimeType is application/json)
  try {
    return JSON.parse(textContent)
  } catch (parseError) {
    // If parsing fails, try to extract JSON from markdown code blocks
    const jsonMatch = textContent.match(/```(?:json)?\s*([\s\S]*?)\s*```/) || textContent.match(/\{[\s\S]*\}/)
    if (jsonMatch) {
      return JSON.parse(jsonMatch[1] || jsonMatch[0])
    }
    throw new Error('Failed to parse JSON response from Gemini API')
  }
}

/**
 * Step 2: Script Generation - Generate Fusion 360 Python script from structured netlist
 */
export const generateFusionScript = async (userPrompt, structuredNetlist) => {
  if (!GEMINI_API_KEY) {
    throw new Error('GEMINI_API_KEY is not configured. Please set VITE_GEMINI_API_KEY in your .env file.')
  }

  const contextPrompt = `Original User Request: "${userPrompt}"

Structured Netlist Data:
${JSON.stringify(structuredNetlist, null, 2)}

${FUSION_SCRIPT_SYSTEM_PROMPT}

Generate a complete Fusion 360 Python script that:
1. Creates all components from the BOM
2. Creates all nets from the netlist
3. Connects all pins according to the netlist connections
4. Is ready to run in Fusion 360's script editor

Return ONLY the Python code, no markdown, no explanations.`

  const response = await fetch(`${GEMINI_API_URL}?key=${GEMINI_API_KEY}`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      contents: [
        {
          parts: [{ text: contextPrompt }],
        },
      ],
      generationConfig: {
        temperature: 0.2,
      },
    }),
  })

  if (!response.ok) {
    const errorData = await response.text()
    throw new Error(`Gemini API error: ${response.status} - ${errorData}`)
  }

  const data = await response.json()
  
  if (!data.candidates || !data.candidates[0] || !data.candidates[0].content) {
    throw new Error('Invalid response from Gemini API')
  }

  return data.candidates[0].content.parts[0].text.trim()
}

