import React from 'react'
import { Mail, BarChart3, Settings, Plus } from 'lucide-react'

export default function Navbar({ currentPage, setCurrentPage }) {
  const navItems = [
    { id: 'dashboard', label: 'Dashboard', icon: BarChart3 },
    { id: 'create', label: 'New Test', icon: Plus },
    { id: 'results', label: 'Results', icon: Mail },
    { id: 'accounts', label: 'Accounts', icon: Settings },
  ]

  return (
    <nav className="bg-white shadow-sm border-b border-gray-200">
      <div className="max-w-7xl mx-auto px-4 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="bg-blue-600 p-2 rounded-lg">
              <Mail className="text-white" size={24} />
            </div>
            <h1 className="text-2xl font-bold text-gray-900">Inbox Placement Tester</h1>
          </div>

          <div className="flex gap-2">
            {navItems.map(({ id, label, icon: Icon }) => (
              <button
                key={id}
                onClick={() => setCurrentPage(id)}
                className={`flex items-center gap-2 px-4 py-2 rounded-lg font-medium transition-colors ${
                  currentPage === id
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                <Icon size={18} />
                <span className="hidden sm:inline">{label}</span>
              </button>
            ))}
          </div>
        </div>
      </div>
    </nav>
  )
}
