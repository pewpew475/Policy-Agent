"use client"

import React, { useState, useEffect } from 'react'
import { X, Activity, FileText, Clock, TrendingUp, Key, AlertCircle } from 'lucide-react'
import { apiService, AnalyticsResponse, APIKey, SystemHealth } from '@/lib/api'

interface AnalyticsDashboardProps {
  isOpen: boolean
  onClose: () => void
}

export default function AnalyticsDashboard({ isOpen, onClose }: AnalyticsDashboardProps) {
  const [analytics, setAnalytics] = useState<AnalyticsResponse | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [apiKeys, setApiKeys] = useState<APIKey[]>([])
  const [systemHealth, setSystemHealth] = useState<SystemHealth | null>(null)

  useEffect(() => {
    if (isOpen) {
      fetchAnalytics()
    }
  }, [isOpen])

  const fetchAnalytics = async () => {
    setLoading(true)
    setError(null)
    
    try {
      const [analyticsData, keysData, healthData] = await Promise.all([
        apiService.getAnalytics(7),
        apiService.getAPIKeys(),
        apiService.getSystemHealth()
      ])
      
      setAnalytics(analyticsData)
      setApiKeys(keysData)
      setSystemHealth(healthData)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch analytics')
    } finally {
      setLoading(false)
    }
  }

  const generateAPIKey = async () => {
    try {
      const keyName = prompt('Enter API key name:')
      if (!keyName) return
      
      const description = prompt('Enter description (optional):') || undefined
      
      await apiService.generateAPIKey(keyName, description)
      await fetchAnalytics() // Refresh data
      alert('API key generated successfully!')
    } catch (err) {
      alert(`Failed to generate API key: ${err instanceof Error ? err.message : 'Unknown error'}`)
    }
  }

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-6xl w-full max-h-[90vh] overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b">
          <h2 className="text-2xl font-bold text-gray-900">Analytics Dashboard</h2>
          <button
            onClick={onClose}
            className="p-2 hover:bg-gray-100 rounded-full transition-colors"
          >
            <X className="w-6 h-6" />
          </button>
        </div>

        {/* Content */}
        <div className="p-6 overflow-y-auto max-h-[calc(90vh-120px)]">
          {loading && (
            <div className="flex items-center justify-center py-12">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-[#ff3f17]"></div>
              <span className="ml-2">Loading analytics...</span>
            </div>
          )}

          {error && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
              <div className="flex items-center">
                <AlertCircle className="w-5 h-5 text-red-500 mr-2" />
                <span className="text-red-700">{error}</span>
              </div>
            </div>
          )}

          {analytics && (
            <div className="space-y-6">
              {/* System Health */}
              {systemHealth && (
                <div className="bg-gray-50 rounded-lg p-4">
                  <h3 className="text-lg font-semibold mb-3 flex items-center">
                    <Activity className="w-5 h-5 mr-2" />
                    System Health
                  </h3>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    <div className="text-center">
                      <div className={`text-2xl font-bold ${systemHealth.status === 'healthy' ? 'text-green-600' : 'text-red-600'}`}>
                        {systemHealth.status === 'healthy' ? '🟢' : '🔴'}
                      </div>
                      <div className="text-sm text-gray-600">Status</div>
                    </div>
                    <div className="text-center">
                      <div className="text-2xl font-bold text-blue-600">{systemHealth.avg_response_time_1h?.toFixed(2)}s</div>
                      <div className="text-sm text-gray-600">Avg Response Time</div>
                    </div>
                    <div className="text-center">
                      <div className="text-2xl font-bold text-purple-600">{systemHealth.requests_1h}</div>
                      <div className="text-sm text-gray-600">Requests (1h)</div>
                    </div>
                    <div className="text-center">
                      <div className="text-2xl font-bold text-orange-600">{systemHealth.error_rate_1h?.toFixed(1)}%</div>
                      <div className="text-sm text-gray-600">Error Rate</div>
                    </div>
                  </div>
                </div>
              )}

              {/* Usage Statistics */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="bg-blue-50 rounded-lg p-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-blue-600 text-sm font-medium">Total Requests</p>
                      <p className="text-2xl font-bold text-blue-900">{analytics.usage_stats.total_requests}</p>
                    </div>
                    <TrendingUp className="w-8 h-8 text-blue-600" />
                  </div>
                </div>

                <div className="bg-green-50 rounded-lg p-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-green-600 text-sm font-medium">Documents Processed</p>
                      <p className="text-2xl font-bold text-green-900">{analytics.usage_stats.documents_processed}</p>
                    </div>
                    <FileText className="w-8 h-8 text-green-600" />
                  </div>
                </div>

                <div className="bg-purple-50 rounded-lg p-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-purple-600 text-sm font-medium">Avg Response Time</p>
                      <p className="text-2xl font-bold text-purple-900">{analytics.usage_stats.average_response_time.toFixed(2)}s</p>
                    </div>
                    <Clock className="w-8 h-8 text-purple-600" />
                  </div>
                </div>
              </div>

              {/* Error Rates */}
              <div className="bg-white border rounded-lg p-4">
                <h3 className="text-lg font-semibold mb-3">Error Rates</h3>
                <div className="grid grid-cols-3 gap-4">
                  <div className="text-center">
                    <div className="text-2xl font-bold text-green-600">{analytics.error_rates['2xx'].toFixed(1)}%</div>
                    <div className="text-sm text-gray-600">Success (2xx)</div>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold text-yellow-600">{analytics.error_rates['4xx'].toFixed(1)}%</div>
                    <div className="text-sm text-gray-600">Client Errors (4xx)</div>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold text-red-600">{analytics.error_rates['5xx'].toFixed(1)}%</div>
                    <div className="text-sm text-gray-600">Server Errors (5xx)</div>
                  </div>
                </div>
              </div>

              {/* Top Endpoints */}
              {analytics.top_endpoints.length > 0 && (
                <div className="bg-white border rounded-lg p-4">
                  <h3 className="text-lg font-semibold mb-3">Top Endpoints</h3>
                  <div className="space-y-2">
                    {analytics.top_endpoints.slice(0, 5).map((endpoint, index) => (
                      <div key={index} className="flex justify-between items-center py-2 border-b last:border-b-0">
                        <span className="font-mono text-sm">{endpoint.endpoint}</span>
                        <div className="text-right">
                          <div className="text-sm font-medium">{endpoint.count} requests</div>
                          <div className="text-xs text-gray-500">{endpoint.avg_response_time.toFixed(2)}s avg</div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Document Types */}
              {Object.keys(analytics.document_types).length > 0 && (
                <div className="bg-white border rounded-lg p-4">
                  <h3 className="text-lg font-semibold mb-3">Document Types Processed</h3>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    {Object.entries(analytics.document_types).map(([type, count]) => (
                      <div key={type} className="text-center">
                        <div className="text-2xl font-bold text-gray-900">{count}</div>
                        <div className="text-sm text-gray-600 uppercase">{type}</div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* API Key Management */}
              <div className="bg-white border rounded-lg p-4">
                <div className="flex items-center justify-between mb-3">
                  <h3 className="text-lg font-semibold flex items-center">
                    <Key className="w-5 h-5 mr-2" />
                    API Key Management
                  </h3>
                  <button
                    onClick={generateAPIKey}
                    className="bg-[#ff3f17] text-white px-4 py-2 rounded-lg hover:bg-[#ff3f17]/90 transition-colors"
                  >
                    Generate New Key
                  </button>
                </div>
                
                {apiKeys.length > 0 ? (
                  <div className="space-y-2">
                    {apiKeys.slice(0, 5).map((key, index) => (
                      <div key={index} className="flex justify-between items-center py-2 border-b last:border-b-0">
                        <div>
                          <div className="font-medium">{key.name}</div>
                          <div className="text-sm text-gray-500">
                            Created: {new Date(key.created_at).toLocaleDateString()}
                          </div>
                        </div>
                        <div className="text-right">
                          <div className={`text-sm font-medium ${key.is_active ? 'text-green-600' : 'text-red-600'}`}>
                            {key.is_active ? 'Active' : 'Inactive'}
                          </div>
                          <div className="text-xs text-gray-500">{key.usage_count} uses</div>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-gray-500 text-center py-4">No API keys generated yet</p>
                )}
              </div>

              {/* Refresh Button */}
              <div className="text-center">
                <button
                  onClick={fetchAnalytics}
                  disabled={loading}
                  className="bg-gray-100 hover:bg-gray-200 text-gray-700 px-6 py-2 rounded-lg transition-colors disabled:opacity-50"
                >
                  {loading ? 'Refreshing...' : 'Refresh Data'}
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
