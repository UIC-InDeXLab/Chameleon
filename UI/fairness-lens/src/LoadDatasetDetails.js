import React, {useEffect, useState} from 'react';
import {Link, useParams} from 'react-router-dom';
import {BASE_BACKEND_URL} from './api';
import './LoadDatasetDetails.css';

const LoadDatasetDetails = () => {
    const {id} = useParams();
    const [currentPage, setCurrentPage] = useState(1);
    const [images, setImages] = useState([]);
    const [isLoading, setIsLoading] = useState(true);
    const [filters, setFilters] = useState([]);
    const [selectedFilters, setSelectedFilters] = useState({});
    const [isGeneratedFilter, setIsGeneratedFilter] = useState('all');

    useEffect(() => {
        fetchFilters();
        fetchImages();
    }, [currentPage, selectedFilters, isGeneratedFilter]);


    const fetchFilters = async () => {
        try {
            const response = await fetch(`${BASE_BACKEND_URL}/v1/datasets/${id}/`);
            const data = await response.json();
            setFilters(data.attributes);
        } catch (error) {
            console.error('Error fetching filters:', error);
        }
    };


    const fetchImages = async () => {
        setIsLoading(true);
        try {
            const queryParams = new URLSearchParams();
            const filterParams = [];

            filters.forEach((filter) => {
                const selectedValue = selectedFilters[filter.name] || 'all';
                filterParams.push(`${filter.name}=${selectedValue}`);
            });

            if (isGeneratedFilter !== 'all') queryParams.append('is_generated', isGeneratedFilter);

            queryParams.append('skip', (currentPage - 1) * 25);
            queryParams.append('limit', 25);

            if (filterParams.length > 0) {
                queryParams.append('filters', filterParams.join('&'));
            }

            const response = await fetch(`${BASE_BACKEND_URL}/v1/datasets/${id}/images/?${queryParams}`);
            const data = await response.json();
            setImages(data.images);
        } catch (error) {
            console.error('Error fetching images:', error);
        } finally {
            setIsLoading(false);
        }
    };

    const handleFilterChange = (filterName, selectedValue) => {
        setSelectedFilters((prevFilters) => ({
            ...prevFilters,
            [filterName]: selectedValue,
        }));
    };


    // Handle pagination
    const handleNextPage = () => {
        setCurrentPage(currentPage + 1);
    };

    const handlePreviousPage = () => {
        if (currentPage > 1) {
            setCurrentPage(currentPage - 1);
        }
    };

    return (
        <div>
            <div className="title">
                <pre>{id}</pre>
                <h2> Details</h2>
            </div>
            <div className="filters">
            {filters.map((filter) => (
                    <div key={filter.name}>
                        <label>{filter.name.charAt(0).toUpperCase() + filter.name.slice(1)}:</label>
                        <select value={selectedFilters[filter.name] || 'all'}
                                onChange={(e) => handleFilterChange(filter.name, e.target.value)}>
                            <option value="all">All</option>
                            {Object.entries(filter.mapping).map(([value, label]) => (
                                <option key={value} value={value}>
                                    {label}
                                </option>
                            ))}
                        </select>
                    </div>
                ))}
                <div key="generated-images">
                    <label>Generated Images:</label>
                    <select value={isGeneratedFilter} onChange={(e) => setIsGeneratedFilter(e.target.value)}>
                        <option value="all">All</option>
                        <option value="true">Just Generated</option>
                        <option value="false">Just Original</option>
                    </select>
                </div>
            </div>
            <div className="pagination">
                <button onClick={handlePreviousPage} disabled={currentPage === 1}>
                    Previous Page
                </button>
                <span>Page {currentPage}</span>
                <button onClick={handleNextPage}>Next Page</button>
            </div>
            <div className="gallery">
                {isLoading ? (
                    <p>Loading images...</p>
                ) : (
                    images.map((image, index) => (
                        <img
                            key={index}
                            src={`${BASE_BACKEND_URL}/v1/image/${id}/${image}`}
                            alt={`Image ${index}`}
                            className="image"
                        />
                    ))
                )}
            </div>
            <div className="repair">
                <Link to={`/repair-dataset/${id}`} className='repair-button'>
                    Repair
                </Link>
            </div>


        </div>
    );
};

export default LoadDatasetDetails;
