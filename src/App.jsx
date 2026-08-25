import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Meteorology from './pages/Meteorology';
import Forecast from './pages/Forecast';
import './styles/globals.css';

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Meteorology />} />
        <Route path="/forecast" element={<Forecast />} />
      </Routes>
    </BrowserRouter>
  );
}
