import { createBrowserRouter } from 'react-router-dom';
import App from './App';
import GenerationPage from '../features/model-generation/pages/GenerationPage';

export const router = createBrowserRouter([
  {
    path: '/',
    element: <App />,
    children: [
      {
        index: true,
        element: <GenerationPage />,
      },
    ],
  },
]);
