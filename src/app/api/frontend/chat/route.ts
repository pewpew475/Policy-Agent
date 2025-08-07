import { NextRequest, NextResponse } from 'next/server'

// AI API configurations
const GLM_API_KEY = process.env.GLM_API_KEY
const GLM_API_URL = process.env.GLM_API_URL || 'https://open.bigmodel.cn/api/paas/v4/'
const GEMINI_API_KEYS = [
  process.env.GEMINI_API_KEY_1,
  process.env.GEMINI_API_KEY_2,
  process.env.GEMINI_API_KEY_3,
  process.env.GEMINI_API_KEY_4,
  process.env.GEMINI_API_KEY_5,
].filter(Boolean)

async function callGLMAPI(message: string, documentContext?: string): Promise<string> {
  if (!GLM_API_KEY) {
    throw new Error('GLM API key not configured')
  }

  const prompt = documentContext
    ? `Based on the following insurance document context:\n\n${documentContext}\n\nUser question: ${message}\n\nPlease provide a helpful response about the insurance policy.`
    : `As an insurance AI assistant, please help with this question: ${message}`

  try {
    const response = await fetch(`${GLM_API_URL}chat/completions`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${GLM_API_KEY}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        model: 'glm-4',
        messages: [
          {
            role: 'system',
            content: 'You are a helpful insurance AI assistant. Provide clear, accurate information about insurance policies and help users understand their coverage.'
          },
          {
            role: 'user',
            content: prompt
          }
        ],
        temperature: 0.7,
        max_tokens: 1000
      })
    })

    if (!response.ok) {
      throw new Error(`GLM API error: ${response.status}`)
    }

    const data = await response.json()
    return data.choices?.[0]?.message?.content || 'Sorry, I could not generate a response.'
  } catch (error) {
    console.error('GLM API error:', error)
    throw error
  }
}

async function callGeminiAPI(message: string, documentContext?: string): Promise<string> {
  if (GEMINI_API_KEYS.length === 0) {
    throw new Error('No Gemini API keys configured')
  }

  const prompt = documentContext
    ? `Based on the following insurance document context:\n\n${documentContext}\n\nUser question: ${message}\n\nPlease provide a helpful response about the insurance policy.`
    : `As an insurance AI assistant, please help with this question: ${message}`

  // Try each Gemini API key until one works
  for (const apiKey of GEMINI_API_KEYS) {
    try {
      const response = await fetch(
        `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent?key=${apiKey}`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            contents: [{
              parts: [{
                text: prompt
              }]
            }],
            generationConfig: {
              temperature: 0.7,
              maxOutputTokens: 1000,
            }
          })
        }
      )

      if (!response.ok) {
        console.warn(`Gemini API key failed: ${response.status}`)
        continue
      }

      const data = await response.json()
      return data.candidates?.[0]?.content?.parts?.[0]?.text || 'Sorry, I could not generate a response.'
    } catch (error) {
      console.warn('Gemini API key error:', error)
      continue
    }
  }

  throw new Error('All Gemini API keys failed')
}

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

    // For now, we'll use a simple document context placeholder
    // In a real implementation, you'd fetch the actual document content from Vercel Blob
    const documentContext = docIds.length > 0
      ? `Document analysis: ${docIds.length} insurance document(s) have been uploaded and are being referenced for this query.`
      : undefined

    let aiResponse: string
    const startTime = Date.now()

    try {
      // Try GLM API first
      console.log('Attempting GLM API...')
      aiResponse = await callGLMAPI(message, documentContext)
      console.log('GLM API successful')
    } catch (glmError) {
      console.log('GLM API failed, trying Gemini...', glmError)
      try {
        // Fallback to Gemini API
        aiResponse = await callGeminiAPI(message, documentContext)
        console.log('Gemini API successful')
      } catch (geminiError) {
        console.error('Both APIs failed:', { glmError, geminiError })
        // Final fallback
        aiResponse = `I apologize, but I'm currently experiencing technical difficulties with my AI services. Please try again in a moment.

Your question: "${message}"

${docIds.length > 0 ? `I can see you've uploaded ${docIds.length} document(s), but I'm unable to analyze them right now due to the service issue.` : ''}

Please contact support if this issue persists.`
      }
    }

    const responseTime = (Date.now() - startTime) / 1000

    return NextResponse.json({
      message: aiResponse,
      conversation_id: `conv-${Date.now()}`,
      response_time: responseTime,
      sources: docIds
    }, {
      headers: {
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
