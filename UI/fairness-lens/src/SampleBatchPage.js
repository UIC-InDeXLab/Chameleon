import React, {useEffect, useState} from 'react';
import './SampleBatchPage.css'; // Add your CSS styles here
import {BASE_BACKEND_URL} from './api'; // Import your backend URL

const SampleBatchPage = () => {
    const [images, setImages] = useState([]);
    const [isLoading, setIsLoading] = useState(true);

    const getSampleBatch = async () => {
        try {
            setIsLoading(true);
            const response = await fetch(`${BASE_BACKEND_URL}/v1/images/sample/`);
            if (response.ok) {
                const data = await response.json();
                setImages(data);
                setImages((prevImages) => prevImages.map((image) => ({...image, accepted: true})));
                setIsLoading(false);
                console.log(data)
            } else {
                console.error('Error fetching sample batch:', response.statusText);
            }
        } catch (error) {
            console.error('Error fetching sample batch:', error);
            setIsLoading(false);
        }
    };

    useEffect(() => {
        // Fetch the initial sample batch when the component mounts
        getSampleBatch();
    }, []);

    const handleClick = (index) => {
        // Create a copy of the images array and toggle the accepted state for the clicked image
        const updatedImages = [...images];
        updatedImages[index].accepted = !updatedImages[index].accepted;
        setImages(updatedImages);
    };

    const handleSubmit = async () => {

        try {
            const jsonData = {};
            images.forEach((image) => {
                jsonData[image.filename] = image.accepted;
            });

            console.log(jsonData);

            const response = await fetch(
                `${BASE_BACKEND_URL}/v1/images/sample/`,
                {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(jsonData)
                }
            );

            if (response.ok) {
                // Handle success
                console.log('Acceptable images submitted successfully.');
                console.log(jsonData)
                getSampleBatch();
            } else {
                console.error('Error submitting acceptable images:', response.statusText);
            }
        } catch (error) {
            console.error('Error submitting acceptable images:', error);
        }
    };


    return (
        <div>
            <h2>Instructions: Please select images that look <b>unrealistic</b><br></br>
                Upon selecting an image, a red border will be displayed around the chosen image <br></br> To deselect
                the image, click on it once again.</h2>
            <div className="button-container">
                <button onClick={handleSubmit} className="submit-button">
                    Submit
                </button>
            </div>
            {isLoading ? (
                <p>Loading...</p>
            ) : (
                <div className="image-grid">
                    {images.map((image, index) => (
                        <div
                            key={index}
                            className={`image-card ${!image.accepted ? 'unacceptable' : ''}`}
                            onClick={() => handleClick(index)}
                        >
                            <img src={`${BASE_BACKEND_URL}/v1/images/${image.filename}`} alt={`Image ${index}`}
                                 className="image"/>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
};

export default SampleBatchPage;
