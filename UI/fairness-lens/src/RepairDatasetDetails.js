import React, {useEffect, useState} from 'react';
import {useParams} from 'react-router-dom';
import {BeatLoader} from 'react-spinners';
import './RepairDatasetDetails.css';
import {BASE_BACKEND_URL} from './api';


const MupCard = ({mup, count}) => {
    return (
        <div className="mup-card">
            <div className="mup-content">
                <p className="mup-name">{mup.combination_str}</p>
            </div>
            <div className="mup-count-wrapper">
                <p className="mup-count">{count}</p>
            </div>
        </div>
    );
};

const renderMUPList = (mups) => {
    const maxLevel = Math.max(...Object.values(mups).map((mup) => mup.level));

    return (
        <div className="mups-list">
            <h2>Maximal Uncovered Patterns:</h2>
            {Array.from({length: maxLevel}, (_, level) => (
                <div className="level-row" key={level + 1}>
                    <h3>Level {level + 1}</h3>
                    <div className="mup-cards">
                        {Object.values(mups).filter((mup) => mup.level === level + 1).map((mup) => (
                            <MupCard key={mup.combination_str} mup={mup} count={mup.count}/>
                        ))}
                    </div>
                </div>
            ))}
        </div>
    );
};
const RepairDatasetDetails = () => {
    const {id} = useParams();
    const [count, setCount] = useState(0);
    const [threshold, setThreshold] = useState('');
    const [maskAccuracy, setMaskAccuracy] = useState('accurate');
    const [baseImageStrategy, setBaseImageStrategy] = useState('similar');
    const [batchSize, setBatchSize] = useState(9);
    const [useParentForEmbeddings, setUseParentForEmbeddings] = useState(false);
    const [pmup, setPmup] = useState('');
    const [prompt, setPrompt] = useState('');
    const [combinationStr, setCombinationStr] = useState('')
    const [countNeeded, setCountNeeded] = useState(0);
    const [pattern, setPattern] = useState('');
    const [bestMups, setBestMups] = useState({});
    const [mups, setMups] = useState({});
    const [lastGeneratedMup, setLastGeneratedMup] = useState('');
    const [attributes, setAttributes] = useState([]);
    const [isLoading, setIsLoading] = useState(false);
    const [isGenerating, setIsGenerating] = useState(false);
    const [isSubmitting, setIsSubmitting] = useState(false);
    const [generatedImages, setGeneratedImages] = useState([]);
    const [pulledArms, setPulledArms] = useState([]);
    const [ddtResults, setDdtResults] = useState([]);
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
            setPmup(Object.values(data.best_mups)[0]?.pmup);
            setPrompt(Object.values(data.best_mups)[0]?.prompt);
            setCombinationStr(Object.values(data.best_mups)[0]?.combination_str);
            setCountNeeded(threshold - Object.values(data.best_mups)[0]?.count);
            setPattern(Object.values(data.best_mups)[0]?.pattern);
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
                        pattern: pattern,
                        threshold: threshold,
                        accuracy: maskAccuracy,
                        strategy: baseImageStrategy,
                        frequency: threshold - countNeeded,
                        prompt: prompt,
                        attributes: attributes,
                        use_parent_for_embeddings: useParentForEmbeddings,
                        limit: batchSize,
                    }),
                }
            );

            if (response.ok) {
                const data = await response.json();
                console.log(data.generated_images);
                setGeneratedImages(data.generated_images);
                setPulledArms(data.pulled_arms);
                setDdtResults(data.ddt_results);
                setMups({});
                setLastGeneratedMup(pattern);
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
                const isAccepted = !selectedImages.includes(imageName) && ddtResults[index];
                return {
                    'name': imageName,
                    'accepted': isAccepted,
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
                setCountNeeded(countNeeded - generatedImages.length + selectedImages.length)
                setGeneratedImages([]);
                setPulledArms([]);
                setDdtResults([]);
                setSelectedImages([]);
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
            const res = await fetch(
                `${BASE_BACKEND_URL}/v1/datasets/${id}/mups/${pmup}/status/?threshold=${threshold}`,
                {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        attributes: attributes
                    }),
                }
            );

            const d = await res.json();

            console.log(d.count);
            console.log(d.is_satisfied)

            // Fetch MUPs response from the backend using the current threshold and dataset ID
            if (d.is_satisfied) {
                const response = await fetch(
                    `${BASE_BACKEND_URL}/v1/datasets/${id}/mups/?threshold=${threshold}`
                );
                const data = await response.json();
                setMups(data.mups);
                setBestMups(data.best_mups);
                setAttributes(data.attributes);
                setPmup(Object.values(data.best_mups)[0]?.pmup);
                setPrompt(Object.values(data.best_mups)[0]?.prompt);
                setCountNeeded(threshold - Object.values(data.best_mups)[0]?.count);
                setPattern(Object.values(data.best_mups)[0]?.pattern);
                setCombinationStr(Object.values(data.best_mups)[0]?.combination_str);
                setGeneratedImages([]);
                setPulledArms([]);
                setDdtResults([]);
                setHasSubmitted(false); // Reset submission status
            } else {
                setBestMups(lastGeneratedMup);
                setGeneratedImages([]);
                setPulledArms([]);
                setDdtResults([]);
                setCountNeeded(threshold - d.count)
                setHasSubmitted(false); // Reset submission status
            }
        } catch (error) {
            console.error('Error finding MUPs:', error);
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div>
            <div className="title">
                <h2>Dataset</h2>
                <pre>{id}</pre>
                <h2> has {count} images</h2>
            </div>
            {Object.keys(bestMups).length > 0 && (
                <div className="best-mup-box">
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
                            <option value="ucb">LinUCB</option>
                            <option value="similar">Similar Images</option>
                            <option value="random">Random</option>
                            <option value="none">No Base Image</option>
                        </select>
                        <label> Use Parent Dataset For Embeddings: </label>
                        <input
                            type="checkbox"
                            checked={useParentForEmbeddings}
                            className="embeddings-checkbox"
                            onChange={(e) => setUseParentForEmbeddings(e.target.checked)}
                        />
                        <label>Batch Size:</label>
                        <select
                            value={batchSize}
                            onChange={(e) => setBatchSize(Number(e.target.value))}
                        >
                            <option value="1">1</option>
                            <option value="5">5</option>
                            <option value="9" selected>
                                9 (default)
                            </option>
                            <option value="16">16</option>
                        </select>
                        <button onClick={handleRepair} className="repair-button">
                            Repair
                        </button>
                    </div>
                    <br></br>
                    <div className="best-mup-text">
                        <p>
                            The best combination to generate image for is <b>{combinationStr}</b><br></br>
                            Total number of images required to satisfy one lowest level MUP
                            is <b>{countNeeded}</b>.
                        </p>
                    </div>
                </div>
            )}
            {isLoading ? (
                <div className="center-content">
                    <BeatLoader size={15} color={'#36D7B7'} loading={isLoading}/>
                    <p>Loading...</p>
                </div>
            ) : isGenerating ? (
                <div className="center-content">
                    <BeatLoader size={15} color={'#36D7B7'} loading={isGenerating}/>
                    <p>Generating..., It usually takes about 5 minutes to generate a full batch, don't refresh the
                        page</p>
                </div>
            ) : (
                Object.keys(mups).length === 0 ? (
                    <div className="repair-div">
                        <form onSubmit={handleFindMUPs} className="repair-form">
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
                    </div>
                ) : (
                    <div className="mups-list">
                        {renderMUPList(mups)}
                    </div>
                )
            )}
            {generatedImages.length > 0 && !hasSubmitted && (
                <div className="generated-images">
                    <h2>Generated Images:</h2>
                    <div className="prompt-div">
                        Prompt for Generated Images is <b>{prompt}</b>
                    </div>
                    <div className="submit-button-div">
                        <p>
                            Please select images that look <b>unrealistic</b>.<br></br> Upon selecting an image, a red
                            border will be displayed around the chosen image. To deselect the image, click on it once
                            again.
                        </p>
                        <button onClick={handleSubmitImages} className="submit-button">
                            Submit
                        </button>
                    </div>
                    <div className="images-grid">
                        {generatedImages.map((image, index) => (
                            <img
                                key={index}
                                src={`${BASE_BACKEND_URL}/v1/image/${image}/?is_generated=1`}
                                alt={`Generated Image ${index}`}
                                onClick={() => (ddtResults[index] ? handleImageClick(image) : {})} // Conditionally handle click
                                className={
                                    ddtResults[index]
                                        ? selectedImages.includes(image)
                                            ? 'selected'
                                            : ''
                                        : 'grayed-out' // Add class for greyed-out images
                                }
                            />
                        ))}
                    </div>
                </div>
            )}
            {hasSubmitted && (
                <div className="reeavalute-div">
                    <button onClick={handleReevaluate} className="reevaluate-button">
                        Reevaluate Dataset
                    </button>
                </div>
            )}
        </div>
    );
};

export default RepairDatasetDetails;