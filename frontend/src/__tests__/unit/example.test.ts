import { describe, it, expect } from 'vitest'

describe('Example Test', () => {
  it('should pass basic assertion', () => {
    expect(1 + 1).toBe(2)
  })

  it('should handle string operations', () => {
    const greeting = 'Hello World'
    expect(greeting).toBe('Hello World')
    expect(greeting).toContain('World')
  })
})
