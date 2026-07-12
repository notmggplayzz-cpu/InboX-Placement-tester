import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api'

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error.response?.data || error.message)
    return Promise.reject(error)
  }
)

export const accountsAPI = {
  getOAuthUrl: (state) => api.get('/accounts/oauth-url', { params: { state } }),
  listAccounts: () => api.get('/accounts'),
  getAccount: (id) => api.get(`/accounts/${id}`),
  updateAccount: (id, data) => api.patch(`/accounts/${id}`, data),
  deleteAccount: (id) => api.delete(`/accounts/${id}`),
}

export const testsAPI = {
  createTest: (data) => api.post('/tests', data),
  listTests: (params) => api.get('/tests', { params }),
  getTest: (id) => api.get(`/tests/${id}`),
  sendTest: (id) => api.post(`/tests/${id}/send`),
  scanTest: (id) => api.post(`/tests/${id}/scan`),
  getResults: (id) => api.get(`/tests/${id}/results`),
  getStatistics: (id) => api.get(`/tests/${id}/statistics`),
  deleteTest: (id) => api.delete(`/tests/${id}`),
}

export default api
