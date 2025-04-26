import { Routes, Route } from 'react-router-dom';
import Layout from './components/Layout';
import HomePage from './pages/HomePage';
import AnalysisPage from './pages/AnalysisPage';
import ResultsPage from './pages/ResultsPage';
import PricingPage from './pages/PricingPage';

function App() {
  return (
    <Routes>
      <Route path="/" element={<Layout />}>
        <Route index element={<HomePage />} />
        <Route path="pricing" element={<PricingPage />} />
        <Route path="analysis/:sessionId" element={<AnalysisPage />} />
        <Route path="results/:sessionId" element={<ResultsPage />} />
      </Route>
    </Routes>
  );
}

export default App;