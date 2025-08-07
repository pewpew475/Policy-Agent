import { NextResponse } from 'next/server'

export async function GET() {
  try {
    const mockHealthData = {
      status: 'healthy',
      version: '1.0.0',
      services: {
        api: 'active',
        upload: 'active',
        chat: 'active',
        analytics: 'active'
      },
      uptime: 3600,
      avg_response_time_1h: 0.85,
      requests_1h: 234,
      error_rate_1h: 2.4
    }

    return NextResponse.json(mockHealthData, {
      headers: {
        'Access-Control-Allow-Origin': '*',
      }
    })

  } catch (error) {
    console.error('System health error:', error)
    return NextResponse.json(
      { error: `Health check failed: ${error instanceof Error ? error.message : 'Unknown error'}` },
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
