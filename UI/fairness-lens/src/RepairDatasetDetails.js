import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import './RepairDatasetDetails.css';
import { BASE_BACKEND_URL } from './api';

const RepairDatasetDetails = () => {
  const { id } = useParams();
  const [count, setCount] = useState(0);
  const [threshold, setThreshold] = useState('');
  const [maskAccuracy, setMaskAccuracy] = useState('accurate');
  const [baseImageStrategy, setBaseImageStrategy] = useState('similar');
  const [bestMups, setBestMups] = useState({});
  const [mups, setMups] = useState({});
  const [lastGeneratedMup, setLastGeneratedMup] = useState('');
  const [attributes, setAttributes] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isGenerating, setIsGenerating] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [generatedImages, setGeneratedImages] = useState([]);
  const [pulledArms, setPulledArms] = useState([]);
  const [selectedImages, setSelectedImages] = useState([]);
  const [hasSubmitted, setHasSubmitted] = useState(false);

  useEffect(() => {
    // Fetch count from the backend based on the dataset ID
    fetch(`${BASE_BACKEND_URL}/v1/datasets/${id}`)
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
      const response = await fetch(
        `${BASE_BACKEND_URL}/v1/datasets/${id}/mups/?threshold=${threshold}`
      );
      const data = await response.json();
      setMups(data.mups);
      setBestMups(data.best_mups);
      setAttributes(data.attributes);
    } catch (error) {
      console.error('Error finding MUPs:', error);
    } finally {
      setIsLoading(false); // Reset loading state
    }
  };

  const handleRepair = async () => {
    setIsGenerating(true);
    console.log(threshold, maskAccuracy, baseImageStrategy);

    try {
      // Post best MUP pattern and threshold to the backend for generating images
      const response = await fetch(
        `${BASE_BACKEND_URL}/v1/datasets/${id}/mups/generate/`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            pattern: Object.keys(bestMups)[0],
            threshold: threshold,
            accuracy: maskAccuracy,
            strategy: baseImageStrategy,
            frequency: Object.values(bestMups)[0]?.count, 
            prompt: Object.values(bestMups)[0]?.prompt, 
            attributes: attributes,
            limit: 1,
          }),
        }
      );

      if (response.ok) {
        const data = await response.json();
        console.log(data.generated_images);
        setGeneratedImages(data.generated_images);
        setPulledArms(data.pulled_arms);
        setMups({});
        setLastGeneratedMup(Object.keys(bestMups)[0]);
        setBestMups({});
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
      let images = generatedImages.map((imageName, index) => {
        return {
            'name': imageName,
            'accepted': !selectedImages.includes(imageName),
            'arm': pulledArms[index]
        };
      });
      console.log(images)
      // Post acceptable images list to the backend
      const response = await fetch(
        `${BASE_BACKEND_URL}/v1/datasets/${id}/images/`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            images: images, 
            attributes: attributes,
            pattern: lastGeneratedMup,
          }),
        }
      );

      if (response.ok) {
        // Handle success
        console.log('Acceptable images submitted successfully.');
        setHasSubmitted(true);
        setGeneratedImages([]);
        setPulledArms([]);
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
      const response = await fetch(
        `${BASE_BACKEND_URL}/v1/datasets/${id}/mups/?threshold=${threshold}`
      );
      const data = await response.json();
      setMups(data.mups);
      setBestMups(data.best_mups);
      setGeneratedImages([]);
      setPulledArms([]);
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
      {Object.keys(bestMups).length > 0 && (
        <div className="best-mup-box">
          <p>
            The best MUP to repair is <b>{Object.values(bestMups)[0]?.prompt}</b> with a frequency of{' '}
            <b>{Object.values(bestMups)[0]?.count}</b>.
          </p>
          <div className="options">
            <label>Mask Accuracy:</label>
            <select
              value={maskAccuracy}
              onChange={(e) => setMaskAccuracy(e.target.value)}
            >
              <option value="accurate">Accurate</option>
              <option value="moderate">Moderate</option>
              <option value="imprecise">Imprecise</option>
            </select>
            <label>Base Image Strategy:</label>
            <select
              value={baseImageStrategy}
              onChange={(e) => setBaseImageStrategy(e.target.value)}
            >
              <option value="similar">Similar Images</option>
              <option value="random">Random</option>
              <option value="ucb">UCB</option>
              <option value="none">No Base Image</option>
            </select>
            <button onClick={handleRepair} className="repair-button">
              Repair
            </button>
          </div>
        </div>
      )}
      {isLoading ? (
        <div className="center-content">
          <p>Loading...</p>
        </div>
      ) : isGenerating ? (
        <div className="center-content">
          <p>
            Generating..., It usually takes about 5 minutes to generate a full
            batch, don't refresh the page
          </p>
        </div>
      ) : (
        Object.keys(mups).length === 0 ? (
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
            <h2>Maximal Uncovered Patterns:</h2>
            <ul className="mups-box">
              {Object.keys(mups).map((key) => (
                <li key={key}>
                  {`${mups[key]?.prompt}: ${mups[key]?.count}`}
                </li>
              ))}
            </ul>
          </div>
        )
      )}
      {generatedImages.length > 0 && !hasSubmitted && (
        <div className="generated-images">
          <h2>Generated Images:</h2>
          <div className="images-grid">
            {generatedImages.map((image, index) => (
              <img
                key={index}
                src={`${BASE_BACKEND_URL}/v1/image/${image}/?is_generated=1`}
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
