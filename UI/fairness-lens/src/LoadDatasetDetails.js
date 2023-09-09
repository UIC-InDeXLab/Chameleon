import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { BASE_BACKEND_URL } from './api';
import './LoadDatasetDetails.css';

const LoadDatasetDetails = () => {
  const { id } = useParams();
  const [currentPage, setCurrentPage] = useState(1);
  const [images, setImages] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [raceFilter, setRaceFilter] = useState('all');
  const [genderFilter, setGenderFilter] = useState('all');
  const [ageGroupFilter, setAgeGroupFilter] = useState('all');
  const [isGeneratedFilter, setIsGeneratedFilter] = useState('all');

  useEffect(() => {
    fetchImages();
  }, [currentPage, raceFilter, genderFilter, ageGroupFilter, isGeneratedFilter]);

  const fetchImages = async () => {
    setIsLoading(true);
    try {
      const queryParams = new URLSearchParams();
      const filterParams = [];
      if (raceFilter !== 'all') filterParams.push(`race=${raceFilter}`);
      if (genderFilter !== 'all') filterParams.push(`gender=${genderFilter}`);
      if (ageGroupFilter !== 'all') filterParams.push(`age_group=${ageGroupFilter}`);
      if (isGeneratedFilter !== 'all') queryParams.append('is_generated', isGeneratedFilter);
      
      queryParams.append('skip', (currentPage - 1) * 25);
      queryParams.append('limit', 25);
      if (filterParams.length > 0) {
        queryParams.append('filters', filterParams);
      }
      console.log(queryParams);
      const response = await fetch(`${BASE_BACKEND_URL}/v1/datasets/${id}/images/?${queryParams}`);
      const data = await response.json();
      setImages(data.images);
    } catch (error) {
      console.error('Error fetching images:', error);
    } finally {
      setIsLoading(false);
    }
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
      <h2>Loaded Dataset Details</h2>
      <div className="filters">
        <label>Race:</label>
        <select value={raceFilter} onChange={(e) => setRaceFilter(e.target.value)}>
          <option value="all">All</option>
          <option value="0">White</option>
          <option value="1">Black</option>
          <option value="2">Asian</option>
          <option value="3">Indian</option>
        </select>
        <label>Gender:</label>
        <select value={genderFilter} onChange={(e) => setGenderFilter(e.target.value)}>
          <option value="all">All</option>
          <option value="0">Male</option>
          <option value="1">Female</option>
        </select> 
        <label>Age Group:</label>
        <select value={ageGroupFilter} onChange={(e) => setAgeGroupFilter(e.target.value)}>
          <option value="all">All</option>
          <option value="0">Infant</option>
          <option value="1">Preschooler</option>
          <option value="2">School Age Child</option>
          <option value="3">Adolescents</option>
          <option value="4">Young Adult</option>
          <option value="5">Adult</option>
          <option value="6">Middle Aged Person</option>
          <option value="7">Elderly</option>
        </select>  
        <label>Generated Images:</label>
        <select value={isGeneratedFilter} onChange={(e) => setIsGeneratedFilter(e.target.value)}>
          <option value="all">All</option>
          <option value="true">Just Generated</option>
          <option value="false">Just Original</option>
        </select>         
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
