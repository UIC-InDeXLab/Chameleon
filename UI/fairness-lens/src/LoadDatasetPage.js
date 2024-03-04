// LoadDatasetPage.js

import React, {useState} from 'react';
import {useNavigate} from 'react-router-dom';
import './LoadDatasetPage.css';
import {BASE_BACKEND_URL} from './api';

const LoadDatasetPage = () => {
    const [datasetId, setDatasetId] = useState('');
    const navigate = useNavigate();

    const handleInputChange = (e) => {
        setDatasetId(e.target.value);
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            const response = await fetch(`${BASE_BACKEND_URL}/v1/datasets/${datasetId}/`);
            const data = await response.json();
            navigate(`/load-dataset/${datasetId}`, {state: {datasetDetails: data}});
        } catch (error) {
            console.error('Error loading dataset:', error);
        }
    };

    return (
        <div className="load-dataset-page">
            <div className="content-container">
                <h1>Load Your Dataset</h1>
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
        </div>
    );
};

export default LoadDatasetPage;
