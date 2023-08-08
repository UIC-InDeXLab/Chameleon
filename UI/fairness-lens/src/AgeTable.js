import React, { useState, useEffect } from "react";

const AgeGroupForm = ({ ageGroup, onSubmit }) => {
  const [maleWhite, setMaleWhite] = useState("");
  const [femaleWhite, setFemaleWhite] = useState("");
  const [maleBlack, setMaleBlack] = useState("");
  const [femaleBlack, setFemaleBlack] = useState("");
  const [maleHispanic, setMaleHispanic] = useState("");
  const [femaleHispanic, setFemaleHispanic] = useState("");

  const handleChange = (event) => {
    const { name, value } = event.target;
    switch (name) {
      case "maleWhite":
        setMaleWhite(value);
        break;
      case "femaleWhite":
        setFemaleWhite(value);
        break;
      case "maleBlack":
        setMaleBlack(value);
        break;
      case "femaleBlack":
        setFemaleBlack(value);
        break;
      case "maleHispanic":
        setMaleHispanic(value);
        break;
      case "femaleHispanic":
        setFemaleHispanic(value);
        break;
    }
  };

  const handleSubmit = (event) => {
    event.preventDefault();
    const data = {
      ageGroup: ageGroup,
      maleWhite: maleWhite,
      femaleWhite: femaleWhite,
      maleBlack: maleBlack,
      femaleBlack: femaleBlack,
      maleHispanic: maleHispanic,
      femaleHispanic: femaleHispanic,
    };
    onSubmit(data);
  };

  return (
    <form onSubmit={handleSubmit}>
      <h3>{ageGroup}</h3>
      <div>
        <label>Male/White:</label>
        <input type="number" name="maleWhite" value={maleWhite} onChange={handleChange} />
      </div>
      <div>
        <label>Female/White:</label>
        <input type="number" name="femaleWhite" value={femaleWhite} onChange={handleChange} />
      </div>
      <div>
        <label>Male/Black:</label>
        <input type="number" name="maleBlack" value={maleBlack} onChange={handleChange} />
      </div>
      <div>
        <label>Female/Black:</label>
        <input type="number" name="femaleBlack" value={femaleBlack} onChange={handleChange} />
      </div>
      <div>
        <label>Male/Hispanic:</label>
        <input type="number" name="maleHispanic" value={maleHispanic} onChange={handleChange} />
      </div>
      <div>
        <label>Female/Hispanic:</label>
        <input type="number" name="femaleHispanic" value={femaleHispanic} onChange={handleChange} />
      </div>
      <button type="submit">Next</button>
    </form>
  );
};

const App = () => {
  const [ageGroup, setAgeGroup] = useState("");
  const [data, setData] = useState([]);

  const handleSubmit = (data) => {
    setData(data);
  };

  return (
    <div>
      <AgeGroupForm ageGroup={ageGroup} onSubmit={handleSubmit} />
      {data.map((d, i) => (
        <AgeGroupForm ageGroup={d.ageGroup} key={i} onSubmit={handleSubmit} />
      ))}
    </div>
  );
};

export default App;
