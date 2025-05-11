// API URL configuration
export const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"

// Check if we're running in a browser environment
export const isBrowser = typeof window !== "undefined"

// Check if we're in a preview environment (Vercel preview, etc.)
export const isPreviewEnvironment = () => {
  if (!isBrowser) return false

  // Check for Vercel preview
  const isVercelPreview =
    window.location.hostname.includes("vercel.app") ||
    window.location.hostname.includes("localhost") ||
    window.location.hostname.includes("127.0.0.1")

  return isVercelPreview
}

// Function to check if the API is reachable
export async function isApiReachable() {
  if (!isBrowser) return false

  // If we're in a preview environment, don't even try to reach the API
  // as it will likely fail and cause console errors
  if (isPreviewEnvironment()) {
    return false
  }

  try {
    const controller = new AbortController()
    const timeoutId = setTimeout(() => controller.abort(), 3000) // Shorter timeout

    const response = await fetch(`${API_URL}`, {
      method: "GET",
      signal: controller.signal,
      // Prevent caching
      headers: {
        "Cache-Control": "no-cache, no-store, must-revalidate",
        Pragma: "no-cache",
        Expires: "0",
      },
    })

    clearTimeout(timeoutId)
    return response.ok
  } catch (error) {
    // Suppress the error log in preview environments
    if (!isPreviewEnvironment()) {
      console.warn("API not reachable:", API_URL)
    }
    return false
  }
}

// Get demo data for preview environments
export const getDemoChats = () => [
  {
    id: "demo-1",
    project_name: "Annual Report 2023",
    last_message: "What were the key financial highlights?",
  },
  {
    id: "demo-2",
    project_name: "Product Documentation",
    last_message: "How do I implement the API?",
  },
  {
    id: "demo-3",
    project_name: "Research Papers",
    last_message: "Summarize the findings on renewable energy",
  },
]
