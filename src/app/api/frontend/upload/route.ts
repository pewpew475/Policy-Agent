import { NextRequest, NextResponse } from 'next/server'
import { put } from '@vercel/blob'
import { documentStore } from '../../../../lib/documentStore'

async function extractTextFromPDF(file: File): Promise<string> {
  try {
    // Dynamic import to avoid build issues
    const pdf = (await import('pdf-parse')).default
    const arrayBuffer = await file.arrayBuffer()
    const buffer = Buffer.from(arrayBuffer)
    const data = await pdf(buffer)
    return data.text
  } catch (error) {
    console.error('PDF extraction error:', error)
    return `Error extracting text from PDF: ${error instanceof Error ? error.message : 'Unknown error'}`
  }
}

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

      const documentId = `doc-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`

      // Extract text content from PDF
      let extractedText = ''
      let summary = `${file.name} uploaded successfully`

      if (file.type === 'application/pdf' || file.name.toLowerCase().endsWith('.pdf')) {
        console.log(`Extracting text from PDF: ${file.name}`)
        extractedText = await extractTextFromPDF(file)

        if (extractedText && extractedText.length > 0) {
          // Store the extracted text
          documentStore.set(documentId, extractedText)
          summary = `PDF content extracted successfully (${extractedText.length} characters)`
          console.log(`PDF text extracted: ${extractedText.substring(0, 200)}...`)
        } else {
          summary = `PDF uploaded but text extraction failed`
        }
      } else {
        summary = `File uploaded (non-PDF, no text extraction)`
      }

      // Upload to Vercel Blob
      const blob = await put(file.name, file, {
        access: 'public',
      })

      uploadedDocuments.push({
        document_id: documentId,
        filename: file.name,
        status: 'ready',
        file_size: file.size,
        document_type: file.name.split('.').pop()?.toLowerCase() || 'unknown',
        upload_timestamp: new Date().toISOString(),
        blob_url: blob.url,
        summary: summary,
        has_extracted_text: extractedText.length > 0
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
