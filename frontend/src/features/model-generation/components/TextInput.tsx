import React, { useState } from 'react';
import { Button, Input } from '@/shared/components/ui';

interface TextInputProps {
  onGenerate: (text: string) => void;
  loading?: boolean;
}

const MIN_LENGTH = 10;
const MAX_LENGTH = 1000;

const TextInput: React.FC<TextInputProps> = ({ onGenerate, loading = false }) => {
  const [text, setText] = useState('');
  const [showTips, setShowTips] = useState(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const trimmedText = text.trim();
    if (trimmedText.length >= MIN_LENGTH && trimmedText.length <= MAX_LENGTH) {
      onGenerate(trimmedText);
      setText('');
    }
  };

  const isValid = text.trim().length >= MIN_LENGTH && text.trim().length <= MAX_LENGTH;
  const charCount = text.length;
  const trimmedLength = text.trim().length;

  const getHelperText = () => {
    if (charCount === 0) {
      return `请输入 ${MIN_LENGTH}-${MAX_LENGTH} 字符`;
    }
    if (trimmedLength < MIN_LENGTH) {
      return `还需 ${MIN_LENGTH - trimmedLength} 字符 (当前 ${trimmedLength}/${MAX_LENGTH})`;
    }
    if (trimmedLength > MAX_LENGTH) {
      return `超出 ${trimmedLength - MAX_LENGTH} 字符 (${trimmedLength}/${MAX_LENGTH})`;
    }
    return `${trimmedLength}/${MAX_LENGTH} 字符`;
  };

  const getErrorMessage = () => {
    if (charCount === 0) return undefined;
    if (trimmedLength < MIN_LENGTH) {
      return `描述长度不足,至少需要 ${MIN_LENGTH} 字符`;
    }
    if (trimmedLength > MAX_LENGTH) {
      return `描述长度超限,最多 ${MAX_LENGTH} 字符`;
    }
    return undefined;
  };

  const examplePrompts = [
    '一个圆形的咖啡杯,表面有简单的花纹装饰',
    '方形的收纳盒,顶部有盖子',
    '可爱的小猫雕像,坐姿,尾巴卷起',
    '简约风格的花瓶,底部宽,顶部窄',
  ];

  const fillExample = (example: string) => {
    setText(example);
    setShowTips(false);
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <Input
          label="模型描述"
          placeholder="例如: 一个圆形的杯子..."
          value={text}
          onChange={(e) => setText(e.target.value)}
          onFocus={() => setShowTips(true)}
          fullWidth
          helperText={getHelperText()}
          error={getErrorMessage()}
        />
        
        {showTips && (
          <div className="mt-2 p-3 bg-blue-50 border border-blue-200 rounded-lg">
            <div className="flex justify-between items-start mb-2">
              <p className="text-sm font-medium text-blue-900">描述示例</p>
              <button
                type="button"
                onClick={() => setShowTips(false)}
                className="text-blue-600 hover:text-blue-800"
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
            <div className="space-y-1">
              {examplePrompts.map((example, index) => (
                <button
                  key={index}
                  type="button"
                  onClick={() => fillExample(example)}
                  className="w-full text-left text-sm text-blue-700 hover:text-blue-900 hover:bg-blue-100 p-2 rounded transition-colors"
                >
                  {example}
                </button>
              ))}
            </div>
            <p className="text-xs text-blue-600 mt-2">
              💡 提示: 描述越详细,生成的模型越准确
            </p>
          </div>
        )}
      </div>
      
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

      {isValid && !loading && (
        <p className="text-xs text-green-600 text-center">
          ✓ 描述格式正确,可以开始生成
        </p>
      )}
    </form>
  );
};

export default TextInput;
