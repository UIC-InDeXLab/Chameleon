import React from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import HomePage from './HomePage';
import AgeGroupForm from './AgeGroupForm';
import LoadDatasetPage from './LoadDatasetPage';
import RepairDatasetDetails from './RepairDatasetDetails';
import LoadDatasetDetails from './LoadDatasetDetails';

const App = () => {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/create-dataset" element={<AgeGroupForm />} />
        <Route path="/load-dataset" element={<LoadDatasetPage />} />
        <Route path="/repair-dataset/:id" element={<RepairDatasetDetails />} />
        <Route path="/load-dataset/:id" element={<LoadDatasetDetails />} /> 
      </Routes>
    </Router>
  );
};

export default App;
