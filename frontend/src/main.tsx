import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import App from './App';
import './styles.css';
import './styles/accessibility.css';
import './styles/sdg-theme.css';

createRoot(document.getElementById('root')!).render(<StrictMode><App /></StrictMode>);
