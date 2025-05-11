import { Button } from "@/components/ui/button"
import Link from "next/link"
import { VideoBackground } from "@/components/video-background"

export default function Home() {
  return (
    <div className="flex min-h-screen flex-col">
      <header className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
        <div className="container flex h-14 items-center">
          <div className="mr-4 flex">
            <Link href="/" className="mr-6 flex items-center space-x-2">
              <span className="font-bold">RAG Chat</span>
            </Link>
          </div>
          <div className="flex flex-1 items-center justify-end space-x-4">
            <nav className="flex items-center space-x-2">
              <Link href="/login">
                <Button variant="outline">Login</Button>
              </Link>
              <Link href="/signup">
                <Button>Sign Up</Button>
              </Link>
            </nav>
          </div>
        </div>
      </header>
      <main className="flex-1">
        {/* Wrap both sections in the VideoBackground component */}
        <VideoBackground videoSrc="/videos/abstract-bg.mp4" overlayOpacity={0.7}>
          <div className="flex flex-col">
            {/* Hero Section */}
            <section className="w-full">
              <div className="container px-4 md:px-6 flex min-h-[calc(100vh-3.5rem)] items-center">
                <div className="grid gap-6 lg:grid-cols-[1fr_400px] lg:gap-12 xl:grid-cols-[1fr_600px]">
                  <div className="flex flex-col justify-center space-y-4">
                    <div className="space-y-2">
                      <h1 className="text-3xl font-bold tracking-tighter sm:text-5xl xl:text-6xl/none text-white">
                        Chat with Your Documents
                      </h1>
                      <p className="max-w-[600px] text-gray-200 md:text-xl">
                        Upload your documents and start chatting with them using our advanced RAG technology. Get
                        instant answers from your own knowledge base.
                      </p>
                    </div>
                    <div className="flex flex-col gap-2 min-[400px]:flex-row">
                      <Link href="/signup">
                        <Button size="lg" className="w-full">
                          Get Started
                        </Button>
                      </Link>
                      <Link href="/login">
                        <Button
                          size="lg"
                          variant="outline"
                          className="w-full bg-background/20 hover:bg-background/30 backdrop-blur-sm text-white border-white/30"
                        >
                          Login
                        </Button>
                      </Link>
                    </div>
                  </div>
                  <div className="flex items-center justify-center">
                    <div className="relative h-[450px] w-[450px] rounded-lg bg-gradient-to-r from-purple-500 to-indigo-500 p-1">
                      <div className="h-full w-full rounded-lg bg-white dark:bg-gray-950 p-6 flex flex-col">
                        <div className="flex items-center justify-between mb-4">
                          <div className="flex items-center space-x-2">
                            <div className="h-8 w-8 rounded-full bg-gradient-to-r from-purple-500 to-indigo-500"></div>
                            <div className="font-medium">RAG Assistant</div>
                          </div>
                          <div className="text-xs text-gray-500">Just now</div>
                        </div>
                        <div className="flex-1 space-y-4 overflow-auto">
                          <div className="rounded-lg bg-gray-100 dark:bg-gray-800 p-3 text-sm">
                            Hello! I'm your document assistant. Upload your files and I'll help you find information.
                          </div>
                          <div className="rounded-lg bg-purple-100 dark:bg-purple-900/20 p-3 text-sm ml-auto max-w-[80%]">
                            Can you summarize the quarterly report?
                          </div>
                          <div className="rounded-lg bg-gray-100 dark:bg-gray-800 p-3 text-sm">
                            Based on your quarterly report, revenue increased by 15% compared to last quarter, with the
                            new product line contributing to 30% of the growth. Expenses remained stable at 65% of
                            revenue.
                          </div>
                        </div>
                        <div className="mt-4 flex items-center gap-2">
                          <div className="relative flex-1 rounded-md border bg-background">
                            <input
                              className="w-full rounded-md bg-transparent px-3 py-2 text-sm"
                              placeholder="Type your message..."
                              disabled
                            />
                          </div>
                          <Button size="sm" disabled>
                            Send
                          </Button>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </section>

            {/* Features Section - Now with the same video background */}
            <section className="w-full py-12 md:py-24 lg:py-32">
              <div className="container px-4 md:px-6">
                <div className="flex flex-col items-center justify-center space-y-4 text-center">
                  <div className="space-y-2">
                    <h2 className="text-3xl font-bold tracking-tighter sm:text-5xl text-white">Features</h2>
                    <p className="max-w-[900px] text-gray-200 md:text-xl/relaxed lg:text-base/relaxed xl:text-xl/relaxed">
                      Our RAG Chat application provides powerful features to help you interact with your documents.
                    </p>
                  </div>
                </div>
                <div className="mx-auto grid max-w-5xl grid-cols-1 gap-6 py-12 md:grid-cols-3">
                  {/* Feature Card 1 */}
                  <div className="flex flex-col items-center space-y-2 rounded-lg border border-white/10 p-6 shadow-lg bg-white/10 backdrop-blur-sm">
                    <div className="rounded-full bg-purple-500/20 p-3">
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
                        className="h-6 w-6 text-purple-300"
                      >
                        <path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z" />
                        <polyline points="14 2 14 8 20 8" />
                      </svg>
                    </div>
                    <h3 className="text-xl font-bold text-white">Document Upload</h3>
                    <p className="text-sm text-gray-200 text-center">
                      Upload multiple document formats including PDFs, Word docs, and text files.
                    </p>
                  </div>

                  {/* Feature Card 2 */}
                  <div className="flex flex-col items-center space-y-2 rounded-lg border border-white/10 p-6 shadow-lg bg-white/10 backdrop-blur-sm">
                    <div className="rounded-full bg-purple-500/20 p-3">
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
                        className="h-6 w-6 text-purple-300"
                      >
                        <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
                      </svg>
                    </div>
                    <h3 className="text-xl font-bold text-white">Intelligent Chat</h3>
                    <p className="text-sm text-gray-200 text-center">
                      Ask questions about your documents and get accurate answers using RAG technology.
                    </p>
                  </div>

                  {/* Feature Card 3 */}
                  <div className="flex flex-col items-center space-y-2 rounded-lg border border-white/10 p-6 shadow-lg bg-white/10 backdrop-blur-sm">
                    <div className="rounded-full bg-purple-500/20 p-3">
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
                        className="h-6 w-6 text-purple-300"
                      >
                        <path d="M20 7h-3a2 2 0 0 1-2-2V2" />
                        <path d="M9 18a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h7l4 4v10a2 2 0 0 1-2 2Z" />
                        <path d="M3 7.6v12.8A1.6 1.6 0 0 0 4.6 22h9.8" />
                      </svg>
                    </div>
                    <h3 className="text-xl font-bold text-white">Chat History</h3>
                    <p className="text-sm text-gray-200 text-center">
                      Access all your previous conversations organized by project.
                    </p>
                  </div>
                </div>
              </div>
            </section>
          </div>
        </VideoBackground>
      </main>
      <footer className="border-t py-6 md:py-0">
        <div className="container flex flex-col items-center justify-between gap-4 md:h-16 md:flex-row">
          <p className="text-sm text-gray-500 dark:text-gray-400">
            © {new Date().getFullYear()} RAG Chat. All rights reserved.
          </p>
        </div>
      </footer>
    </div>
  )
}
