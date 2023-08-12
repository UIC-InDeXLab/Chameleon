import React, { useState } from 'react';
import clipboardCopy from 'clipboard-copy';
import './AgeGroupForm.css';
import { BASE_BACKEND_URL } from './api';

const AgeGroupForm = () => {
  const [currentStep, setCurrentStep] = useState(0);
  const [formData, setFormData] = useState([]);
  const [responseMessage, setResponseMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false); 

  const ageGroups = [
    { name: 'Infant', categories: ['Male', 'Female'] },
    { name: 'Preschooler', categories: ['Male', 'Female'] },
    { name: 'School age child', categories: ['Male', 'Female'] },
    { name: 'Adolescents', categories: ['Male', 'Female'] },
    { name: 'Young Adult', categories: ['Male', 'Female'] },
    { name: 'Adult', categories: ['Male', 'Female'] },
    { name: 'Middle Aged Person', categories: ['Male', 'Female'] },
    { name: 'Senior', categories: ['Male', 'Female'] },
    { name: 'Elderly', categories: ['Male', 'Female'] },
  ];

  const races = ['White', 'Black', 'Asian', 'Indian'];

  const handleNextStep = () => {
    if (currentStep < ageGroups.length - 1) {
      setCurrentStep(currentStep + 1);
    } else {
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

  const handleCopyClick = () => {
    const idElement = document.getElementById('dataset-id');
    const idText = idElement.textContent;

    clipboardCopy(idText) // Use clipboard-copy to copy the ID to the clipboard
      .then(() => {
        console.log('Copied to clipboard:', idText);
      })
      .catch((error) => {
        console.error('Error copying to clipboard:', error);
      });
  };

  const submitFormData = async () => {
    setIsLoading(true);
    try {
      const response = await fetch(`${BASE_BACKEND_URL}/v1/datasets/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({"age_groups" : formData}),
      });

      if (response.ok) {
        const data = await response.json();
        setResponseMessage(
          <p>
            Congrats, your dataset id is{' '}
            <span id="dataset-id" className="code-box">
              {data.id}
            </span>
            .{' '}
            <button onClick={handleCopyClick} className="copy-button">
              Copy to Clipboard
            </button>
          </p>
        );
      } else {
        setResponseMessage(
          'Sorry, we couldn\'t perform your operation right now, please try again later'
        );
      }
    } catch (error) {
      console.error('Error creating dataset:', error);
      setResponseMessage(
        'Sorry, we couldn\'t perform your operation right now, please try again later'
      );
    }
    finally {
      setIsLoading(false);
    }
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
      <div className="response-message">
      {isLoading ? (
          <p>Please wait while we create your dataset...</p> 
        ) : (
          responseMessage 
        )}
      </div>
    </div>
  );
};

export default AgeGroupForm;

