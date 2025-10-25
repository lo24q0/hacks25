import React, { useState } from 'react';
import { Button, TextArea, Toast } from '@douyinfe/semi-ui';

interface TextInputProps {
  onGenerate: (text: string) => void;
  loading?: boolean;
}

const TextInput: React.FC<TextInputProps> = ({ onGenerate, loading = false }) => {
  const [text, setText] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (text.trim() && text.length >= 10) {
      onGenerate(text);
    } else {
      Toast.warning('描述长度应在 10-1000 字符之间');
    }
  };

  const isValid = text.trim().length >= 10 && text.trim().length <= 1000;

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <TextArea
          placeholder="请输入模型描述 (10-1000字符)..."
          value={text}
          onChange={(value) => setText(value)}
          rows={6}
          maxLength={1000}
          showClear
          validateStatus={text.length > 0 && !isValid ? 'error' : 'default'}
          style={{ width: '100%' }}
        />
        <div className="mt-2 text-sm text-gray-500 text-right">
          {text.length}/1000 字符
        </div>
        {text.length > 0 && !isValid && (
          <div className="mt-1 text-sm text-red-500">
            描述长度应在 10-1000 字符之间
          </div>
        )}
      </div>
      
      <Button
        htmlType="submit"
        type="primary"
        size="large"
        block
        disabled={!isValid || loading}
        loading={loading}
      >
        {loading ? '生成中...' : '生成 3D 模型'}
      </Button>
    </form>
  );
};

export default TextInput;
