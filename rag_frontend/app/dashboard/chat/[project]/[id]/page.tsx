"use client"

import type React from "react"

import { useState, useRef, useEffect } from "react"
import { useParams, useRouter } from "next/navigation"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { useToast } from "@/components/ui/use-toast"
import { Send, Loader2, Bot, User } from "lucide-react"
import { API_URL } from "@/lib/config"
import ReactMarkdown from "react-markdown"
import remarkGfm from "remark-gfm"

interface Message {
  id: string
  role: "user" | "assistant"
  content: string
  timestamp: string
}

interface ChatHistoryItem {
  user_query: string
  chatbot_answer: string
}

interface ChatData {
  project_name: string
  vector_id: string
  chat_history: ChatHistoryItem[]
  timestamp: string
}

export default function ChatDetailPage() {
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState("")
  const [isLoading, setIsLoading] = useState(false)
  const [isInitialLoading, setIsInitialLoading] = useState(true)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const { project, id } = useParams()
  const router = useRouter()
  const { toast } = useToast()

  useEffect(() => {
    // Fetch chat history
    const fetchChatHistory = async () => {
      try {
        const token = localStorage.getItem("token")
        if (!token) {
          router.push("/login")
          return
        }

        // First try to get the specific chat by vector_id
        const response = await fetch(`${API_URL}/get_chats`, {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        })

        if (!response.ok) {
          throw new Error("Failed to fetch chat history")
        }

        const data = await response.json()
        console.log("Fetched chats data:", data)

        // Find the specific chat with the matching vector_id
        let chatData: ChatData | undefined

        if (data.chats && Array.isArray(data.chats)) {
          chatData = data.chats.find((chat: ChatData) => chat.vector_id === id)
        }

        if (!chatData) {
          // If not found, add welcome message
          setMessages([
            {
              id: "welcome",
              role: "assistant",
              content: `Welcome to the ${project} project! Ask me anything about your documents.`,
              timestamp: new Date().toISOString(),
            },
          ])
          return
        }

        // Convert chat_history to messages format
        const convertedMessages: Message[] = []

        // Process each item in chat_history to create user and assistant messages
        chatData.chat_history.forEach((item, index) => {
          // Add user message
          convertedMessages.push({
            id: `user-${index}`,
            role: "user",
            content: item.user_query,
            timestamp: new Date(chatData?.timestamp || Date.now()).toISOString(),
          })

          // Add assistant message
          convertedMessages.push({
            id: `assistant-${index}`,
            role: "assistant",
            content: item.chatbot_answer,
            timestamp: new Date(chatData?.timestamp || Date.now()).toISOString(),
          })
        })

        if (convertedMessages.length > 0) {
          setMessages(convertedMessages)
        } else {
          // No messages, add welcome message
          setMessages([
            {
              id: "welcome",
              role: "assistant",
              content: `Welcome to the ${project} project! Ask me anything about your documents.`,
              timestamp: new Date().toISOString(),
            },
          ])
        }
      } catch (error) {
        console.error("Error fetching chat history:", error)
        toast({
          title: "Error",
          description: "Failed to load chat history",
          variant: "destructive",
        })

        // Add fallback welcome message
        setMessages([
          {
            id: "welcome",
            role: "assistant",
            content: `Welcome to the ${project} project! Ask me anything about your documents.`,
            timestamp: new Date().toISOString(),
          },
        ])
      } finally {
        setIsInitialLoading(false)
      }
    }

    fetchChatHistory()
  }, [project, id, router, toast])

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    if (!input.trim()) return

    const userMessage: Message = {
      id: Date.now().toString(),
      role: "user",
      content: input,
      timestamp: new Date().toISOString(),
    }

    setMessages((prev) => [...prev, userMessage])
    setInput("")
    setIsLoading(true)

    try {
      const token = localStorage.getItem("token")
      if (!token) {
        router.push("/login")
        return
      }

      const formData = new FormData()
      formData.append("user_query", input)
      formData.append("project_name", project as string)
      // Also send the vector_id to continue the conversation
      formData.append("vector_id", id as string)

      const response = await fetch(`${API_URL}/chat`, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
        },
        body: formData,
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || "Failed to get response")
      }

      const data = await response.json()
      console.log("Backend response:", data)

      // Check different possible response formats
      let responseText = "I couldn't find an answer to that question."

      if (data.chatbot_answer) {
        responseText = data.chatbot_answer
      } else if (data.response) {
        responseText = data.response
      } else if (data.answer) {
        responseText = data.answer
      } else if (data.text) {
        responseText = data.text
      } else if (typeof data === "string") {
        responseText = data
      }

      const assistantMessage: Message = {
        id: Date.now().toString(),
        role: "assistant",
        content: responseText,
        timestamp: new Date().toISOString(),
      }

      setMessages((prev) => [...prev, assistantMessage])
    } catch (error) {
      toast({
        title: "Error",
        description: error instanceof Error ? error.message : "Failed to get a response",
        variant: "destructive",
      })

      const errorMessage: Message = {
        id: Date.now().toString(),
        role: "assistant",
        content: "Sorry, I encountered an error processing your request.",
        timestamp: new Date().toISOString(),
      }

      setMessages((prev) => [...prev, errorMessage])
    } finally {
      setIsLoading(false)
    }
  }

  if (isInitialLoading) {
    return (
      <div className="flex h-[calc(100vh-3.5rem)] items-center justify-center">
        <div className="flex flex-col items-center space-y-4">
          <Loader2 className="h-8 w-8 animate-spin text-purple-500" />
          <p className="text-sm text-gray-500">Loading chat history...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="flex flex-col h-[calc(100vh-3.5rem)]">
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((message) => (
          <div key={message.id} className={`flex ${message.role === "user" ? "justify-end" : "justify-start"}`}>
            <div
              className={`flex max-w-[80%] items-start space-x-2 ${
                message.role === "user" ? "flex-row-reverse space-x-reverse" : ""
              }`}
            >
              <div
                className={`flex h-8 w-8 items-center justify-center rounded-full ${
                  message.role === "assistant"
                    ? "bg-purple-100 text-purple-500 dark:bg-purple-900/20 dark:text-purple-400"
                    : "bg-gray-100 text-gray-600 dark:bg-gray-800 dark:text-gray-400"
                }`}
              >
                {message.role === "assistant" ? <Bot className="h-5 w-5" /> : <User className="h-5 w-5" />}
              </div>
              <div
                className={`rounded-lg px-4 py-2 ${
                  message.role === "assistant"
                    ? "bg-gray-100 text-gray-900 dark:bg-gray-800 dark:text-gray-100"
                    : "bg-purple-500 text-white dark:bg-purple-600"
                }`}
              >
                {message.role === "assistant" ? (
                  <div className="markdown-content">
                    <ReactMarkdown
                      remarkPlugins={[remarkGfm]}
                      components={{
                        h1: ({ node, ...props }) => <h1 className="text-xl font-bold my-2" {...props} />,
                        h2: ({ node, ...props }) => <h2 className="text-lg font-bold my-2" {...props} />,
                        h3: ({ node, ...props }) => <h3 className="text-md font-bold my-2" {...props} />,
                        p: ({ node, ...props }) => <p className="my-1" {...props} />,
                        ul: ({ node, ...props }) => <ul className="list-disc pl-5 my-2" {...props} />,
                        ol: ({ node, ...props }) => <ol className="list-decimal pl-5 my-2" {...props} />,
                        li: ({ node, ...props }) => <li className="my-1" {...props} />,
                        a: ({ node, ...props }) => <a className="text-blue-500 hover:underline" {...props} />,
                        code: ({ node, inline, ...props }) =>
                          inline ? (
                            <code className="bg-gray-200 dark:bg-gray-700 px-1 py-0.5 rounded text-sm" {...props} />
                          ) : (
                            <code
                              className="block bg-gray-200 dark:bg-gray-700 p-2 rounded text-sm my-2 overflow-x-auto"
                              {...props}
                            />
                          ),
                        pre: ({ node, ...props }) => <pre className="my-2 overflow-x-auto" {...props} />,
                        blockquote: ({ node, ...props }) => (
                          <blockquote
                            className="border-l-4 border-gray-300 dark:border-gray-600 pl-4 my-2 italic"
                            {...props}
                          />
                        ),
                        strong: ({ node, ...props }) => <strong className="font-bold" {...props} />,
                        em: ({ node, ...props }) => <em className="italic" {...props} />,
                      }}
                    >
                      {message.content}
                    </ReactMarkdown>
                  </div>
                ) : (
                  message.content
                )}
              </div>
            </div>
          </div>
        ))}
        {isLoading && (
          <div className="flex justify-start">
            <div className="flex max-w-[80%] items-start space-x-2">
              <div className="flex h-8 w-8 items-center justify-center rounded-full bg-purple-100 text-purple-500 dark:bg-purple-900/20 dark:text-purple-400">
                <Bot className="h-5 w-5" />
              </div>
              <div className="rounded-lg bg-gray-100 px-4 py-2 dark:bg-gray-800">
                <Loader2 className="h-5 w-5 animate-spin text-gray-500" />
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>
      <div className="border-t p-4">
        <form onSubmit={handleSubmit} className="flex space-x-2">
          <Input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask a question about your documents..."
            className="flex-1"
            disabled={isLoading}
          />
          <Button type="submit" disabled={isLoading || !input.trim()}>
            {isLoading ? <Loader2 className="h-4 w-4 animate-spin" /> : <Send className="h-4 w-4" />}
            <span className="sr-only">Send</span>
          </Button>
        </form>
      </div>
    </div>
  )
}
