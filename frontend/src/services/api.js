const API_URL = "http://127.0.0.1:8000";

export async function predecirSena(archivo) {
    const formData = new FormData();

    formData.append("file", archivo);

    const response = await fetch(
        `${API_URL}/api/v1/predict`,
        {
            method: "POST",
            body: formData
        }
    );

    if (!response.ok) {
        throw new Error("Error al comunicarse con el backend");
    }

    return await response.json();
}