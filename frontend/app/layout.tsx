import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'OmniTrace AI - OSINT & Behavioral Analytics',
  description: 'Next-gen OSINT platform powered by Gemini AI',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  )
}
