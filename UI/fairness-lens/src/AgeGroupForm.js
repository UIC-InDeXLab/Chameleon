import React, { useState } from 'react';
import './AgeGroupForm.css';
import HomepageButton from './HomePageButton';

const AgeGroupForm = () => {
  const [currentStep, setCurrentStep] = useState(0);
  const [formData, setFormData] = useState([]);

  const ageGroups = [
    { name: 'Infant', categories: ['Male', 'Female'] },
    { name: 'Preschooler', categories: ['Male', 'Female'] },
    { name: 'School age', categories: ['Male', 'Female'] },
    { name: 'Adolescents', categories: ['Male', 'Female'] },
    { name: 'Young Adult', categories: ['Male', 'Female'] },
    { name: 'Adult', categories: ['Male', 'Female'] },
    { name: 'Middle Aged', categories: ['Male', 'Female'] },
    { name: 'Senior', categories: ['Male', 'Female'] },
    { name: 'Elderly', categories: ['Male', 'Female'] },


    // Add more age groups as needed
  ];

  const races = ['White', 'Black', 'Hispanic', 'Asian'];

  const handleNextStep = () => {
    if (currentStep < ageGroups.length - 1) {
      setCurrentStep(currentStep + 1);
    } else {
      // Last step, submit the form data
      submitFormData();
    }
  };

  const handlePreviousStep = () => {
    if (currentStep > 0) {
      setCurrentStep(currentStep - 1);
    }
  };

  const handleInputChange = (ageGroup, category, race, value) => {
    const updatedFormData = [...formData];
    updatedFormData[currentStep] = {
      ...updatedFormData[currentStep],
      [ageGroup]: {
        ...updatedFormData[currentStep]?.[ageGroup],
        [category]: {
          ...updatedFormData[currentStep]?.[ageGroup]?.[category],
          [race]: value,
        },
      },
    };
    setFormData(updatedFormData);
  };

  const submitFormData = () => {
    const url = 'https://example.com/submit'; // Replace with your specific URL
    console.log(JSON.stringify(formData))
    fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(formData),
    })
      .then((response) => response.json())
      .then((data) => {
        // Handle the response from the server if needed
        console.log('Form data submitted:', data);
      })
      .catch((error) => {
        console.error('Error submitting form data:', error);
      });
  };

  return (
    <div className="container">
      <div className="step">
        {ageGroups.map((ageGroup, index) =>
          index === currentStep ? (
            <div key={index}>
              <h2>{ageGroup.name}</h2>
              <div className="categories-row">
                {ageGroup.categories.map((category) => (
                  <div className="category" key={category}>
                    <h3>{category}</h3>
                    {races.map((race) => (
                      <div className="race" key={race}>
                        <label>{race}:</label>
                        <input
                          type="number"
                          min="0"
                          value={formData[currentStep]?.[ageGroup.name]?.[category]?.[race] || ''}
                          onChange={(e) =>
                            handleInputChange(ageGroup.name, category, race, e.target.value)
                          }
                        />
                      </div>
                    ))}
                  </div>
                ))}
              </div>
              {currentStep > 0 && (
                <button onClick={handlePreviousStep}>Previous</button>
              )}
              {currentStep === ageGroups.length - 1 ? (
                <button onClick={handleNextStep}>Submit</button>
              ) : (
                <button onClick={handleNextStep}>Next</button>
              )}
            </div>
          ) : null
        )}
      </div>
    </div>
  );
};

export default AgeGroupForm;

