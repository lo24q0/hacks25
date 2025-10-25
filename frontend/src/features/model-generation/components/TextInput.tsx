import React, { useState } from 'react';
import { Button, TextArea, Toast, Tag, Space, Tooltip } from '@douyinfe/semi-ui';
import { IconStar, IconBulb } from '@douyinfe/semi-icons';

interface TextInputProps {
  onGenerate: (text: string) => void
  loading?: boolean
}

const EXAMPLE_PROMPTS = [
  '一个带把手的圆形咖啡杯,高度10厘米',
  '现代简约风格的台灯,底座为圆形',
  '可爱的卡通小猫,坐姿,圆润造型',
  '几何图案的花瓶,高15厘米',
  '带笑脸的圆形徽章',
];

const TextInput: React.FC<TextInputProps> = ({ onGenerate, loading = false }) => {
  const [text, setText] = useState('');
  const [showExamples, setShowExamples] = useState(true);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (text.trim() && text.length >= 10) {
      onGenerate(text);
    } else {
      Toast.warning('描述长度应在 10-1000 字符之间');
    }
  }

  const handleExampleClick = (example: string) => {
    setText(example);
    setShowExamples(false);
    Toast.success('已填充示例描述');
  };

  const isValid = text.trim().length >= 10 && text.trim().length <= 1000;
  const charCount = text.length;
  const charColor = charCount === 0 ? 'gray' : charCount > 900 ? 'red' : charCount > 700 ? 'orange' : 'green';

  return (
    <form onSubmit={handleSubmit} className="space-y-5">
      {showExamples && text.length === 0 && (
        <div className="bg-gradient-to-r from-blue-50 to-purple-50 rounded-lg p-4 border border-blue-100">
          <div className="flex items-center gap-2 mb-3">
            <IconBulb className="text-blue-600" size="large" />
            <span className="font-semibold text-gray-700">试试这些示例:</span>
          </div>
          <Space wrap spacing="tight">
            {EXAMPLE_PROMPTS.map((prompt, index) => (
              <Tooltip key={index} content="点击使用此示例" position="top">
                <Tag
                  color="blue"
                  size="large"
                  className="cursor-pointer hover:shadow-md transition-all duration-200 transform hover:scale-105"
                  onClick={() => handleExampleClick(prompt)}
                >
                  {prompt}
                </Tag>
              </Tooltip>
            ))}
          </Space>
        </div>
      )}

      <div className="relative">
        <TextArea
          placeholder="请详细描述你想生成的3D模型...&#10;&#10;提示:&#10;• 描述物体的形状、大小和特征&#10;• 可以指定颜色、材质和风格&#10;• 尽量具体和详细,效果会更好&#10;&#10;例如: 一个带把手的圆形咖啡杯,高度10厘米,简约现代风格"
          value={text}
          onChange={(value) => setText(value)}
          rows={8}
          maxLength={1000}
          showClear
          validateStatus={text.length > 0 && !isValid ? 'error' : 'default'}
          style={{ width: '100%', fontSize: '15px' }}
          className="transition-all duration-200"
          onFocus={() => setShowExamples(false)}
        />
        <div className="mt-3 flex items-center justify-between">
          <div className="flex items-center gap-2">
            {text.length >= 10 && text.length <= 1000 && (
              <Tag color="green" size="small">
                ✓ 描述符合要求
              </Tag>
            )}
            {text.length > 0 && text.length < 10 && (
              <Tag color="orange" size="small">
                还需 {10 - text.length} 个字符
              </Tag>
            )}
          </div>
          <div className="text-sm font-medium" style={{ color: charColor === 'gray' ? '#8c8c8c' : charColor === 'green' ? '#52c41a' : charColor === 'orange' ? '#fa8c16' : '#ff4d4f' }}>
            {charCount}/1000 字符
          </div>
        </div>
        {text.length > 0 && !isValid && (
          <div className="mt-2 text-sm text-red-500 flex items-center gap-1">
            <span>⚠️</span>
            <span>描述长度应在 10-1000 字符之间</span>
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
        icon={<IconStar />}
        theme="solid"
        className="transition-all duration-200 hover:shadow-lg"
        style={{ 
          background: !isValid || loading ? undefined : 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
          borderColor: 'transparent'
        }}
      >
        {loading ? '正在施展魔法...' : '✨ 生成 3D 模型'}
      </Button>

      {text.length > 0 && (
        <div className="text-xs text-gray-500 text-center">
          💡 提示: 详细的描述能获得更好的生成效果
        </div>
      )}
    </form>
  )
}

export default TextInput
