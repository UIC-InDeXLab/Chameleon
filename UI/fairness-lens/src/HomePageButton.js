import React from 'react';
import { Link } from 'react-router-dom';

const HomepageButton = () => {
  return (
    <Link to="/" className="homepage-button">
      Homepage
    </Link>
  );
};

export default HomepageButton;
