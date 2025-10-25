import React from 'react'

export interface LoadingProps {
  size?: 'sm' | 'md' | 'lg' | 'xl'
  text?: string
  fullScreen?: boolean
  variant?: 'spinner' | 'dots' | 'pulse'
}

const Loading: React.FC<LoadingProps> = ({
  size = 'md',
  text,
  fullScreen = false,
  variant = 'spinner',
}) => {
  const sizeMap = {
    sm: 'h-4 w-4',
    md: 'h-8 w-8',
    lg: 'h-12 w-12',
    xl: 'h-16 w-16',
  }

  const containerClass = fullScreen
    ? 'fixed inset-0 flex items-center justify-center bg-white bg-opacity-75 z-50'
    : 'flex items-center justify-center'

  const renderSpinner = () => (
    <svg
      className={`animate-spin ${sizeMap[size]} text-blue-600`}
      xmlns="http://www.w3.org/2000/svg"
      fill="none"
      viewBox="0 0 24 24"
    >
      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
      <path
        className="opacity-75"
        fill="currentColor"
        d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
      />
    </svg>
  )

  const renderDots = () => {
    const dotSize =
      size === 'sm' ? 'h-2 w-2' : size === 'md' ? 'h-3 w-3' : size === 'lg' ? 'h-4 w-4' : 'h-5 w-5'

    return (
      <div className="flex space-x-2">
        <div
          className={`${dotSize} bg-blue-600 rounded-full animate-bounce`}
          style={{ animationDelay: '0s' }}
        />
        <div
          className={`${dotSize} bg-blue-600 rounded-full animate-bounce`}
          style={{ animationDelay: '0.1s' }}
        />
        <div
          className={`${dotSize} bg-blue-600 rounded-full animate-bounce`}
          style={{ animationDelay: '0.2s' }}
        />
      </div>
    )
  }

  const renderPulse = () => (
    <div className={`${sizeMap[size]} bg-blue-600 rounded-full animate-pulse`} />
  )

  const renderLoader = () => {
    switch (variant) {
      case 'dots':
        return renderDots()
      case 'pulse':
        return renderPulse()
      case 'spinner':
      default:
        return renderSpinner()
    }
  }

  return (
    <div className={containerClass}>
      <div className="flex flex-col items-center space-y-3">
        {renderLoader()}
        {text && <p className="text-sm text-gray-600 font-medium">{text}</p>}
      </div>
    </div>
  )
}

export default Loading
