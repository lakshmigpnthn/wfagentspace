import React from 'react';
import './index.css';
import ReactDOM from 'react-dom/client';
import GCPAgentSpace from './GCPAgentSpace.tsx'; // Use .tsx extension if the file is not renamed

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <GCPAgentSpace />
  </React.StrictMode>
);

