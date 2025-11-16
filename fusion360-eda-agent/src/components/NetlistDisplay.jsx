import React from 'react'

const NetlistDisplay = ({ structuredNetlist }) => {
  if (!structuredNetlist) return null

  return (
    <div className="space-y-6">
      {/* BOM Section */}
      <div className="bg-white rounded-lg border border-gray-200 p-4">
        <h3 className="text-lg font-semibold text-gray-800 mb-3">Bill of Materials (BOM)</h3>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Name</th>
                <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Type</th>
                <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Value</th>
                <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Package</th>
                <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Manufacturer</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {structuredNetlist.bom?.components?.map((component, idx) => (
                <tr key={idx} className="hover:bg-gray-50">
                  <td className="px-4 py-2 text-sm font-medium text-gray-900">{component.name}</td>
                  <td className="px-4 py-2 text-sm text-gray-700">{component.type}</td>
                  <td className="px-4 py-2 text-sm text-gray-700">{component.value}</td>
                  <td className="px-4 py-2 text-sm text-gray-700">{component.package || 'N/A'}</td>
                  <td className="px-4 py-2 text-sm text-gray-700">{component.manufacturer || 'N/A'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Netlist Section */}
      <div className="bg-white rounded-lg border border-gray-200 p-4">
        <h3 className="text-lg font-semibold text-gray-800 mb-3">Netlist</h3>
        <div className="space-y-3">
          {structuredNetlist.netlist?.nets?.map((net, idx) => (
            <div key={idx} className="border-l-4 border-blue-500 pl-3 py-2 bg-gray-50 rounded">
              <div className="font-medium text-gray-800 mb-1">{net.net_name}</div>
              <div className="text-sm text-gray-600 space-y-1">
                {net.connections?.map((conn, connIdx) => (
                  <div key={connIdx}>
                    <span className="font-medium">{conn.component}</span>
                    <span className="text-gray-400 mx-2">→</span>
                    <span>{conn.pin}</span>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* DFM Notes Section */}
      {structuredNetlist.dfm_notes && structuredNetlist.dfm_notes.length > 0 && (
        <div className="bg-yellow-50 rounded-lg border border-yellow-200 p-4">
          <h3 className="text-lg font-semibold text-yellow-800 mb-3">Design for Manufacturability Notes</h3>
          <ul className="list-disc list-inside space-y-1">
            {structuredNetlist.dfm_notes.map((note, idx) => (
              <li key={idx} className="text-sm text-yellow-700">{note}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  )
}

export default NetlistDisplay

