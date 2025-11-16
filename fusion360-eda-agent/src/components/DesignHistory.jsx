import React from 'react'

const DesignHistory = ({ designs, onLoadDesign, isLoading }) => {
  const formatDate = (timestamp) => {
    if (!timestamp) return 'Unknown date'
    const date = timestamp.toDate ? timestamp.toDate() : new Date(timestamp)
    return date.toLocaleString()
  }

  const truncatePrompt = (prompt, maxLength = 60) => {
    if (!prompt) return 'No prompt'
    return prompt.length > maxLength ? prompt.substring(0, maxLength) + '...' : prompt
  }

  return (
    <div className="h-full flex flex-col bg-gray-50 border-r border-gray-200">
      <div className="p-4 border-b border-gray-200 bg-white">
        <h2 className="text-lg font-semibold text-gray-800">Design History</h2>
        <p className="text-sm text-gray-500 mt-1">
          {designs.length} {designs.length === 1 ? 'design' : 'designs'}
        </p>
      </div>

      <div className="flex-1 overflow-y-auto">
        {isLoading ? (
          <div className="p-4 text-center text-gray-500">Loading...</div>
        ) : designs.length === 0 ? (
          <div className="p-4 text-center text-gray-500 text-sm">
            No designs yet. Create your first design to see it here.
          </div>
        ) : (
          <div className="p-2">
            {designs.map((design) => (
              <button
                key={design.id}
                onClick={() => onLoadDesign(design)}
                className="w-full text-left p-3 mb-2 rounded-lg border border-gray-200 bg-white hover:bg-blue-50 hover:border-blue-300 transition-colors"
              >
                <div className="text-sm font-medium text-gray-800 mb-1">
                  {truncatePrompt(design.prompt)}
                </div>
                <div className="text-xs text-gray-500">
                  {formatDate(design.createdAt)}
                </div>
              </button>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}

export default DesignHistory

