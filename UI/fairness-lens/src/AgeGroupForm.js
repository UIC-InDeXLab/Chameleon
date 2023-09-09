import React, { useState, useEffect } from 'react';
import clipboardCopy from 'clipboard-copy';
import './AgeGroupForm.css';
import { BASE_BACKEND_URL } from './api';

const AgeGroupForm = () => {
  const [currentStep, setCurrentStep] = useState(0);
  const [formData, setFormData] = useState([]);
  const [responseMessage, setResponseMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [ageGroups, setAgeGroups] = useState([]);
  const [categories, setCategories] = useState([]);
  const [races, setRaces] = useState([]);

  useEffect(() => {
    fetchFormData();
  }, []);

  const fetchFormData = async () => {
    try {
      const response = await fetch(`${BASE_BACKEND_URL}/v1/datasets`);
      const data = await response.json();
      console.log(data.attributes[0].mapping)
      setAgeGroups(data.attributes[0].mapping);
      setCategories(data.attributes[1].mapping);
      setRaces(data.attributes[2].mapping);
    } catch (error) {
      console.error('Error fetching form data:', error);
    }
  };

  const handleNextStep = () => {
    if (currentStep < Object.keys(ageGroups).length - 1) {
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
        body: JSON.stringify({ "age_groups": formData }),
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
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="container">
      <div className="step">
        {Object.keys(ageGroups).map((ageGroupKey, index) =>
          index === currentStep ? (
            <div key={index}>
              <h2>{ageGroups[ageGroupKey]}</h2>
              <div className="categories-row">
                {Object.keys(categories).map((categoryKey) => (
                  <div className="category" key={categoryKey}>
                    <h3>{categories[categoryKey]}</h3>
                    {Object.keys(races).map((raceKey) => (
                      <div className="race" key={raceKey}>
                        <label>{races[raceKey]}:</label>
                        <input
                          type="number"
                          min="0"
                          value={formData[currentStep]?.[ageGroupKey]?.[categoryKey]?.[raceKey] || ''}
                          onChange={(e) =>
                            handleInputChange(ageGroupKey, categoryKey, raceKey, e.target.value)
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
              {currentStep === Object.keys(ageGroups).length - 1 ? (
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
