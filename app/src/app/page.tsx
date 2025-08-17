export default function Home() {
  return (
    <main className="min-h-screen bg-gray-50">
      <div className="container mx-auto px-4 py-8">
        <header className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">
            StopOdds
          </h1>
          <p className="text-lg text-gray-600">
            Estimate your chances of being stopped on Melbourne public transport — from commuter-reported data
          </p>
        </header>
        
        <div className="max-w-2xl mx-auto">
          <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
            <h2 className="text-xl font-semibold mb-4">Coming Soon</h2>
            <p className="text-gray-600">
              StopOdds is currently in development. We're building a transparent, 
              privacy-first platform to help understand fare inspection patterns 
              on Melbourne public transport.
            </p>
          </div>
        </div>
      </div>
    </main>
  )
}