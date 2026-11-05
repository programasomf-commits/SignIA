
import { useEffect, useRef, useState } from "react";
import { predecirSena } from "./services/api";
import "./App.css";

const API_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

function App() {
  const [apiStatus, setApiStatus] = useState("Conectando...");
  const [apiService, setApiService] = useState("");
  const [databaseStatus, setDatabaseStatus] = useState("Consultando...");
  const [samples, setSamples] = useState([]);
  const [datasetSummary, setDatasetSummary] = useState(null);
  const [selectedSample, setSelectedSample] = useState(null);
  const [archivo, setArchivo] = useState(null);
  const [resultado, setResultado] = useState(null);
  const [cargando, setCargando] = useState(false);
  const [error, setError] = useState("");
  const [preview, setPreview] = useState("");
  // Control de cámara integrada
const videoRef = useRef(null);
const streamRef = useRef(null);
const [camaraActiva, setCamaraActiva] = useState(false);
const [capturando, setCapturando] = useState(false);

  useEffect(() => {
    let activo = true;

    async function cargarDatos() {
      try {
        const health = await fetch(`${API_URL}/health`);
        if (!health.ok) throw new Error("FastAPI no disponible");
        const healthData = await health.json();
        if (!activo) return;

        setApiStatus(healthData.status || "ok");
        setApiService(healthData.service || "SignIA API");

        const datasetResponse = await fetch(`${API_URL}/dataset`);
        if (!datasetResponse.ok) throw new Error("No se pudo consultar el dataset");
        const datasetData = await datasetResponse.json();
        if (!activo) return;
        setSamples(Array.isArray(datasetData.samples) ? datasetData.samples : []);

        const summaryResponse = await fetch(`${API_URL}/dataset/summary`);
        if (!summaryResponse.ok) throw new Error("No se pudo consultar el resumen");
        const summaryData = await summaryResponse.json();
        if (!activo) return;
        setDatasetSummary(summaryData);

        const sampleResponse = await fetch(`${API_URL}/dataset/LSM-HOLA-001`);
        if (sampleResponse.ok) {
          const sampleData = await sampleResponse.json();
          if (activo) setSelectedSample(sampleData);
        }

        const dbResponse = await fetch(`${API_URL}/database/status`);
        if (!dbResponse.ok) throw new Error("No se pudo consultar PostgreSQL");
        const dbData = await dbResponse.json();
        if (activo) {
          setDatabaseStatus(dbData.status || "ok");
        }
      } catch (err) {
        if (activo) {
          setApiStatus("error");
          setApiService(err.message || "No se pudo conectar con FastAPI");
          setDatabaseStatus("Sin conexión");
        }
      }
    }

    cargarDatos();
    return () => { activo = false; };
  }, []);

  useEffect(() => {
    if (!archivo) {
      setPreview("");
      return;
    }

    const url = URL.createObjectURL(archivo);
    setPreview(url);
    return () => URL.revokeObjectURL(url);
  }, [archivo]);

  function seleccionarArchivo(event) {
    const nuevoArchivo = event.target.files?.[0];
    if (!nuevoArchivo) return;

    if (!nuevoArchivo.type.startsWith("image/")) {
      setError("Selecciona un archivo de imagen válido.");
      return;
    }

    setArchivo(nuevoArchivo);
    setResultado(null);
    setError("");
  }

  async function analizarImagen() {
    if (!archivo) {
      setError("Primero selecciona una imagen para analizar.");
      return;
    }

    setCargando(true);
    setError("");
    setResultado(null);

    try {
      const data = await predecirSena(archivo);
      setResultado(data);
    } catch (err) {
      setError(err.message || "Ocurrió un error al procesar la imagen.");
    } finally {
      setCargando(false);
    }
  }

    async function activarCamara() {
    try {
      setError("");
      setResultado(null);
      setArchivo(null);

      const stream = await navigator.mediaDevices.getUserMedia({
        video: {
          facingMode: "user",
          width: { ideal: 1280 },
          height: { ideal: 720 }
        },
        audio: false
      });

      streamRef.current = stream;



      setCamaraActiva(true);
    } catch (err) {
      detenerCamara();
      setError("No se pudo acceder a la cámara. Verifica los permisos del navegador.");
    }
  }

  function detenerCamara() {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach((track) => track.stop());
      streamRef.current = null;
    }

    if (videoRef.current) {
      videoRef.current.srcObject = null;
    }

    setCamaraActiva(false);
  }

  async function capturarYAnalizar() {
    const video = videoRef.current;

    if (!video || video.readyState < 2) {
      setError("La cámara todavía no está lista.");
      return;
    }

    setCapturando(true);
    setCargando(true);
    setError("");
    setResultado(null);

    try {
      const canvas = document.createElement("canvas");
      canvas.width = video.videoWidth;
      canvas.height = video.videoHeight;

      const contexto = canvas.getContext("2d");
      contexto.drawImage(video, 0, 0, canvas.width, canvas.height);

      const blob = await new Promise((resolve, reject) => {
        canvas.toBlob(
          (resultado) => {
            if (resultado) {
              resolve(resultado);
            } else {
              reject(new Error("No se pudo capturar la imagen."));
            }
          },
          "image/jpeg",
          0.92
        );
      });

      const imagen = new File([blob], "captura_camara.jpg", {
        type: "image/jpeg"
      });

      const data = await predecirSena(imagen);
      setResultado(data);
    } catch (err) {
      setError(err.message || "Ocurrió un error al analizar la captura.");
    } finally {
      setCapturando(false);
      setCargando(false);
    }
  }

    useEffect(() => {
    if (camaraActiva && videoRef.current && streamRef.current) {
      videoRef.current.srcObject = streamRef.current;

      videoRef.current.play().catch(() => {
        setError("No se pudo iniciar la reproducción de la cámara.");
      });
    }
  }, [camaraActiva]);

  useEffect(() => {
    return () => {
      if (streamRef.current) {
        streamRef.current.getTracks().forEach((track) => track.stop());
      }
    };
  }, []);

  const totalMuestras = datasetSummary?.total_samples ?? samples.length;
  const etiquetas = Array.isArray(datasetSummary?.labels)
    ? datasetSummary.labels
    : [];
  const lenguajes = Array.isArray(datasetSummary?.languages)
    ? datasetSummary.languages
    : [];

  const confianza = resultado?.confidence ?? resultado?.confidence_score;
  const confianzaPorcentaje =
    typeof confianza === "number"
      ? `${(confianza * 100).toFixed(1)}%`
      : "No disponible";

  const conexionActiva = apiStatus === "ok";

  return (
    <main className="app-shell">
      <header className="topbar">
        <a className="brand" href="#inicio">
          <span className="brand-symbol">S</span>
          <span>
            <strong>SignIA</strong>
            <small>INTERPRETACIÓN DE LENGUA DE SEÑAS</small>
          </span>
        </a>

        <div className="topbar-right">
          <span className={`connection-pill ${conexionActiva ? "online" : "offline"}`}>
            <span className="status-dot" />
            {conexionActiva ? "Sistema conectado" : "Sistema desconectado"}
          </span>
          <span className="version-label">PROTOTIPO · 1.0</span>
        </div>
      </header>

      <section className="hero-section" id="inicio">
        <div className="hero-copy">
          <span className="eyebrow"><span /> TECNOLOGÍA PARA LA INCLUSIÓN</span>
          <h1>Las manos también<br /><span>tienen una voz.</span></h1>
          <p>
            Plataforma experimental para el reconocimiento de señas de la
            Lengua de Señas Mexicana mediante visión artificial y aprendizaje automático.
          </p>
        </div>
        <div className="hero-decoration" aria-hidden="true">
          <div className="orbit orbit-one" />
          <div className="orbit orbit-two" />
          <div className="orbit-core">S</div>
          <span className="orbit-caption">LSM / AI</span>
        </div>
      </section>

      <section className="metrics-grid">
        <article className="metric-card">
          <span className="metric-icon">◈</span>
          <span className="metric-label">Muestras del dataset</span>
          <strong>{totalMuestras}</strong>
          <small>Registros disponibles en el proyecto</small>
        </article>
        <article className="metric-card">
          <span className="metric-icon">⌘</span>
          <span className="metric-label">Etiquetas registradas</span>
          <strong>{etiquetas.length}</strong>
          <small>{etiquetas.length ? etiquetas.join(" · ") : "Información pendiente"}</small>
        </article>
        <article className="metric-card">
          <span className="metric-icon">◎</span>
          <span className="metric-label">Lenguaje</span>
          <strong>{lenguajes.length ? lenguajes.join(", ") : "LSM"}</strong>
          <small>Lengua de Señas Mexicana</small>
        </article>
        <article className="metric-card">
          <span className="metric-icon">⌁</span>
          <span className="metric-label">Umbral de confianza</span>
          <strong>85%</strong>
          <small>Requisito para registrar predicciones</small>
        </article>
      </section>

      <section className="workspace">
        <div className="section-heading">
          <div>
            <span className="eyebrow">ÁREA DE TRABAJO</span>
            <h2>Reconocimiento de señas</h2>
          </div>
          <span className="module-tag">MÓDULO 01 / VISIÓN ARTIFICIAL</span>
        </div>

        <div className="recognition-grid">
          <article className="panel upload-panel">
            <div className="panel-heading">
              <div>
                <span className="step-number">01</span>
                <h3>Imagen de entrada</h3>
              </div>
              <span className="subtle-label">ENTRADA</span>
            </div>

            <div className="camera-section">
              <div className="camera-controls">
                {!camaraActiva ? (
                  <button
                    type="button"
                    className="analyze-button"
                    onClick={activarCamara}
                    disabled={!conexionActiva}
                  >
                    ACTIVAR CÁMARA
                    <span>◉</span>
                  </button>
                ) : (
                  <>
                    <button
                      type="button"
                      className="analyze-button"
                      onClick={capturarYAnalizar}
                      disabled={capturando || cargando}
                    >
                      {capturando ? "CAPTURANDO..." : "CAPTURAR Y ANALIZAR"}
                      <span>→</span>
                    </button>

                    <button
                      type="button"
                      className="remove-file"
                      onClick={detenerCamara}
                    >
                      DETENER CÁMARA
                    </button>
                  </>
                )}
              </div>

              {camaraActiva && (
                <div className="camera-preview">
                  <video
                    ref={videoRef}
                    autoPlay
                    playsInline
                    muted
                    style={{
                      width: "100%",
                      maxHeight: "320px",
                      objectFit: "cover",
                      borderRadius: "12px",
                      background: "#000"
                    }}
                  />
                  <p>Coloca tu mano frente a la cámara y realiza la seña.</p>
                </div>
              )}
            </div>

            <label className={`upload-zone ${preview ? "has-preview" : ""}`}>
              {preview ? (
                <img className="image-preview" src={preview} alt="Imagen seleccionada para analizar" />
              ) : (
                <span className="upload-placeholder">
                  <span className="upload-icon">＋</span>
                  <strong>Selecciona una imagen</strong>
                  <small>Formatos de imagen compatibles con el navegador</small>
                  <span className="browse-label">EXPLORAR ARCHIVOS</span>
                </span>
              )}
              <input type="file" accept="image/*" onChange={seleccionarArchivo} />
            </label>

            {archivo && (
              <div className="file-info">
                <span>◈</span>
                <span className="file-name">{archivo.name}</span>
                <button className="remove-file" onClick={() => {
                  setArchivo(null);
                  setResultado(null);
                  setError("");
                }} aria-label="Quitar imagen">×</button>
              </div>
            )}

            <button
              className="analyze-button"
              onClick={analizarImagen}
              disabled={cargando || !archivo || !conexionActiva}
            >
              {cargando ? "ANALIZANDO IMAGEN..." : "ANALIZAR SEÑA"}
              <span>→</span>
            </button>
            <p className="privacy-note">La imagen se envía al servicio local de SignIA para su procesamiento.</p>
          </article>

          <article className="panel result-panel">
            <div className="panel-heading">
              <div>
                <span className="step-number">02</span>
                <h3>Resultado del análisis</h3>
              </div>
              <span className="subtle-label">SALIDA</span>
            </div>

            {!resultado && !cargando && (
              <div className="empty-result">
                <div className="result-orb">⌁</div>
                <strong>Esperando imagen</strong>
                <p>El resultado de la interpretación aparecerá aquí después del análisis.</p>
              </div>
            )}

            {cargando && (
              <div className="empty-result loading-result">
                <div className="loader-ring" />
                <strong>Procesando imagen</strong>
                <p>Analizando la información visual recibida...</p>
              </div>
            )}

            {resultado && (
              <div className="result-content">
                <span className="result-overline">SEÑA IDENTIFICADA</span>
                <strong className="prediction-word">{resultado.prediction || "Sin predicción"}</strong>
                <div className="confidence-row">
                  <span>Confianza del modelo</span>
                  <strong>{confianzaPorcentaje}</strong>
                </div>
                <div className="confidence-track">
                  <span style={{
                    width: `${typeof confianza === "number" ? Math.min(100, Math.max(0, confianza * 100)) : 0}%`
                  }} />
                </div>
                <div className="result-details">
                  <div>
                    <span>Estado</span>
                    <strong>{resultado.status || "No disponible"}</strong>
                  </div>
                  <div>
                    <span>Mano detectada</span>
                    <strong>{resultado.vision?.hand_detected ? "Sí" : "No"}</strong>
                  </div>
                  <div>
                    <span>Landmarks</span>
                    <strong>{resultado.vision?.landmarks?.length ?? "No disponible"}</strong>
                  </div>
                </div>
                {resultado.status === "low_confidence" && (
                  <p className="warning-message">
                    La confianza está por debajo del umbral del 85%. Esta predicción no se registra.
                  </p>
                )}
              </div>
            )}
          </article>
        </div>

        {error && <div className="error-message">⚠ {error}</div>}
      </section>

      <section className="system-section">
        <div className="section-heading">
          <div>
            <span className="eyebrow">INFRAESTRUCTURA</span>
            <h2>Estado de los servicios</h2>
          </div>
        </div>

        <div className="services-grid">
          <article className="service-card">
            <span className={`service-indicator ${conexionActiva ? "active" : "inactive"}`} />
            <div>
              <strong>API / FastAPI</strong>
              <small>{apiService || "Verificando servicio..."}</small>
            </div>
            <span className="service-status">{apiStatus}</span>
          </article>
          <article className="service-card">
            <span className={`service-indicator ${databaseStatus === "ok" ? "active" : "inactive"}`} />
            <div>
              <strong>Base de datos / PostgreSQL</strong>
              <small>Servicio de persistencia</small>
            </div>
            <span className="service-status">{databaseStatus}</span>
          </article>
          <article className="service-card">
            <span className="service-indicator active" />
            <div>
              <strong>Clasificador LSM</strong>
              <small>Modelo de reconocimiento configurado</small>
            </div>
            <span className="service-status">Configurado</span>
          </article>
        </div>
      </section>

      <section className="dataset-section">
        <div className="section-heading">
          <div>
            <span className="eyebrow">INFORMACIÓN DEL PROYECTO</span>
            <h2>Dataset de SignIA</h2>
          </div>
          <span className="module-tag">{samples.length} MUESTRAS CONSULTADAS</span>
        </div>

        <div className="dataset-panel">
          <div className="dataset-summary">
            <div>
              <span className="metric-label">Etiquetas disponibles</span>
              <div className="tag-list">
                {etiquetas.length
                  ? etiquetas.map((label) => <span className="data-tag" key={label}>{label}</span>)
                  : <span className="muted">Sin información</span>}
              </div>
            </div>
            <div>
              <span className="metric-label">Lenguajes registrados</span>
              <div className="tag-list">
                {lenguajes.length
                  ? lenguajes.map((language) => <span className="data-tag" key={language}>{language}</span>)
                  : <span className="muted">Sin información</span>}
              </div>
            </div>
          </div>

          {selectedSample && (
            <div className="sample-detail">
              <span className="eyebrow">MUESTRA DE REFERENCIA</span>
              <strong>{selectedSample.sample_id}</strong>
              <span>{selectedSample.label} · {selectedSample.language}</span>
              <small>
                {selectedSample.frames ?? "—"} frames · {selectedSample.landmarks_per_frame ?? "—"} landmarks por frame
              </small>
            </div>
          )}
        </div>
      </section>

      <footer className="footer">
        <div className="footer-brand"><span className="brand-symbol">S</span> SignIA</div>
        <span>Proyecto académico · Interpretación de Lengua de Señas Mexicana</span>
        <span>© 2026</span>
      </footer>
    </main>
  );
}

export default App;
