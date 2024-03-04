import React, {useEffect, useState} from 'react';
import {BASE_BACKEND_URL} from './api';
import './DatasetSelector.css';
import {useNavigate} from 'react-router-dom';

function DatasetSelector() {
    const [datasets, setDatasets] = useState([]);
    const [selectedDataset, setSelectedDataset] = useState(null);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState(null);
    const [datasetId, setDatasetId] = useState(null);
    const [childData, setChildData] = useState({name: '', number: 0, parent: ''});

    useEffect(() => {
        setIsLoading(true);
        setError(null);

        fetch(`${BASE_BACKEND_URL}/v1/datasets/`)
            .then(response => response.json())
            .then(data => setDatasets(data))
            .catch(error => setError(error))
            .finally(() => setIsLoading(false));
    }, []);

    const navigate = useNavigate();

    const handleDatasetChange = (event) => {
        setSelectedDataset(datasets.find(dataset => dataset.name === event.target.value));
    };

    const handleInputChange = (event) => {
        setChildData({
            ...childData,
            [event.target.name]: event.target.value,
        });
    };

    const handleCreateChildDataset = async (event) => {
        event.preventDefault();

        if (!childData.name || childData.number < 1 || childData.number > selectedDataset.num_elements) {
            return;
        }

        try {
            const response = await fetch(`${BASE_BACKEND_URL}/v1/datasets/`, {
                method: 'POST',
                body: JSON.stringify({name: childData.name, number: childData.number, parent: selectedDataset.name}),
            });

            const data = await response.json();

            setSelectedDataset(null);
            setChildData({name: '', number: 0});

            setDatasetId(data.id);
        } catch (error) {
            console.error('Error creating child dataset:', error);
        }
    };

    return (
        <div className="load-dataset-page">
            <div className="dataset-selector">
                <h1>Create Your Own Dataset Sample</h1>

                {isLoading && <p>Loading datasets...</p>}
                {error && <p className="error-message">Error fetching datasets: {error.message}</p>}

                {!isLoading && datasets.length > 0 && (
                    <>
                        <select onChange={handleDatasetChange} value={selectedDataset?.name}
                                className="select-dataset-options">
                            <option value="">Select a parent dataset</option>
                            {datasets.map(dataset => (
                                <option key={dataset.name} value={dataset.name}>
                                    {dataset.name}
                                </option>
                            ))}
                        </select><br></br>

                        {selectedDataset && (
                            <div className="selected-dataset">
                                <p><b>Attributes:</b></p>
                                <ul>
                                    {selectedDataset.attributes.map(attribute => (
                                        <li key={attribute.name}>

                                            {/*<ul>*/}
                                            <div className="attribute-card">
                                                <strong>{attribute.name}</strong>
                                                <pre>{Object.values(attribute.mapping).join(', ')}</pre>
                                            </div>
                                            {/*</ul>*/}
                                        </li>
                                    ))}
                                </ul>

                                <form onSubmit={handleCreateChildDataset}>
                                    <div className="sample-form-input-div">
                                        <label htmlFor="name">Sample Name:</label>
                                        <input type="text" id="name" name="name" value={childData.name}
                                               onChange={handleInputChange}/>
                                        <label htmlFor="number">#Samples:</label>
                                        <input
                                            type="number"
                                            id="number"
                                            name="number"
                                            value={childData.number}
                                            onChange={handleInputChange}
                                            min={1}
                                            max={selectedDataset.num_elements}
                                        />
                                    </div>

                                    <button type="submit">Create Your Sample</button>
                                </form>
                            </div>
                        )}
                    </>
                )}

                {datasetId && (
                    <div className="dataset-created">
                        <p>Dataset created successfully!</p>
                        <div className="dataset-id-box" onClick={() => navigator.clipboard.writeText(datasetId)}>
                            Dataset ID: {datasetId}
                        </div>
                        <button onClick={() => navigate(`/load-dataset/${datasetId}`)}>Explore It!</button>
                    </div>
                )}
            </div>
        </div>

    );
}

export default DatasetSelector;
