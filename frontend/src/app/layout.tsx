import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'Arc Workbench',
  description: 'Interactive Debugging Companion for ARC-Eval',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className={`${inter.className} bg-arc-gray-extralight text-arc-gray-dark`}>
        {/* Basic overall page structure */}
        <div className="min-h-screen flex flex-col">
          {/* Header placeholder - can be a component later */}
          <header className="bg-white shadow-sm p-4">
            <h1 className="text-2xl font-bold text-arc-blue">Arc Workbench</h1>
          </header>

          {/* Main content area */}
          <main className="flex-grow container mx-auto p-4">
            {children}
          </main>

          {/* Footer placeholder */}
          <footer className="text-center p-4 text-sm text-arc-gray">
            © {new Date().getFullYear()} ARC-Eval
          </footer>
        </div>
      </body>
    </html>
  )
}
