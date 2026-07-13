import React, { useState, useEffect } from 'react'
import { Mail, Settings, BarChart3, Plus } from 'lucide-react'
import Navbar from './components/Navbar'
import Dashboard from './pages/Dashboard'
import AccountManager from './pages/AccountManager'
import TestCreator from './pages/TestCreator'
import TestResults from './pages/TestResults'

export default function App() {
  const [currentPage, setCurrentPage] = useState('dashboard')
  const [accounts, setAccounts] = useState([])
  const [tests, setTests] = useState([])
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    loadInitialData()
  }, [])

  const loadInitialData = async () => {
    setLoading(true)
    try {
      const { accountsAPI, testsAPI } = await import('./services/api')

      // Load accounts
      const accountsRes = await accountsAPI.listAccounts()
      const accountsData = Array.isArray(accountsRes) ? accountsRes :
                          Array.isArray(accountsRes.data) ? accountsRes.data : []
      console.log('Loaded accounts:', accountsData, 'Count:', accountsData.length)
      setAccounts(accountsData)

      // Load tests
      try {
        const testsRes = await testsAPI.listTests({ limit: 10 })
        const testsData = Array.isArray(testsRes) ? testsRes :
                         Array.isArray(testsRes.data) ? testsRes.data : []
        console.log('Loaded tests:', testsData)
        setTests(testsData)
      } catch (testError) {
        console.warn('Failed to load tests (non-fatal):', testError)
      }
    } catch (error) {
      console.error('Failed to load accounts:', error)
      setAccounts([])
    } finally {
      setLoading(false)
    }
  }

  const renderPage = () => {
    switch (currentPage) {
      case 'dashboard':
        return <Dashboard tests={tests} accounts={accounts} />
      case 'accounts':
        return <AccountManager accounts={accounts} onRefresh={loadInitialData} />
      case 'create':
        return <TestCreator accounts={accounts} onSuccess={() => {
          setCurrentPage('dashboard')
          loadInitialData()
        }} />
      case 'results':
        return <TestResults tests={tests} />
      default:
        return <Dashboard tests={tests} accounts={accounts} />
    }
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar currentPage={currentPage} setCurrentPage={setCurrentPage} />

      <main className="max-w-7xl mx-auto px-4 py-8">
        {loading && <div className="text-center py-8">Loading...</div>}
        {!loading && renderPage()}
      </main>
    </div>
  )
}
