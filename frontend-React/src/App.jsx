import React from 'react';
import { BrowserRouter, Route, Routes } from 'react-router-dom';
import { SearchPage } from './pages/SearchPage';
import './styles.css';

export function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<SearchPage />} />
      </Routes>
    </BrowserRouter>
  );
}
