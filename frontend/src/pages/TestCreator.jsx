import React, { useState } from 'react'
import { Send } from 'lucide-react'
import { testsAPI } from '../services/api'

export default function TestCreator({ accounts, onSuccess }) {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const [formData, setFormData] = useState({
    campaign_name: '',
    subject: '',
    html_body: '',
    plain_text_body: '',
    sender_email: '',
    custom_headers: '',
  })

  const handleChange = (e) => {
    const { name, value } = e.target
    setFormData(prev => ({
      ...prev,
      [name]: value,
    }))
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setSuccess('')

    if (!formData.campaign_name || !formData.subject || !formData.html_body || !formData.sender_email) {
      setError('Please fill in all required fields')
      return
    }

    if (accounts.length === 0) {
      setError('Please connect at least one Gmail account first')
      return
    }

    try {
      setLoading(true)

      const testData = {
        ...formData,
        custom_headers: formData.custom_headers ? formData.custom_headers : null,
      }

      const response = await testsAPI.createTest(testData)
      setSuccess(`Test "${formData.campaign_name}" created successfully!`)

      await testsAPI.sendTest(response.data.id)
      setSuccess(`Test "${formData.campaign_name}" sent to ${accounts.length} accounts!`)

      setTimeout(() => {
        onSuccess()
      }, 1500)

      setFormData({
        campaign_name: '',
        subject: '',
        html_body: '',
        plain_text_body: '',
        sender_email: '',
        custom_headers: '',
      })
    } catch (err) {
      setError('Failed to create test: ' + (err.response?.data?.detail || err.message))
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="max-w-2xl mx-auto">
      <div className="card">
        <h2 className="text-2xl font-bold text-gray-900 mb-6">Create New Test</h2>

        {error && (
          <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700">
            {error}
          </div>
        )}

        {success && (
          <div className="mb-4 p-4 bg-green-50 border border-green-200 rounded-lg text-green-700">
            {success}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="form-group">
            <label className="form-label">Campaign Name *</label>
            <input
              type="text"
              name="campaign_name"
              value={formData.campaign_name}
              onChange={handleChange}
              placeholder="e.g., Q4 Newsletter Test"
              className="form-input"
              required
            />
          </div>

          <div className="form-group">
            <label className="form-label">From Email *</label>
            <input
              type="email"
              name="sender_email"
              value={formData.sender_email}
              onChange={handleChange}
              placeholder="sender@example.com"
              className="form-input"
              required
            />
          </div>

          <div className="form-group">
            <label className="form-label">Subject Line *</label>
            <input
              type="text"
              name="subject"
              value={formData.subject}
              onChange={handleChange}
              placeholder="Test Subject Line"
              className="form-input"
              required
            />
          </div>

          <div className="form-group">
            <label className="form-label">Plain Text Body</label>
            <textarea
              name="plain_text_body"
              value={formData.plain_text_body}
              onChange={handleChange}
              placeholder="Optional plain text version..."
              rows="4"
              className="form-textarea"
            />
          </div>

          <div className="form-group">
            <label className="form-label">HTML Body *</label>
            <textarea
              name="html_body"
              value={formData.html_body}
              onChange={handleChange}
              placeholder="<html><body>Your email content here...</body></html>"
              rows="8"
              className="form-textarea"
              required
            />
          </div>

          <div className="form-group">
            <label className="form-label">Custom Headers (JSON)</label>
            <textarea
              name="custom_headers"
              value={formData.custom_headers}
              onChange={handleChange}
              placeholder='{"X-Custom-Header": "value"}'
              rows="3"
              className="form-textarea"
            />
            <p className="text-sm text-gray-500 mt-1">Optional: Add custom email headers as JSON</p>
          </div>

          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
            <p className="text-sm text-blue-800">
              This test will be sent to <strong>{accounts.length}</strong> Gmail {accounts.length === 1 ? 'account' : 'accounts'}.
            </p>
          </div>

          <button
            type="submit"
            disabled={loading || accounts.length === 0}
            className="w-full btn-primary flex items-center justify-center gap-2"
          >
            <Send size={20} />
            {loading ? 'Creating & Sending...' : 'Create & Send Test'}
          </button>
        </form>
      </div>

      <div className="mt-6 card bg-gray-50">
        <h3 className="font-semibold text-gray-900 mb-2">Tips</h3>
        <ul className="space-y-2 text-sm text-gray-700">
          <li>• Use realistic content that matches your actual email campaigns</li>
          <li>• Test different subject lines and content variations</li>
          <li>• Check results after a few minutes for accurate delivery detection</li>
          <li>• Save the campaign name for easy reference</li>
        </ul>
      </div>
    </div>
  )
}
