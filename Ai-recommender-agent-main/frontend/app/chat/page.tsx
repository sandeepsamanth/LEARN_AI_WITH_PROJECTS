'use client'

import { useEffect, useState, useRef } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { MessageSquare, Send, Plus, Bot, User as UserIcon, ArrowLeft } from 'lucide-react'
import api from '@/lib/api'
import { getCurrentUser, User } from '@/lib/auth'
import LoadingPage from '@/app/components/LoadingPage'
import LoadingSpinner from '@/app/components/LoadingSpinner'

interface Message {
  id: string
  content: string
  role: 'user' | 'assistant'
  created_at: string
}

interface Conversation {
  id: string
  title: string
  created_at: string
}

export default function ChatPage() {
  const router = useRouter()
  const [user, setUser] = useState<User | null>(null)
  const [conversations, setConversations] = useState<Conversation[]>([])
  const [currentConversationId, setCurrentConversationId] = useState<string | null>(null)
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    loadUser()
  }, [])

  useEffect(() => {
    if (user) {
      loadConversations()
    }
  }, [user])

  useEffect(() => {
    if (currentConversationId) {
      loadMessages()
    }
  }, [currentConversationId])

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  const loadUser = async () => {
    try {
      const currentUser = await getCurrentUser()
      if (!currentUser) {
        router.push('/auth/login')
        return
      }
      setUser(currentUser)
    } catch (error) {
      router.push('/auth/login')
    }
  }

  const loadConversations = async () => {
    try {
      const response = await api.get('/api/chat/conversations')
      setConversations(response.data.conversations || [])
    } catch (error) {
      console.error('Error loading conversations:', error)
    }
  }

  const loadMessages = async () => {
    if (!currentConversationId) return
    try {
      const response = await api.get(`/api/chat/conversations/${currentConversationId}/messages`)
      setMessages(response.data.messages || [])
    } catch (error) {
      console.error('Error loading messages:', error)
    }
  }

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!input.trim() || loading) return

    const userMessage = input.trim()
    setInput('')
    setLoading(true)

    // Add user message to UI immediately
    const tempUserMessage: Message = {
      id: `temp-${Date.now()}`,
      content: userMessage,
      role: 'user',
      created_at: new Date().toISOString(),
    }
    setMessages(prev => [...prev, tempUserMessage])

    try {
      const response = await api.post('/api/chat/message', {
        content: userMessage,
        conversation_id: currentConversationId || null,
      })

      if (response.data && response.data.message) {
        const assistantMessage: Message = {
          id: response.data.message.id || `msg-${Date.now()}`,
          content: response.data.message.content,
          role: 'assistant',
          created_at: response.data.message.created_at || new Date().toISOString(),
        }

        setMessages(prev => {
          // Replace temp message with real one
          const filtered = prev.filter(m => m.id !== tempUserMessage.id)
          return [...filtered, assistantMessage]
        })

        if (response.data.conversation_id && response.data.conversation_id !== currentConversationId) {
          setCurrentConversationId(response.data.conversation_id)
          loadConversations()
        }
      } else {
        throw new Error('Invalid response from server')
      }
    } catch (error: any) {
      console.error('Error sending message:', error)
      // Remove temp message and show error
      setMessages(prev => prev.filter(m => m.id !== tempUserMessage.id))
      // Add error message
      const errorMessage: Message = {
        id: `error-${Date.now()}`,
        content: `Error: ${error.response?.data?.detail || error.message || 'Failed to send message. Please try again.'}`,
        role: 'assistant',
        created_at: new Date().toISOString(),
      }
      setMessages(prev => [...prev, errorMessage])
    } finally {
      setLoading(false)
    }
  }

  const startNewConversation = () => {
    setCurrentConversationId(null)
    setMessages([])
  }

  if (!user) {
    return <LoadingPage />
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 flex">
      {/* Sidebar */}
      <div className="w-64 bg-white shadow-lg border-r border-gray-200 flex flex-col">
        <div className="p-4 border-b border-gray-200 bg-gradient-to-r from-blue-600 to-purple-600">
          <Link 
            href="/dashboard" 
            className="flex items-center gap-2 text-white hover:text-blue-100 text-sm font-medium mb-3 transition"
          >
            <ArrowLeft className="w-4 h-4" />
            Back to Dashboard
          </Link>
          <h2 className="text-lg font-semibold text-white flex items-center gap-2">
            <MessageSquare className="w-5 h-5" />
            Conversations
          </h2>
        </div>
        <div className="p-4 flex-1 overflow-y-auto">
          <button
            onClick={startNewConversation}
            className="w-full px-4 py-3 bg-gradient-to-r from-blue-600 to-blue-700 text-white rounded-lg hover:from-blue-700 hover:to-blue-800 mb-4 font-medium shadow-md transition flex items-center justify-center gap-2"
          >
            <Plus className="w-5 h-5" />
            New Conversation
          </button>
          <div className="space-y-2">
            {conversations.length === 0 ? (
              <p className="text-sm text-gray-500 text-center py-4">No conversations yet</p>
            ) : (
              conversations.map((conv) => (
                <button
                  key={conv.id}
                  onClick={() => setCurrentConversationId(conv.id)}
                  className={`w-full text-left px-4 py-3 rounded-lg transition ${
                    currentConversationId === conv.id
                      ? 'bg-blue-50 text-blue-700 border-2 border-blue-200'
                      : 'hover:bg-gray-50 border border-transparent'
                  }`}
                >
                  <div className="font-medium truncate flex items-center gap-2">
                    <MessageSquare className="w-4 h-4" />
                    {conv.title}
                  </div>
                  <div className="text-xs text-gray-500 mt-1">
                    {new Date(conv.created_at).toLocaleDateString()}
                  </div>
                </button>
              ))
            )}
          </div>
        </div>
      </div>

      {/* Chat Area */}
      <div className="flex-1 flex flex-col">
        <header className="bg-white shadow-sm p-4 border-b border-gray-200">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
              <Bot className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                Career Advisor
              </h1>
              <p className="text-xs text-gray-500">AI-powered career guidance</p>
            </div>
          </div>
        </header>

        <div className="flex-1 overflow-y-auto p-6 space-y-4 bg-gradient-to-b from-white to-gray-50">
          {messages.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-full text-center">
              <div className="w-20 h-20 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center mb-4">
                <Bot className="w-10 h-10 text-white" />
              </div>
              <h2 className="text-2xl font-semibold text-gray-900 mb-2">Start a conversation</h2>
              <p className="text-gray-600 max-w-md">
                Ask me anything about your career, job search, or skill development!
              </p>
            </div>
          ) : (
            messages.map((message) => (
              <div
                key={message.id}
                className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'} items-start gap-3`}
              >
                {message.role === 'assistant' && (
                  <div className="w-8 h-8 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center flex-shrink-0">
                    <Bot className="w-5 h-5 text-white" />
                  </div>
                )}
                <div
                  className={`max-w-2xl px-4 py-3 rounded-xl shadow-sm ${
                    message.role === 'user'
                      ? 'bg-gradient-to-r from-blue-600 to-blue-700 text-white'
                      : 'bg-white text-gray-900 border border-gray-200'
                  }`}
                >
                  <p className="whitespace-pre-wrap leading-relaxed">{message.content}</p>
                </div>
                {message.role === 'user' && (
                  <div className="w-8 h-8 bg-gray-200 rounded-full flex items-center justify-center flex-shrink-0">
                    <UserIcon className="w-5 h-5 text-gray-600" />
                  </div>
                )}
              </div>
            ))
          )}
          {loading && (
            <div className="flex justify-start items-start gap-3">
              <div className="w-8 h-8 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center">
                <Bot className="w-5 h-5 text-white" />
              </div>
              <div className="bg-white px-4 py-3 rounded-xl shadow-sm border border-gray-200">
                <div className="flex items-center gap-2 text-gray-500">
                  <LoadingSpinner size="sm" />
                  <span>Thinking...</span>
                </div>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        <form onSubmit={handleSendMessage} className="bg-white border-t border-gray-200 p-4 shadow-lg">
          <div className="flex gap-3 max-w-4xl mx-auto">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask about careers, jobs, skills..."
              className="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-gray-900 bg-white"
              disabled={loading}
            />
            <button
              type="submit"
              disabled={loading || !input.trim()}
              className="px-6 py-3 bg-gradient-to-r from-blue-600 to-blue-700 text-white rounded-lg hover:from-blue-700 hover:to-blue-800 disabled:opacity-50 font-medium shadow-md transition flex items-center gap-2"
            >
              <Send className="w-5 h-5" />
              Send
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

