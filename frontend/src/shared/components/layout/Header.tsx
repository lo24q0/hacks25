import { Link, useLocation } from 'react-router-dom'
import { Nav } from '@douyinfe/semi-ui'
import { IconHome, IconImage } from '@douyinfe/semi-icons'

export default function Header() {
  const location = useLocation()

  const navItems = [
    { itemKey: '/', text: '模型生成', icon: <IconHome /> },
    { itemKey: '/style-transfer', text: '图片风格化', icon: <IconImage /> },
  ]

  return (
    <header style={{ background: 'white', boxShadow: '0 2px 8px rgba(0,0,0,0.05)' }}>
      <div style={{ maxWidth: 1400, margin: '0 auto', padding: '0 24px' }}>
        <div
          style={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            height: 64,
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: 40 }}>
            <Link to="/" style={{ textDecoration: 'none' }}>
              <h1 style={{ fontSize: 20, fontWeight: 'bold', color: '#333', margin: 0 }}>
                🖨️ 3D模型打印平台
              </h1>
            </Link>

            <Nav
              mode="horizontal"
              selectedKeys={[location.pathname]}
              items={navItems}
              onSelect={(data) => {
                window.location.href = data.itemKey as string
              }}
            />
          </div>
        </div>
      </div>
    </header>
  )
}
