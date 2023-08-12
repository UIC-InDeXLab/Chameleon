import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import './RepairDatasetDetails.css'; // Import the CSS file

const RepairDatasetDetails = () => {
  const { id } = useParams();
  const [count, setCount] = useState(0);
  const [threshold, setThreshold] = useState('');
  const [mups, setMups] = useState([]);
  const [bestMup, setBestMup] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isGenerating, setIsGenerating] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [generatedImages, setGeneratedImages] = useState([]);
  const [selectedImages, setSelectedImages] = useState([]);  
  const [hasSubmitted, setHasSubmitted] = useState(false);

  useEffect(() => {
    // Fetch count from the backend based on the dataset ID
    fetch(`http://localhost:8000/v1/datasets/${id}`)
      .then((response) => response.json())
      .then((data) => {
        setCount(data.count);
      })
      .catch((error) => {
        console.error('Error fetching dataset count:', error);
      });
  }, [id]);

  const handleThresholdChange = (e) => {
    setThreshold(e.target.value);
  };

  const handleFindMUPs = async (e) => {
    e.preventDefault();
    setIsLoading(true); // Set loading state

    try {
      // Fetch MUPs response from the backend using the provided threshold and dataset ID
      const response = await fetch(`http://localhost:8000/v1/datasets/${id}/mups/?threshold=${threshold}`);
      const data = await response.json();
      setMups(data.mups);
      setBestMup(data.best_mups[0]); // Get the best MUP from the response
    } catch (error) {
      console.error('Error finding MUPs:', error);
    } finally {
      setIsLoading(false); // Reset loading state
    }
  };

  const handleRepair = async () => {
    setIsGenerating(true);
  
    try {
      // Post best MUP pattern and threshold to the backend for generating images
      const response = await fetch(`http://localhost:8000/v1/datasets/${id}/mups/generate/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          pattern: bestMup.pattern,
          threshold: threshold,
          limit: 3,
        }),
      });
  
      if (response.ok) {
        const data = await response.json();
        console.log(data.generated_images)
        setGeneratedImages(data.generated_images);
        setMups([]);
        setBestMup(null);
      } else {
        console.error('Error generating images:', response.statusText);
      }
    } catch (error) {
      console.error('Error generating images:', error);
    } finally {
      setIsGenerating(false);
    }
  };

  const handleImageClick = (image) => {

    // Toggle the selected state of the image
    setSelectedImages((prevSelectedImages) =>
      prevSelectedImages.includes(image)
        ? prevSelectedImages.filter((img) => img !== image)
        : [...prevSelectedImages, image]
    );
  };

  const handleSubmitImages = async () => {
    setIsSubmitting(true);

    try {
      // Subtract selected images from generated images
      const acceptableImages = generatedImages.filter(
        (image) => !selectedImages.includes(image)
      );

      // Post acceptable images list to the backend
      const response = await fetch(`http://localhost:8000/v1/datasets/${id}/images/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          acceptable_images: acceptableImages,
        }),
      });

      if (response.ok) {
        // Handle success
        console.log('Acceptable images submitted successfully.');
        setHasSubmitted(true);
        setGeneratedImages([]);
      } else {
        console.error('Error submitting acceptable images:', response.statusText);
      }
    } catch (error) {
      console.error('Error submitting acceptable images:', error);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleReevaluate = async () => {
    setIsLoading(true);

    try {
      // Fetch MUPs response from the backend using the current threshold and dataset ID
      const response = await fetch(`http://localhost:8000/v1/datasets/${id}/mups/?threshold=${threshold}`);
      const data = await response.json();
      setMups(data.mups);
      setBestMup(data.best_mups[0]);
      setGeneratedImages([]);
      setHasSubmitted(false); // Reset submission status
    } catch (error) {
      console.error('Error finding MUPs:', error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div>
      <h1>Dataset {id} has {count} images</h1>
      {bestMup && (
        <div className="best-mup-box">
          <p>
            The best MUP to repair is {bestMup.prompt} with a frequency of {bestMup.frequency}.
          </p>
          <button onClick={handleRepair} className="repair-button">
            Repair
          </button>
        </div>
      )}
      {isLoading ? (
        <div className="center-content">
          <p>Loading...</p>
        </div>
      ) : isGenerating ? (
        <div className="center-content">
          <p>Generating..., It usually takes about 5 minutes to generate a full batch, don't refresh the page</p>
        </div>
      ) : (
        mups.length === 0 ? (
          <form onSubmit={handleFindMUPs}>
            <label>
              Threshold:
              <input
                type="number"
                value={threshold}
                onChange={handleThresholdChange}
                className="threshold-input"
                required
              />
            </label>
            <button type="submit" className="find-mups-button">
              Find MUPs
            </button>
          </form>
        ) : (
          <div className="mups-list">
            <h2>MUPs List:</h2>
            <ul className="mups-box">
              {mups.map((mup, index) => (
                <li key={index}>
                  {`${index + 1}. ${mup.prompt}: ${mup.frequency}`}
                </li>
              ))}
            </ul>
          </div>
        )
      )}
      {generatedImages.length > 0 && !hasSubmitted &&  (
        <div className="generated-images">
          <h2>Generated Images:</h2>
          <div className="images-grid">
            {generatedImages.map((image, index) => (
              <img
                key={index}
                src={`http://localhost:8000/v1/image/${image}/?is_generated=1`}
                alt={`Generated Image ${index}`}
                onClick={() => handleImageClick(image)}
                className={selectedImages.includes(image) ? 'selected' : ''}
              />
            ))}
          </div>
          <button onClick={handleSubmitImages} className="submit-button">
            Submit
          </button>
        </div>
      )}
      {hasSubmitted && (
        <div className="generated-images">
          <button onClick={handleReevaluate} className="reevaluate-button">
            Reevaluate Dataset
          </button>
        </div>
      )}
    </div>
  );
};

export default RepairDatasetDetails;
