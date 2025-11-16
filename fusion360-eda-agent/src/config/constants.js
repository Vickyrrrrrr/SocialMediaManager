// JSON Schema for Netlist Structure (Step 1: Audit Check)
export const NETLIST_SCHEMA = {
  type: 'object',
  properties: {
    bom: {
      type: 'object',
      description: 'Bill of Materials - all components needed for the circuit',
      properties: {
        components: {
          type: 'array',
          items: {
            type: 'object',
            properties: {
              name: { type: 'string', description: 'Component name (e.g., "R1", "C1", "U1")' },
              type: { type: 'string', description: 'Component type (e.g., "Resistor", "Capacitor", "IC")' },
              value: { type: 'string', description: 'Component value (e.g., "10k", "100uF", "555")' },
              package: { type: 'string', description: 'Package type (e.g., "0805", "DIP-8", "TO-92")' },
              manufacturer: { type: 'string', description: 'Manufacturer part number or generic identifier' },
            },
            required: ['name', 'type', 'value'],
          },
        },
      },
      required: ['components'],
    },
    netlist: {
      type: 'object',
      description: 'Pin-by-pin netlist connections',
      properties: {
        nets: {
          type: 'array',
          items: {
            type: 'object',
            properties: {
              net_name: { type: 'string', description: 'Net name (e.g., "VCC", "GND", "OUTPUT")' },
              connections: {
                type: 'array',
                items: {
                  type: 'object',
                  properties: {
                    component: { type: 'string', description: 'Component name (e.g., "R1")' },
                    pin: { type: 'string', description: 'Pin name or number (e.g., "1", "VCC", "OUT")' },
                  },
                  required: ['component', 'pin'],
                },
              },
            },
            required: ['net_name', 'connections'],
          },
        },
      },
      required: ['nets'],
    },
    dfm_notes: {
      type: 'array',
      items: { type: 'string' },
      description: 'Design for Manufacturability notes and warnings',
    },
  },
  required: ['bom', 'netlist', 'dfm_notes'],
}

// System Prompt for Fusion 360 Script Generation (Step 2)
export const FUSION_SCRIPT_SYSTEM_PROMPT = `You are an expert in the Autodesk Fusion 360 Electronics Design Python API. Your task is to generate complete, runnable Python scripts that programmatically create schematics in Fusion 360.

CRITICAL REQUIREMENTS:
1. Import the necessary Fusion 360 API modules at the top
2. Use the correct API calls to add components, create nets, and connect pins
3. The script must be complete and executable when pasted into Fusion 360's script editor
4. Use proper error handling and API patterns

FUSION 360 API PATTERNS:
- Access the active design: adsk.core.Application.get().activeProduct
- Get the root component: design.rootComponent
- Add components: rootComponent.occurrences.addNewComponent()
- Create nets: design.netList.createNet(netName)
- Connect pins: net.connectPin(componentPin)

Generate ONLY the Python script code, no explanations or markdown formatting. The script should be ready to copy-paste and run.`

export const APP_ID = import.meta.env.VITE_APP_ID || 'fusion360-eda-agent'
export const GEMINI_API_KEY = import.meta.env.VITE_GEMINI_API_KEY

