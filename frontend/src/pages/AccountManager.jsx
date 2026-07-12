import React, { useState } from 'react'
import { Plus, Trash2, ExternalLink } from 'lucide-react'
import { accountsAPI } from '../services/api'

export default function AccountManager({ accounts, onRefresh }) {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const handleConnect = async () => {
    try {
      setLoading(true)
      const state = 'user_' + Date.now()
      const response = await accountsAPI.getOAuthUrl(state)
      window.location.href = response.data.url
    } catch (err) {
      setError('Failed to connect account: ' + err.message)
    } finally {
      setLoading(false)
    }
  }

  const handleDelete = async (id) => {
    if (!window.confirm('Are you sure you want to delete this account?')) return

    try {
      setLoading(true)
      await accountsAPI.deleteAccount(id)
      onRefresh()
    } catch (err) {
      setError('Failed to delete account: ' + err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-6">
      <div className="card">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-2xl font-bold text-gray-900">Gmail Accounts</h2>
          <button
            onClick={handleConnect}
            disabled={loading}
            className="btn-primary flex items-center gap-2"
          >
            <Plus size={20} />
            Connect Account
          </button>
        </div>

        {error && (
          <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700">
            {error}
          </div>
        )}

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {accounts.map((account) => (
            <div key={account.id} className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
              <div className="flex items-start justify-between mb-3">
                <div>
                  <h3 className="font-semibold text-gray-900">{account.email}</h3>
                  {account.nickname && (
                    <p className="text-sm text-gray-600">{account.nickname}</p>
                  )}
                </div>
                <span className="inline-block px-2 py-1 bg-green-100 text-green-800 text-xs font-semibold rounded">
                  Active
                </span>
              </div>

              <div className="space-y-2 mb-4 text-sm text-gray-600">
                <p>Last Sync: {account.last_sync ? new Date(account.last_sync).toLocaleString() : 'Never'}</p>
                <p>Connected: {new Date(account.created_at).toLocaleDateString()}</p>
              </div>

              <button
                onClick={() => handleDelete(account.id)}
                disabled={loading}
                className="w-full btn-danger flex items-center justify-center gap-2"
              >
                <Trash2 size={18} />
                Delete
              </button>
            </div>
          ))}
        </div>

        {accounts.length === 0 && (
          <div className="text-center py-12">
            <p className="text-gray-500 mb-4">No Gmail accounts connected yet</p>
            <button
              onClick={handleConnect}
              disabled={loading}
              className="btn-primary"
            >
              Connect Your First Account
            </button>
          </div>
        )}
      </div>

      <div className="card bg-blue-50 border border-blue-200">
        <h3 className="text-lg font-semibold text-blue-900 mb-2">How to Connect an Account</h3>
        <ol className="list-decimal list-inside space-y-2 text-blue-800">
          <li>Click "Connect Account" button above</li>
          <li>Sign in with your Gmail account</li>
          <li>Grant permission to read and send emails</li>
          <li>Your account will appear in the list above</li>
        </ol>
      </div>
    </div>
  )
}
