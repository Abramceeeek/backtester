import { useRouter } from 'next/router'
import { useEffect } from 'react'

export default function Home() {
  const router = useRouter()

  useEffect(() => {
    // Redirect to backtest page
    router.push('/backtest')
  }, [router])

  return (
    <div className="min-h-screen flex items-center justify-center">
      <p>Redirecting to backtester...</p>
    </div>
  )
}
