import { createBrowserRouter } from 'react-router-dom'
import App from './App'
import GenerationPage from '../features/model-generation/pages/GenerationPage'
import StyleTransferPage from '../features/style-transfer/pages/StyleTransferPage'

export const router = createBrowserRouter([
  {
    path: '/',
    element: <App />,
    children: [
      {
        index: true,
        element: <GenerationPage />,
      },
      {
        path: 'style-transfer',
        element: <StyleTransferPage />,
      },
    ],
  },
])
