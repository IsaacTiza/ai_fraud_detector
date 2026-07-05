import { BrowserRouter, Routes, Route } from "react-router-dom";
import Layout from "./components/Layout";
import Dashboard from "./pages/Dashboard";
import Predict from "./pages/Predict";
import ModelPerformance from "./pages/ModelPerformance";
import Trend from "./pages/Trend";

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<Layout />}>
          <Route path="/" element={<Dashboard />} />
          <Route path="/predict" element={<Predict />} />
          <Route path="/model-performance" element={<ModelPerformance />} />
          <Route path="/trend" element={<Trend />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}
