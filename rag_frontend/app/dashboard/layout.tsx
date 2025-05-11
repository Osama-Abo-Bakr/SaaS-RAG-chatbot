"use client"

import type React from "react"

import { useEffect, useState } from "react"
import { useRouter } from "next/navigation"
import {
  SidebarProvider,
  Sidebar,
  SidebarContent,
  SidebarHeader,
  SidebarFooter,
  SidebarMenu,
  SidebarMenuItem,
  SidebarMenuButton,
  SidebarTrigger,
} from "@/components/ui/sidebar"
import { Button } from "@/components/ui/button"
import { PlusCircle, LogOut, MessageSquare, User } from "lucide-react"
import { useToast } from "@/components/ui/use-toast"
import { API_URL } from "@/lib/config"

// First, update the Chat interface to match your API response structure
interface Chat {
  id?: string | number
  project_name: string
  vector_id: string
  chat_history: Array<{
    user_query: string
    chatbot_answer: string
  }>
  timestamp: string
  last_message?: string
  [key: string]: any // Allow for other properties
}

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode
}) {
  const router = useRouter()
  const { toast } = useToast()
  const [chats, setChats] = useState<Chat[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const token = localStorage.getItem("token")

    if (!token) {
      router.push("/login")
      return
    }

    // Then, update the fetchChats function to correctly process the response
    const fetchChats = async () => {
      try {
        console.log("Fetching chats from:", `${API_URL}/get_chats`)

        const response = await fetch(`${API_URL}/get_chats`, {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        })

        console.log("Chat response status:", response.status)

        if (!response.ok) {
          if (response.status === 401) {
            localStorage.removeItem("token")
            router.push("/login")
            return
          }
          throw new Error(`Failed to fetch chats: ${response.status}`)
        }

        const data = await response.json()
        console.log("Parsed data:", data)

        // Handle the specific response format from your API
        let chatsList: Chat[] = []

        if (data.chats && Array.isArray(data.chats)) {
          chatsList = data.chats
        } else if (Array.isArray(data)) {
          chatsList = data
        }

        console.log("Processed chats list:", chatsList)

        // Normalize the chat objects to ensure they have the required properties
        const normalizedChats = chatsList.map((chat) => {
          // Use vector_id as the id if no id is present
          const chatId = chat.id || chat.vector_id || `chat-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`

          // Get the last message from chat_history if available
          let lastMessage = "New conversation"
          if (chat.chat_history && chat.chat_history.length > 0) {
            // Use the most recent message (which is the first in the array)
            lastMessage = chat.chat_history[0].user_query || "New conversation"
          }

          return {
            ...chat,
            id: chatId,
            last_message: lastMessage,
          }
        })

        console.log("Normalized chats:", normalizedChats)
        setChats(normalizedChats)

        // If we got no chats but the request was successful, create a default chat
        if (normalizedChats.length === 0) {
          // Create a default chat for the current project if we're in a project
          const pathParts = window.location.pathname.split("/")
          const projectIndex = pathParts.indexOf("chat")

          if (projectIndex !== -1 && pathParts.length > projectIndex + 1) {
            const currentProject = pathParts[projectIndex + 1]
            setChats([
              {
                id: "default",
                project_name: currentProject,
                vector_id: "default",
                chat_history: [],
                timestamp: new Date().toISOString(),
                last_message: "New conversation",
              },
            ])
          }
        }
      } catch (error) {
        console.error("Error fetching chats:", error)
        setError(error instanceof Error ? error.message : "Unknown error")
        toast({
          title: "Error",
          description: `Failed to load chat history: ${error instanceof Error ? error.message : "Unknown error"}`,
          variant: "destructive",
        })

        // Create a default chat for the current project if we're in a project
        const pathParts = window.location.pathname.split("/")
        const projectIndex = pathParts.indexOf("chat")

        if (projectIndex !== -1 && pathParts.length > projectIndex + 1) {
          const currentProject = pathParts[projectIndex + 1]
          setChats([
            {
              id: "default",
              project_name: currentProject,
              vector_id: "default",
              chat_history: [],
              timestamp: new Date().toISOString(),
              last_message: "New conversation",
            },
          ])
        }
      } finally {
        setIsLoading(false)
      }
    }

    fetchChats()
  }, [router, toast])

  const handleLogout = () => {
    localStorage.removeItem("token")
    router.push("/login")
    toast({
      title: "Logged out",
      description: "You've been logged out successfully.",
    })
  }

  // Group chats by project name
  const chatsByProject = chats.reduce(
    (acc, chat) => {
      const projectName = chat.project_name || "Default Project"
      if (!acc[projectName]) {
        acc[projectName] = []
      }
      acc[projectName].push(chat)
      return acc
    },
    {} as Record<string, Chat[]>,
  )

  return (
    <SidebarProvider>
      <div className="flex min-h-screen">
        <Sidebar>
          <SidebarHeader className="border-b px-4 py-2">
            <div className="flex items-center justify-between">
              <h2 className="text-lg font-semibold">RAG Chat</h2>
              <SidebarTrigger />
            </div>
          </SidebarHeader>
          <SidebarContent>
            <div className="px-4 py-2">
              <Button
                variant="outline"
                className="w-full justify-start gap-2"
                onClick={() => router.push("/dashboard/upload")}
              >
                <PlusCircle size={16} />
                New Project
              </Button>
            </div>

            {isLoading ? (
              <div className="p-4">
                <div className="h-4 w-3/4 bg-gray-200 dark:bg-gray-700 rounded animate-pulse mb-2"></div>
                <div className="h-4 w-1/2 bg-gray-200 dark:bg-gray-700 rounded animate-pulse mb-2"></div>
                <div className="h-4 w-2/3 bg-gray-200 dark:bg-gray-700 rounded animate-pulse"></div>
              </div>
            ) : error ? (
              <div className="p-4 text-sm text-red-500">
                <p>Error loading chats: {error}</p>
                <Button variant="outline" size="sm" className="mt-2" onClick={() => window.location.reload()}>
                  Retry
                </Button>
              </div>
            ) : Object.keys(chatsByProject).length === 0 ? (
              <div className="p-4 text-sm text-gray-500 dark:text-gray-400">
                <p>No chats found. Upload documents to start chatting.</p>
              </div>
            ) : (
              <SidebarMenu>
                {Object.entries(chatsByProject).map(([projectName, projectChats]) => (
                  <div key={projectName} className="mb-4">
                    <div className="px-4 py-1 text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase">
                      {projectName}
                    </div>
                    {projectChats.map((chat, index) => (
                      <SidebarMenuItem key={`${projectName}-${chat.vector_id || index}`}>
                        <SidebarMenuButton
                          onClick={() => router.push(`/dashboard/chat/${projectName}/${chat.vector_id}`)}
                          className="flex items-center gap-2"
                        >
                          <MessageSquare size={16} />
                          <span className="truncate">
                            {chat.last_message && chat.last_message.length > 30
                              ? chat.last_message.substring(0, 30) + "..."
                              : chat.last_message || "New Chat"}
                          </span>
                        </SidebarMenuButton>
                      </SidebarMenuItem>
                    ))}
                  </div>
                ))}
              </SidebarMenu>
            )}
          </SidebarContent>
          <SidebarFooter className="border-t p-4">
            <Button variant="ghost" className="w-full justify-start gap-2" onClick={handleLogout}>
              <LogOut size={16} />
              Logout
            </Button>
          </SidebarFooter>
        </Sidebar>
        <div className="flex-1 overflow-auto">
          <header className="sticky top-0 z-10 flex h-14 items-center gap-4 border-b bg-background px-4 sm:px-6">
            <SidebarTrigger />
            <div className="flex-1">
              <h1 className="text-lg font-semibold">Dashboard</h1>
            </div>
            <Button variant="ghost" size="icon" className="rounded-full">
              <User size={20} />
              <span className="sr-only">User menu</span>
            </Button>
          </header>
          <main className="flex-1">{children}</main>
        </div>
      </div>
    </SidebarProvider>
  )
}
