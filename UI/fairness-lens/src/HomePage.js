import React from 'react';
import { Link } from 'react-router-dom';
import './HomePage.css';

const HomePage = () => {
  return (
    <div className="home-page">
      <h1>Welcome to Dataset Tools App</h1>
      <div className="button-container">
        <Link to="/create-dataset" className="big-button">
          Create Your Dataset
        </Link>
        {/* <Link to="/repair-dataset" className="big-button">
          Repair Your Dataset
        </Link> */}
        <Link to="/load-dataset" className="big-button">
          Load Your Dataset
        </Link>
        <Link to="/examine-dataset" className="big-button">
          Sample Your Dataset
        </Link>
      </div>
    </div>
  );
};

export default HomePage;
