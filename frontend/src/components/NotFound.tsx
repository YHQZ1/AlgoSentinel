import { AlertCircle } from 'lucide-react'

export default function NotFound() {
  return (
    <div className="min-h-screen flex items-center justify-center p-4">
      <div className="text-center">
        <AlertCircle className="w-16 h-16 text-neon-red mx-auto mb-4" />
        <h1 className="text-4xl font-bold text-neon-blue mb-2">404</h1>
        <p className="text-slate-400 mb-6">Page not found</p>
        <a
          href="/"
          className="px-6 py-2 bg-gradient-to-r from-neon-blue to-neon-purple rounded-lg text-slate-900 font-bold hover:shadow-lg transition-all"
        >
          Back to Dashboard
        </a>
      </div>
    </div>
  )
}
