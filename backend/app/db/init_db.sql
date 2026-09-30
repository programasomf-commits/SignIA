-- SignIA - Script de inicialización de PostgreSQL
-- Base de datos: signia_db

CREATE TABLE IF NOT EXISTS integration_test (
    id SERIAL PRIMARY KEY,
    component VARCHAR(100) NOT NULL,
    status VARCHAR(50) NOT NULL
);

INSERT INTO integration_test (component, status)
VALUES ('PostgreSQL', 'ok')
ON CONFLICT DO NOTHING;
