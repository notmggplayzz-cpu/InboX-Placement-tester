import React, { useState, useEffect } from 'react'
import { RefreshCw, Download } from 'lucide-react'
import { testsAPI } from '../services/api'

export default function TestResults({ tests }) {
  const [selectedTest, setSelectedTest] = useState(null)
  const [results, setResults] = useState([])
  const [statistics, setStatistics] = useState(null)
  const [loading, setLoading] = useState(false)

  const loadTestResults = async (testId) => {
    try {
      setLoading(true)
      const [resultsRes, statsRes] = await Promise.all([
        testsAPI.getResults(testId),
        testsAPI.getStatistics(testId).catch(() => null),
      ])
      setResults(resultsRes.data || [])
      setStatistics(statsRes?.data || null)
    } catch (error) {
      console.error('Failed to load results:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleTestSelect = async (test) => {
    setSelectedTest(test)
    await loadTestResults(test.id)
  }

  const handleScanAgain = async () => {
    if (!selectedTest) return
    try {
      setLoading(true)
      await testsAPI.scanTest(selectedTest.id)
      await loadTestResults(selectedTest.id)
    } catch (error) {
      console.error('Failed to rescan:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleExport = (format) => {
    if (!results.length) return
    const data = results.map(r => ({
      email: r.email,
      folder: r.folder,
      delivered: r.folder !== 'NOT_FOUND' ? 'Yes' : 'No',
      delivery_time: r.delivery_time_seconds ? `${r.delivery_time_seconds}s` : 'N/A',
      received_time: r.received_time ? new Date(r.received_time).toLocaleString() : 'N/A',
    }))

    if (format === 'csv') {
      const csv = [
        Object.keys(data[0]).join(','),
        ...data.map(row => Object.values(row).map(v => `"${v}"`).join(','))
      ].join('\n')
      downloadFile(csv, `results-${selectedTest.id}.csv`, 'text/csv')
    } else if (format === 'json') {
      downloadFile(JSON.stringify(data, null, 2), `results-${selectedTest.id}.json`, 'application/json')
    }
  }

  const downloadFile = (content, filename, type) => {
    const blob = new Blob([content], { type })
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = filename
    a.click()
    window.URL.revokeObjectURL(url)
  }

  const getFolderBadgeColor = (folder) => {
    switch (folder) {
      case 'INBOX': return 'badge-success'
      case 'PROMOTIONS': return 'badge-warning'
      case 'SPAM': return 'badge-danger'
      case 'TRASH': return 'badge-danger'
      default: return 'badge-info'
    }
  }

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Test Campaigns</h3>
          <div className="space-y-2">
            {tests.length === 0 ? (
              <p className="text-gray-500">No tests yet</p>
            ) : (
              tests.map(test => (
                <button
                  key={test.id}
                  onClick={() => handleTestSelect(test)}
                  className={`w-full text-left p-3 rounded-lg transition-colors ${
                    selectedTest?.id === test.id
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-100 hover:bg-gray-200 text-gray-900'
                  }`}
                >
                  <p className="font-medium">{test.campaign_name}</p>
                  <p className="text-sm opacity-75">{new Date(test.created_at).toLocaleDateString()}</p>
                </button>
              ))
            )}
          </div>
        </div>

        <div className="lg:col-span-2">
          {selectedTest && statistics ? (
            <div className="card">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-gray-900">Statistics</h3>
                <button
                  onClick={handleScanAgain}
                  disabled={loading}
                  className="btn-secondary flex items-center gap-2"
                >
                  <RefreshCw size={18} />
                  Rescan
                </button>
              </div>

              <div className="grid grid-cols-2 gap-4 mb-6">
                <div className="border border-gray-200 rounded p-3">
                  <p className="text-gray-600 text-sm">Inbox Rate</p>
                  <p className="text-2xl font-bold text-green-600">{statistics.inbox_percentage.toFixed(1)}%</p>
                </div>
                <div className="border border-gray-200 rounded p-3">
                  <p className="text-gray-600 text-sm">Spam Rate</p>
                  <p className="text-2xl font-bold text-red-600">{statistics.spam_percentage.toFixed(1)}%</p>
                </div>
                <div className="border border-gray-200 rounded p-3">
                  <p className="text-gray-600 text-sm">Delivery Rate</p>
                  <p className="text-2xl font-bold text-blue-600">{statistics.delivery_rate.toFixed(1)}%</p>
                </div>
                <div className="border border-gray-200 rounded p-3">
                  <p className="text-gray-600 text-sm">Total Accounts</p>
                  <p className="text-2xl font-bold text-gray-900">{statistics.total_accounts}</p>
                </div>
              </div>

              <div className="flex gap-2">
                <button
                  onClick={() => handleExport('csv')}
                  className="btn-secondary flex items-center gap-2 flex-1"
                >
                  <Download size={18} />
                  CSV
                </button>
                <button
                  onClick={() => handleExport('json')}
                  className="btn-secondary flex items-center gap-2 flex-1"
                >
                  <Download size={18} />
                  JSON
                </button>
              </div>
            </div>
          ) : (
            <div className="card text-center py-8">
              <p className="text-gray-500">Select a test to view results</p>
            </div>
          )}
        </div>
      </div>

      {selectedTest && (
        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Detailed Results</h3>
          <div className="overflow-x-auto">
            {loading ? (
              <p className="text-center py-4 text-gray-500">Loading results...</p>
            ) : results.length > 0 ? (
              <table className="table">
                <thead>
                  <tr>
                    <th>Email</th>
                    <th>Folder</th>
                    <th>Received Time</th>
                    <th>Delivery Time</th>
                    <th>Labels</th>
                  </tr>
                </thead>
                <tbody>
                  {results.map(result => (
                    <tr key={result.id}>
                      <td className="font-medium">{result.email || 'N/A'}</td>
                      <td>
                        <span className={`badge ${getFolderBadgeColor(result.folder)}`}>
                          {result.folder}
                        </span>
                      </td>
                      <td className="text-sm">
                        {result.received_time ? new Date(result.received_time).toLocaleString() : '-'}
                      </td>
                      <td className="text-sm">
                        {result.delivery_time_seconds ? `${result.delivery_time_seconds.toFixed(1)}s` : '-'}
                      </td>
                      <td className="text-sm">{result.labels || 'None'}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            ) : (
              <p className="text-center py-4 text-gray-500">No results yet. Run a scan to see results.</p>
            )}
          </div>
        </div>
      )}
    </div>
  )
}
