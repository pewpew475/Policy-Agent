import { NextRequest, NextResponse } from 'next/server'

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    const { message, document_ids = [] } = body

    if (!message) {
      return NextResponse.json(
        { error: 'Message is required' },
        { status: 400 }
      )
    }

    // Mock AI response for now
    let aiResponse = `I understand you're asking: "${message}". `
    
    if (document_ids.length > 0) {
      aiResponse += `I've analyzed ${document_ids.length} document(s). `
    }
    
    aiResponse += "This is a demo response from the Insurance AI Assistant. The full AI integration with GLM and Gemini APIs will be available once the backend is properly configured with your API keys."

    return NextResponse.json({
      message: aiResponse,
      conversation_id: `conv-${Date.now()}`,
      response_time: 0.5,
      sources: document_ids
    })

  } catch (error) {
    console.error('Chat error:', error)
    return NextResponse.json(
      { 
        error: `Chat failed: ${error instanceof Error ? error.message : 'Unknown error'}` 
      },
      { status: 500 }
    )
  }
}

export async function OPTIONS() {
  return new NextResponse(null, {
    status: 200,
    headers: {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'POST, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type, Authorization',
    },
  })
}
