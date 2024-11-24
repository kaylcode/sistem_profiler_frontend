// src/App.js
import './App.css';
import Sidebar from './Sidebar'; 
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom'; // Ganti Switch dengan Routes
import Home from './Home';
import Kategorisasi from './Kategorisasi'; // Halaman dengan tabel
import Hasil from './Hasil';
import 'bootstrap/dist/css/bootstrap.min.css';

function App() {
  return (
    <Router>
      <div className="App" style={{ display: 'flex' }}>
        <Sidebar />
        <div style={{ flex: 1, padding: '20px' }}>
          <Routes>
            <Route exact path="/" element={<Home />} /> {/* Ganti component dengan element */}
            <Route path="/Kategorisasi" element={<Kategorisasi />} />
            <Route path="/Hasil" element={<Hasil />} />
          </Routes>
        </div>
      </div>
    </Router>
  );
}

export default App;



