import React, { useState } from 'react'
import { Button, Input } from '@/shared/components/ui'

interface TextInputProps {
  onGenerate: (text: string) => void
  loading?: boolean
}

const TextInput: React.FC<TextInputProps> = ({ onGenerate, loading = false }) => {
  const [text, setText] = useState('')

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (text.trim() && text.length >= 10) {
      onGenerate(text)
    }
  }

  const isValid = text.trim().length >= 10 && text.trim().length <= 1000

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <Input
        label="模型描述"
        placeholder="请输入模型描述 (10-1000字符)..."
        value={text}
        onChange={(e) => setText(e.target.value)}
        fullWidth
        helperText={`${text.length}/1000 字符`}
        error={text.length > 0 && !isValid ? '描述长度应在 10-1000 字符之间' : undefined}
      />

      <Button
        type="submit"
        variant="primary"
        size="lg"
        fullWidth
        disabled={!isValid || loading}
        loading={loading}
      >
        {loading ? '生成中...' : '生成 3D 模型'}
      </Button>
    </form>
  )
}

export default TextInput
