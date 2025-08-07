import { NextRequest, NextResponse } from 'next/server'
import { put } from '@vercel/blob'

export async function POST(request: NextRequest) {
  try {
    const formData = await request.formData()
    const files = formData.getAll('files') as File[]
    
    if (!files || files.length === 0) {
      return NextResponse.json(
        { error: 'No files provided' },
        { status: 400 }
      )
    }

    const uploadedDocuments = []

    for (const file of files) {
      if (file.size === 0) continue

      // Upload to Vercel Blob
      const blob = await put(file.name, file, {
        access: 'public',
      })

      uploadedDocuments.push({
        document_id: `doc-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
        filename: file.name,
        status: 'ready',
        file_size: file.size,
        document_type: file.name.split('.').pop()?.toLowerCase() || 'unknown',
        upload_timestamp: new Date().toISOString(),
        blob_url: blob.url,
        summary: `${file.name} uploaded successfully`
      })
    }

    return NextResponse.json({
      uploaded_documents: uploadedDocuments
    })

  } catch (error) {
    console.error('Upload error:', error)
    return NextResponse.json(
      { 
        error: `Upload failed: ${error instanceof Error ? error.message : 'Unknown error'}` 
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
