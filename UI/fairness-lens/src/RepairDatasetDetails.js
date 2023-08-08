import React from 'react';
import { useLocation } from 'react-router-dom';

const RepairDatasetDetails = () => {
  const location = useLocation();
  const datasetDetails = location.state?.datasetDetails || {};

  // Render the dataset details
  return (
    <div>
      <h1>Dataset Details</h1>
      <pre>{JSON.stringify(datasetDetails, null, 2)}</pre>
    </div>
  );
};

export default RepairDatasetDetails;
