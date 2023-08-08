import React, { useState } from 'react';

const MultiStepForm = () => {
  const ageGroups = [
    { name: 'Infant', genderCategories: ['Male', 'Female'] },
    { name: 'Adolescents', genderCategories: ['Male', 'Female'] },
    // Add more age groups here
  ];
  const raceOptions = ['White', 'Black', 'Hispanic', 'Asian'];

  const [formData, setFormData] = useState([]);

  const handleInputChange = (event, ageGroupIndex, genderCategoryIndex) => {
    const { name, value } = event.target;
    const updatedFormData = [...formData];
    updatedFormData[ageGroupIndex][genderCategoryIndex][name] = value;
    setFormData(updatedFormData);
  };

  const handleNextStep = () => {
    const updatedFormData = [...formData];
    updatedFormData.push([]);
    setFormData(updatedFormData);
  };

  const handleSubmit = () => {
    // Send the form data as JSON to the desired URL
    fetch('https://example.com/submit', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(formData),
    })
      .then((response) => response.json())
      .then((data) => {
        // Handle the response from the server if needed
        console.log(data);
      })
      .catch((error) => {
        // Handle any errors that occur during the request
        console.error(error);
      });
  };

  const renderForm = () => {
    return (
      <div>
        {formData.map((ageGroup, ageGroupIndex) => (
          <div key={ageGroupIndex}>
            <h2>{ageGroups[ageGroupIndex].name}</h2>
            {ageGroups[ageGroupIndex].genderCategories.map((genderCategory, genderCategoryIndex) => (
              <div key={genderCategoryIndex}>
                <h3>{genderCategory}</h3>
                {raceOptions.map((raceOption, raceOptionIndex) => (
                  <label key={raceOptionIndex}>
                    {raceOption}:
                    <input
                      type="number"
                      name={raceOption}
                      value={ageGroup[genderCategoryIndex]?.[raceOption] || ''}
                      onChange={(e) => handleInputChange(e, ageGroupIndex, genderCategoryIndex)}
                    />
                  </label>
                ))}
              </div>
            ))}
          </div>
        ))}
        {formData.length < ageGroups.length && (
          <button onClick={handleNextStep}>Next</button>
        )}
        {formData.length === ageGroups.length && (
          <button onClick={handleSubmit}>Submit</button>
        )}
      </div>
    );
  };

  return (
    <div>
      <h1>Multi-Step Form</h1>
      {renderForm()}
    </div>
  );
};

export default MultiStepForm;
