import { useEffect, useState } from "react";

function App() {
  const [apiStatus, setApiStatus] = useState("Conectando...");
  const [apiService, setApiService] = useState("");
  const [samples, setSamples] = useState([]);
  const [selectedSample, setSelectedSample] = useState(null);
  const [datasetSummary, setDatasetSummary] = useState(null);

  useEffect(() => {
fetch("http://127.0.0.1:8000/health")
  .then((response) => {
    if (!response.ok) {
      throw new Error("Error HTTP");
    }

    return response.json();
  })
  .then((data) => {
    setApiStatus(data.status);
    setApiService(data.service);

    return fetch("http://127.0.0.1:8000/dataset");
  })
  .then((response) => {
    if (!response.ok) {
      throw new Error("Error al obtener el dataset");
    }

    return response.json();
  })
 .then((data) => {
  setSamples(data.samples);

  return fetch(
    "http://127.0.0.1:8000/dataset/summary"
  );
})
.then((response) => {
  if (!response.ok) {
    throw new Error("Error al obtener el resumen del dataset");
  }

  return response.json();
})
.then((data) => {
  setDatasetSummary(data);

  return fetch(
    "http://127.0.0.1:8000/dataset/LSM-HOLA-001"
  );
})
.then((response) => {
  if (!response.ok) {
    throw new Error("Error al obtener la muestra");
  }

  return response.json();
})

.then((data) => {
  setSelectedSample(data);

  return fetch(
    "http://127.0.0.1:8000/database/test"
  );
})
.then((response) => {
  if (!response.ok) {
    throw new Error("Error al obtener datos de PostgreSQL");
  }

  return response.json();
})
.then((data) => {
  console.log("PostgreSQL:", data);
})
.catch(() => {
  setApiStatus("error");
  setApiService("No se pudo conectar con FastAPI");
});

  }, []);

  return (
    <div>
      <h1>SignIA</h1>

      <h2>Integración React + FastAPI</h2>

      <p>
        Estado de la API: <strong>{apiStatus}</strong>
      </p>

      <p>
        Servicio: <strong>{apiService}</strong>
      </p>
      <h3>Dataset</h3>

<p>
  Total de muestras: <strong>{samples.length}</strong>
</p>

{datasetSummary && (
  <div>
    <p>
      <strong>Etiquetas:</strong>{" "}
      {datasetSummary.labels.join(", ")}
    </p>

    <p>
      <strong>Lenguajes:</strong>{" "}
      {datasetSummary.languages.join(", ")}
    </p>
  </div>
)}

{samples.map((sample) => (
  <div key={sample.sample_id}>
    <p>
      <strong>Sample ID:</strong> {sample.sample_id}
    </p>

    <p>
      <strong>Etiqueta:</strong> {sample.label}
    </p>

    <p>
      <strong>Lenguaje:</strong> {sample.language}
    </p>

    <p>
      <strong>Shape:</strong> {sample.shape.join(", ")}
    </p>

    <p>
      <strong>Archivo:</strong> {sample.file}
    </p>
  </div>
))}

{selectedSample && (
  <div>
    <h3>Muestra seleccionada</h3>

    <p>
      <strong>Sample ID:</strong> {selectedSample.sample_id}
    </p>

    <p>
      <strong>Etiqueta:</strong> {selectedSample.label}
    </p>

    <p>
      <strong>Lenguaje:</strong> {selectedSample.language}
    </p>

    <p>
      <strong>Frames:</strong> {selectedSample.frames}
    </p>

    <p>
      <strong>Landmarks por frame:</strong>{" "}
      {selectedSample.landmarks_per_frame}
    </p>

    <p>
      <strong>Coordenadas por landmark:</strong>{" "}
      {selectedSample.coordinates_per_landmark}
    </p>

    <p>
      <strong>Shape:</strong>{" "}
      {selectedSample.shape.join(" × ")}
    </p>

    <p>
      <strong>Normalización:</strong>{" "}
      {selectedSample.normalization.origin}
    </p>

    <p>
      <strong>Escala:</strong>{" "}
      {selectedSample.normalization.scale}
    </p>
  </div>
)}
    </div>
  );
}

export default App;
