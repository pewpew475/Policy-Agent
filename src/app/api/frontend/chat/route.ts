import { NextRequest, NextResponse } from 'next/server'

export async function POST(request: NextRequest) {
  try {
    const formData = await request.formData()
    const message = formData.get('message') as string
    const documentIds = formData.get('document_ids') as string

    if (!message) {
      return NextResponse.json(
        { error: 'Message is required' },
        { status: 400 }
      )
    }

    const docIds = documentIds ? documentIds.split(',') : []

    // Mock AI response for now
    let aiResponse = `I understand you're asking: "${message}". `
    
    if (docIds.length > 0) {
      aiResponse += `I've analyzed ${docIds.length} document(s). `
    }
    
    aiResponse += "This is a demo response from the Insurance AI Assistant. The full AI integration with GLM and Gemini APIs will be available once the backend is properly configured with your API keys."

    // Create a readable stream for the response (to match the expected format)
    const encoder = new TextEncoder()
    const stream = new ReadableStream({
      start(controller) {
        const responseData = JSON.stringify({
          message: aiResponse,
          conversation_id: `conv-${Date.now()}`,
          response_time: 0.5,
          sources: docIds
        })
        
        controller.enqueue(encoder.encode(responseData))
        controller.close()
      }
    })

    return new Response(stream, {
      headers: {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
      }
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
