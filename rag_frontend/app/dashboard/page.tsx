import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { FileUp, MessageSquare, PlusCircle } from "lucide-react"
import Link from "next/link"

export default function DashboardPage() {
  return (
    <div className="container mx-auto p-6">
      <div className="grid gap-6">
        <div className="flex flex-col gap-2">
          <h1 className="text-3xl font-bold tracking-tight">Welcome to RAG Chat</h1>
          <p className="text-gray-500 dark:text-gray-400">
            Upload documents and start chatting with them using our advanced RAG technology.
          </p>
        </div>

        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between pb-2 space-y-0">
              <CardTitle className="text-sm font-medium">Upload Documents</CardTitle>
              <FileUp className="h-4 w-4 text-gray-500 dark:text-gray-400" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">Start a New Project</div>
              <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                Upload documents to create a new knowledge base
              </p>
              <Link href="/dashboard/upload">
                <Button className="w-full mt-4">
                  <PlusCircle className="mr-2 h-4 w-4" />
                  New Project
                </Button>
              </Link>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between pb-2 space-y-0">
              <CardTitle className="text-sm font-medium">Chat with Documents</CardTitle>
              <MessageSquare className="h-4 w-4 text-gray-500 dark:text-gray-400" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">Ask Questions</div>
              <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                Get instant answers from your uploaded documents
              </p>
              <div className="mt-4 text-center text-sm text-gray-500 dark:text-gray-400">
                Upload documents first to start chatting
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between pb-2 space-y-0">
              <CardTitle className="text-sm font-medium">How It Works</CardTitle>
              <svg
                xmlns="http://www.w3.org/2000/svg"
                width="24"
                height="24"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
                className="h-4 w-4 text-gray-500 dark:text-gray-400"
              >
                <circle cx="12" cy="12" r="10" />
                <path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3" />
                <path d="M12 17h.01" />
              </svg>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">RAG Technology</div>
              <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                Retrieval Augmented Generation for accurate answers
              </p>
              <ol className="mt-4 space-y-2 text-sm text-gray-500 dark:text-gray-400">
                <li className="flex items-center">
                  <span className="mr-2 flex h-6 w-6 items-center justify-center rounded-full bg-purple-100 text-purple-800 dark:bg-purple-900/20 dark:text-purple-400">
                    1
                  </span>
                  <span>Upload your documents (PDF, Word, Text)</span>
                </li>
                <li className="flex items-center">
                  <span className="mr-2 flex h-6 w-6 items-center justify-center rounded-full bg-purple-100 text-purple-800 dark:bg-purple-900/20 dark:text-purple-400">
                    2
                  </span>
                  <span>Our system processes and indexes your content</span>
                </li>
                <li className="flex items-center">
                  <span className="mr-2 flex h-6 w-6 items-center justify-center rounded-full bg-purple-100 text-purple-800 dark:bg-purple-900/20 dark:text-purple-400">
                    3
                  </span>
                  <span>Ask questions and get accurate answers</span>
                </li>
              </ol>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}
