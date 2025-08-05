"use client"

import AiInput from '@/components/ui/ai-input'
import React, { useState, useEffect } from 'react'
import Navigation from '@/components/Navigation/navigation'
import AnalyticsDashboard from '@/components/Analytics/AnalyticsDashboard'
import { Globe, ArrowRight, Copy, Check } from 'lucide-react'
import { apiService, UploadedDocument } from '@/lib/api'

interface Message {
  text: string;
  isAi: boolean;
  timestamp?: Date;
  documentIds?: string[];
}

interface ChatHistory {
  id: string;
  title: string;
  messages: Message[];
  timestamp: Date;
}

const Page = () => {
  const [messages, setMessages] = useState<Message[]>([])
  const [isAiTyping, setIsAiTyping] = useState(false)
  const [chatHistory, setChatHistory] = useState<ChatHistory[]>([])
  const [currentChatId, setCurrentChatId] = useState<string | null>(null)
  const [isNavigationOpen, setIsNavigationOpen] = useState(false)
  const [isBackendConnected, setIsBackendConnected] = useState(false)
  const [showAnalytics, setShowAnalytics] = useState(false)
  const [uploadedDocuments, setUploadedDocuments] = useState<string[]>([])
  const [isUploading, setIsUploading] = useState(false)
  const [copiedMessageIndex, setCopiedMessageIndex] = useState<number | null>(null)

  // Check backend connectivity on component mount
  useEffect(() => {
    const checkBackend = async () => {
      try {
        const isHealthy = await apiService.checkHealth()
        setIsBackendConnected(isHealthy)
      } catch (error) {
        console.error('Backend connectivity check failed:', error)
        setIsBackendConnected(false)
      }
    }

    checkBackend()
    // Check every 30 seconds
    const interval = setInterval(checkBackend, 30000)
    return () => clearInterval(interval)
  }, [])

  const handleCopyMessage = async (text: string, index: number) => {
    try {
      await navigator.clipboard.writeText(text)
      setCopiedMessageIndex(index)
      setTimeout(() => setCopiedMessageIndex(null), 2000)
    } catch (err) {
      console.error('Failed to copy text:', err)
    }
  }

  const generateChatTitle = (messages: Message[]): string => {
    if (messages.length === 0) return "New Chat"
    const firstUserMessage = messages.find(msg => !msg.isAi)
    if (firstUserMessage) {
      return firstUserMessage.text.length > 30
        ? firstUserMessage.text.substring(0, 30) + "..."
        : firstUserMessage.text
    }
    return "New Chat"
  }

  const handleNewChat = () => {
    // Save current chat to history if it has messages
    if (messages.length > 0) {
      const newChat: ChatHistory = {
        id: Date.now().toString(),
        title: generateChatTitle(messages),
        messages: [...messages],
        timestamp: new Date()
      }
      setChatHistory(prev => [newChat, ...prev])
    }

    // Clear current chat
    setMessages([])
    setCurrentChatId(null)
    setIsAiTyping(false)
  }

  const handleLoadChat = (chat: ChatHistory) => {
    // Save current chat if it has messages and is different from the one being loaded
    if (messages.length > 0 && currentChatId !== chat.id) {
      const currentChat: ChatHistory = {
        id: currentChatId || Date.now().toString(),
        title: generateChatTitle(messages),
        messages: [...messages],
        timestamp: new Date()
      }
      setChatHistory(prev => {
        const filtered = prev.filter(c => c.id !== currentChatId)
        return [currentChat, ...filtered]
      })
    }

    // Load selected chat
    setMessages(chat.messages)
    setCurrentChatId(chat.id)
    setIsAiTyping(false)
  }

  const handleDeleteChat = (chatId: string) => {
    setChatHistory(prev => prev.filter(chat => chat.id !== chatId))

    // If the deleted chat was the current one, clear the current chat
    if (currentChatId === chatId) {
      setMessages([])
      setCurrentChatId(null)
      setIsAiTyping(false)
    }
  }

  const handleMessage = async (message: string, files?: File[]) => {
    // Add user message
    const userMessage: Message = {
      text: message,
      isAi: false,
      timestamp: new Date()
    }
    setMessages(prev => [...prev, userMessage])
    setIsAiTyping(true)

    try {
      if (!isBackendConnected) {
        // Fallback to demo mode if backend is not connected
        setTimeout(() => {
          setMessages(prev => [...prev, {
            text: "⚠️ Backend not connected. This is a demo response. Please ensure the backend server is running on http://localhost:8000",
            isAi: true,
            timestamp: new Date()
          }])
          setIsAiTyping(false)
        }, 1000)
        return
      }

      let documentIds: string[] = []

      // Step 1: Upload files first if any
      if (files && files.length > 0) {
        setIsUploading(true)
        try {
          const uploadResult = await apiService.uploadFiles(files)

          // Extract document IDs from successful uploads
          documentIds = uploadResult.uploaded_documents
            .filter(doc => doc.status === 'ready' && doc.document_id)
            .map(doc => doc.document_id!)

          // Update uploaded documents list
          setUploadedDocuments(prev => [...prev, ...documentIds])

          // Show upload status
          const uploadStatus = uploadResult.uploaded_documents
            .map(doc => `📄 ${doc.filename}: ${doc.status === 'ready' ? '✅ Ready' : '❌ Failed'}`)
            .join('\n')

          setMessages(prev => [...prev, {
            text: `📁 File Upload Status:\n${uploadStatus}`,
            isAi: true,
            timestamp: new Date()
          }])

        } catch (uploadError) {
          console.error('Error uploading files:', uploadError)
          setMessages(prev => [...prev, {
            text: `❌ Upload Error: ${uploadError instanceof Error ? uploadError.message : 'Failed to upload files'}`,
            isAi: true,
            timestamp: new Date()
          }])
          setIsAiTyping(false)
          setIsUploading(false)
          return
        } finally {
          setIsUploading(false)
        }
      }

      // Step 2: Send chat message with document context
      const contextDocuments = documentIds.length > 0 ? documentIds : uploadedDocuments

      // Debug log
      console.log('Sending message with documents:', contextDocuments)

      // Show user which documents are being analyzed
      if (contextDocuments.length > 0) {
        setMessages(prev => [...prev, {
          text: `🔍 Analyzing ${contextDocuments.length} document(s) to answer your question...`,
          isAi: true,
          timestamp: new Date()
        }])
      } else {
        setMessages(prev => [...prev, {
          text: `⚠️ No documents uploaded yet. Please upload your insurance documents first using the 📎 icon.`,
          isAi: true,
          timestamp: new Date()
        }])
        setIsAiTyping(false)
        return
      }

      const stream = await apiService.sendChatMessage(message, contextDocuments)

      // Start with empty AI message
      let aiResponse = ""
      setMessages(prev => [...prev, { text: "", isAi: true, timestamp: new Date() }])

      // Stream the response
      for await (const chunk of apiService.parseStreamingResponse(stream)) {
        aiResponse += chunk
        setMessages(prev => {
          const newMessages = [...prev]
          const lastMessage = newMessages[newMessages.length - 1]
          if (lastMessage && lastMessage.isAi) {
            lastMessage.text = aiResponse
          }
          return newMessages
        })
      }

      setIsAiTyping(false)

    } catch (error) {
      console.error('Error sending message:', error)
      setMessages(prev => [...prev, {
        text: `❌ Error: ${error instanceof Error ? error.message : 'Failed to send message'}`,
        isAi: true,
        timestamp: new Date()
      }])
      setIsAiTyping(false)
    }
  }

  return (
    <div className='flex h-screen'>
      {/* Navigation Sidebar */}
      <div className={`transition-all duration-300 ${isNavigationOpen ? 'w-64' : 'w-0'} overflow-hidden`}>
        <Navigation
          isOpen={isNavigationOpen}
          onToggle={() => setIsNavigationOpen(!isNavigationOpen)}
          onNewChat={handleNewChat}
          onLoadChat={handleLoadChat}
          onDeleteChat={handleDeleteChat}
          chatHistory={chatHistory}
          currentChatId={currentChatId}
        />
      </div>

      {/* Main Chat Area */}
      <div className='flex-1 flex flex-col relative'>
        {/* Navigation Toggle Button - Always visible */}
        {!isNavigationOpen && (
          <button
            onClick={() => setIsNavigationOpen(true)}
            className="absolute top-4 left-4 z-10 bg-white p-2 rounded-full shadow-lg hover:shadow-xl transition-shadow"
          >
            <Globe className="w-6 h-6" />
          </button>
        )}

        {/* Analytics Dashboard Button - Top Right */}
        <button
          onClick={() => setShowAnalytics(true)}
          className="absolute top-4 right-4 z-10 bg-white p-2 rounded-full shadow-lg hover:shadow-xl transition-shadow"
          title="Analytics Dashboard"
        >
          <ArrowRight className="w-6 h-6" />
        </button>

        {/* Backend Connection Status */}
        <div className={`absolute top-4 right-16 z-10 px-3 py-1 rounded-full text-xs font-medium ${
          isBackendConnected
            ? 'bg-green-100 text-green-800'
            : 'bg-red-100 text-red-800'
        }`}>
          {isBackendConnected ? '🟢 Connected' : '🔴 Disconnected'}
        </div>

        {/* Messages Area */}
        <div className="flex-1 overflow-y-auto px-4 pb-40 pt-16">
          <div className="max-w-4xl mx-auto">
            {/* Uploaded Documents Indicator */}
            {uploadedDocuments.length > 0 && (
              <div className="mb-4 p-3 bg-green-50 border border-green-200 rounded-lg">
                <div className="flex items-center gap-2 text-green-800">
                  <span className="text-sm font-medium">📄 {uploadedDocuments.length} document(s) ready for analysis</span>
                </div>
              </div>
            )}

            <div className="flex flex-col gap-4 py-4 mb-8">
              {messages.map((msg, index) => (
                <div
                  key={index}
                  className={`group relative max-w-[80%] ${
                    msg.isAi ? 'self-start' : 'self-end'
                  }`}
                >
                  <div
                    className={`p-3 rounded-lg ${
                      msg.isAi
                        ? 'bg-neutral-100'
                        : 'bg-[#ff3f17]/15 text-[#ff3f17]'
                    }`}
                  >
                    {msg.text}
                  </div>

                  {/* Copy button for AI messages */}
                  {msg.isAi && msg.text.trim() && (
                    <button
                      onClick={() => handleCopyMessage(msg.text, index)}
                      className="absolute top-2 right-2 opacity-0 group-hover:opacity-100 transition-opacity bg-white/80 hover:bg-white rounded-full p-1.5 shadow-sm border border-gray-200"
                      title="Copy message"
                    >
                      {copiedMessageIndex === index ? (
                        <Check className="w-3 h-3 text-green-600" />
                      ) : (
                        <Copy className="w-3 h-3 text-gray-600" />
                      )}
                    </button>
                  )}
                </div>
              ))}
              {isAiTyping && (
                <div className="p-3 rounded-lg bg-neutral-100 self-start">
                  AI is typing...
                </div>
              )}
            </div>
          </div>
        </div>

        {/* AI Input - Floating at bottom */}
        <div className="fixed bottom-6 left-0 right-0 px-4 z-20">
          <div className="max-w-4xl mx-auto">
            <div className="bg-white/80 backdrop-blur-sm rounded-3xl shadow-2xl border border-gray-200/50 p-2">
              <AiInput onSendMessage={handleMessage} />
            </div>
          </div>
        </div>
      </div>

      {/* Analytics Dashboard Modal */}
      <AnalyticsDashboard
        isOpen={showAnalytics}
        onClose={() => setShowAnalytics(false)}
      />
    </div>
  )
}

export default Page