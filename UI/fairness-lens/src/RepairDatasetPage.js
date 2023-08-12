import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom'; // Import useNavigate instead of useHistory
import './RepairDatasetPage.css'; // Import the CSS file
import { BASE_BACKEND_URL } from './api';


const RepairDatasetPage = () => {
  const [datasetId, setDatasetId] = useState('');
  const navigate = useNavigate(); // Use useNavigate instead of useHistory

  const handleInputChange = (e) => {
    setDatasetId(e.target.value);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      // Fetch dataset details from the backend using the provided datasetId
      console.log({datasetId})
      const response = await fetch(`${BASE_BACKEND_URL}/v1/datasets/${datasetId}/`);
      const data = await response.json();

      // Redirect to the dataset details page
      navigate(`/repair-dataset/${datasetId}`, { state: { datasetDetails: data } });
    } catch (error) {
      console.error('Error loading dataset:', error);
    }
  };

  return (
    <div className="repair-dataset-page">
      <h1>Repair Your Dataset</h1>
      <form onSubmit={handleSubmit}>
        <label>
          Enter Dataset ID:
          <input
            type="text"
            value={datasetId}
            onChange={handleInputChange}
            className="dataset-id-input"
          />
        </label>
        <button type="submit" className="load-button">
          Load My Dataset
        </button>
      </form>
    </div>
  );
};

export default RepairDatasetPage;
