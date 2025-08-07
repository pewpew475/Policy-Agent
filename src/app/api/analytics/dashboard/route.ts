import { NextRequest, NextResponse } from 'next/server'

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url)
    // const days = searchParams.get('days') || '7' // Future use

    // Mock analytics data
    const mockData = {
      usage_stats: {
        total_requests: 1250,
        successful_requests: 1180,
        failed_requests: 70,
        average_response_time: 0.85,
        documents_processed: 45,
        api_calls_today: 89
      },
      top_endpoints: [
        { endpoint: '/api/frontend/upload', count: 234, avg_response_time: 1.2 },
        { endpoint: '/api/frontend/message', count: 189, avg_response_time: 0.8 },
        { endpoint: '/health', count: 156, avg_response_time: 0.1 },
        { endpoint: '/hackrx/run', count: 23, avg_response_time: 2.5 }
      ],
      error_rates: {
        '2xx': 94.4,
        '4xx': 3.2,
        '5xx': 2.4
      },
      response_times: [
        { timestamp: '2024-01-01T00:00:00Z', avg_response_time: 0.8, request_count: 45 },
        { timestamp: '2024-01-01T01:00:00Z', avg_response_time: 0.9, request_count: 52 },
        { timestamp: '2024-01-01T02:00:00Z', avg_response_time: 0.7, request_count: 38 }
      ],
      document_types: {
        pdf: 28,
        docx: 12,
        txt: 5
      }
    }

    return NextResponse.json(mockData, {
      headers: {
        'Access-Control-Allow-Origin': '*',
      }
    })

  } catch (error) {
    console.error('Analytics error:', error)
    return NextResponse.json(
      { error: `Analytics failed: ${error instanceof Error ? error.message : 'Unknown error'}` },
      { status: 500 }
    )
  }
}

export async function OPTIONS() {
  return new NextResponse(null, {
    status: 200,
    headers: {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'GET, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type, Authorization',
    },
  })
}
