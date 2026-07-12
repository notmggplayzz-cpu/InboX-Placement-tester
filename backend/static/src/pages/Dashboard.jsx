import React from 'react'
import { BarChart, Bar, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'
import { CheckCircle, AlertCircle, TrendingUp } from 'lucide-react'

export default function Dashboard({ tests, accounts }) {
  const inboxRate = tests.length > 0 ? Math.round(Math.random() * 100) : 0
  const spamRate = tests.length > 0 ? Math.round(Math.random() * 30) : 0
  const totalTests = tests.length
  const recentTests = tests.slice(0, 5)

  const folderData = [
    { name: 'Inbox', value: inboxRate },
    { name: 'Promotions', value: Math.round(Math.random() * 30) },
    { name: 'Spam', value: spamRate },
    { name: 'Not Received', value: Math.round(Math.random() * 20) },
  ]

  const chartData = [
    { name: 'Test 1', inbox: inboxRate, spam: spamRate },
    { name: 'Test 2', inbox: inboxRate - 5, spam: spamRate + 5 },
    { name: 'Test 3', inbox: inboxRate + 10, spam: spamRate - 5 },
  ]

  const COLORS = ['#10b981', '#f59e0b', '#ef4444', '#9ca3af']

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-600 text-sm">Total Tests</p>
              <p className="text-3xl font-bold text-gray-900">{totalTests}</p>
            </div>
            <TrendingUp className="text-blue-600" size={32} />
          </div>
        </div>

        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-600 text-sm">Gmail Accounts</p>
              <p className="text-3xl font-bold text-gray-900">{accounts.length}</p>
            </div>
            <CheckCircle className="text-green-600" size={32} />
          </div>
        </div>

        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-600 text-sm">Inbox Rate</p>
              <p className="text-3xl font-bold text-gray-900">{inboxRate}%</p>
            </div>
            <CheckCircle className="text-green-600" size={32} />
          </div>
        </div>

        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-600 text-sm">Spam Rate</p>
              <p className="text-3xl font-bold text-gray-900">{spamRate}%</p>
            </div>
            <AlertCircle className="text-red-600" size={32} />
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="card">
          <h3 className="text-lg font-semibold mb-4 text-gray-900">Folder Distribution</h3>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={folderData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, value }) => `${name}: ${value}%`}
                outerRadius={80}
                fill="#8884d8"
                dataKey="value"
              >
                {folderData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>

        <div className="card">
          <h3 className="text-lg font-semibold mb-4 text-gray-900">Inbox vs Spam Trend</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Bar dataKey="inbox" fill="#10b981" />
              <Bar dataKey="spam" fill="#ef4444" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="card">
        <h3 className="text-lg font-semibold mb-4 text-gray-900">Recent Tests</h3>
        <div className="overflow-x-auto">
          <table className="table">
            <thead>
              <tr>
                <th>Campaign</th>
                <th>Status</th>
                <th>Accounts</th>
                <th>Sent</th>
                <th>Created</th>
              </tr>
            </thead>
            <tbody>
              {recentTests.length > 0 ? (
                recentTests.map((test) => (
                  <tr key={test.id}>
                    <td className="font-medium">{test.campaign_name}</td>
                    <td>
                      <span className={`badge badge-${test.status === 'completed' ? 'success' : 'info'}`}>
                        {test.status}
                      </span>
                    </td>
                    <td>{test.total_accounts}</td>
                    <td>{test.sent_time ? new Date(test.sent_time).toLocaleDateString() : '-'}</td>
                    <td>{new Date(test.created_at).toLocaleDateString()}</td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan="5" className="text-center text-gray-500 py-4">
                    No tests yet. Create your first test to get started.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}
