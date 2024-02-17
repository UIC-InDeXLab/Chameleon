// HomePage.js

import React from 'react';
import { Link } from 'react-router-dom';
import './HomePage.css';
import Logo from './logo.png'; 

const HomePage = () => {
  return (
    <div className="home-page">
      <div className="header">
        <img src={Logo} alt="Chameleon Logo" className="logo" />
        <h1>Chameleon</h1>
      </div>
      <p className="description">
        Welcome to Chameleon
      </p>
      <div className="button-container">
        <Link to="/create-dataset" className="big-button">
          Create Your Dataset
        </Link>
        <Link to="/load-dataset" className="big-button">
          Load Your Dataset
        </Link>
      </div>
    </div>
  );
};

export default HomePage;
