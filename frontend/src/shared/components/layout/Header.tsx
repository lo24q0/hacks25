export default function Header() {
  return (
    <header className="bg-white shadow-sm">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center py-4">
          <div className="flex items-center">
            <h1 className="text-2xl font-bold text-gray-900">3D模型打印平台</h1>
          </div>
          <nav className="flex space-x-4">
            <a href="/" className="text-gray-700 hover:text-gray-900">
              模型生成
            </a>
          </nav>
        </div>
      </div>
    </header>
  )
}
