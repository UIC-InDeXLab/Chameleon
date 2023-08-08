import React from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import HomePage from './HomePage';
import AgeGroupForm from './AgeGroupForm';
import RepairDatasetPage from './RepairDatasetPage';
import RepairDatasetDetails from './RepairDatasetDetails';

const App = () => {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/create-dataset" element={<AgeGroupForm />} />
        <Route path="/repair-dataset" element={<RepairDatasetPage />} />
        <Route path="/repair-dataset/:id" element={<RepairDatasetDetails />} /> {/* Add this route */}
      </Routes>
    </Router>
  );
};

export default App;
