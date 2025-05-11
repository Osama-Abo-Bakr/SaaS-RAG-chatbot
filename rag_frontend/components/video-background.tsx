"use client"

import type React from "react"

import { useEffect, useRef, useState } from "react"

interface VideoBackgroundProps {
  videoSrc: string
  fallbackImageSrc?: string
  overlayOpacity?: number
  children?: React.ReactNode
}

export function VideoBackground({
  videoSrc,
  fallbackImageSrc = "/placeholder.svg?height=1080&width=1920",
  overlayOpacity = 0.5,
  children,
}: VideoBackgroundProps) {
  const videoRef = useRef<HTMLVideoElement>(null)
  const [isVideoLoaded, setIsVideoLoaded] = useState(false)

  useEffect(() => {
    const video = videoRef.current
    if (!video) return

    const handleCanPlay = () => {
      setIsVideoLoaded(true)
    }

    video.addEventListener("canplay", handleCanPlay)

    // Check if video is already loaded
    if (video.readyState >= 3) {
      setIsVideoLoaded(true)
    }

    return () => {
      video.removeEventListener("canplay", handleCanPlay)
    }
  }, [])

  return (
    <div className="relative w-full h-full overflow-hidden">
      {/* Fallback image shown until video loads */}
      {!isVideoLoaded && (
        <div
          className="absolute inset-0 bg-cover bg-center z-0"
          style={{ backgroundImage: `url(${fallbackImageSrc})` }}
        />
      )}

      {/* Video background */}
      <video
        ref={videoRef}
        autoPlay
        muted
        loop
        playsInline
        className={`absolute inset-0 w-full h-full object-cover z-0 transition-opacity duration-1000 ${
          isVideoLoaded ? "opacity-100" : "opacity-0"
        }`}
      >
        <source src={videoSrc} type="video/mp4" />
        Your browser does not support the video tag.
      </video>

      {/* Dark overlay to improve text readability */}
      <div className="absolute inset-0 bg-black z-10" style={{ opacity: overlayOpacity }} />

      {/* Content */}
      <div className="relative z-20 h-full">{children}</div>
    </div>
  )
}
