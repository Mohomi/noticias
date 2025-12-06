-- Tabla para mapear nombres alternativos de categorías a categorías existentes
-- Esto permite normalizar categorías similares con nombres diferentes

CREATE TABLE IF NOT EXISTS tbl_categoria_mapeo (
    id_mapeo SERIAL PRIMARY KEY,
    nombre_alternativo VARCHAR(100) NOT NULL UNIQUE,
    id_categoria_real INTEGER NOT NULL,
    fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (id_categoria_real) REFERENCES tbl_categoria(id_categoria)
        ON DELETE CASCADE ON UPDATE CASCADE,

    INDEX idx_nombre_alternativo (nombre_alternativo),
    INDEX idx_categoria_real (id_categoria_real)
);

-- Insertar algunos mapeos comunes iniciales
INSERT IGNORE INTO tbl_categoria_mapeo (nombre_alternativo, id_categoria_real) VALUES
-- Nacional / País
('nacional', 1),  -- Asumiendo que 1 es la categoría "Nacional" o similar
('país', 1),
('local', 1),

-- Internacional / Mundo
('internacional', 2),  -- Asumiendo que 2 es "Internacional"
('mundo', 2),
('global', 2),
('world', 2),

-- Política
('política', 3),  -- Asumiendo que 3 es "Política"
('politics', 3),

-- Economía
('economía', 4),  -- Asumiendo que 4 es "Economía"
('economia', 4),
('business', 4),
('negocios', 4),

-- Deportes
('deportes', 5),  -- Asumiendo que 5 es "Deportes"
('sports', 5),
('deportivo', 5),

-- Tecnología
('tecnología', 6),  -- Asumiendo que 6 es "Tecnología"
('tecnologia', 6),
('tech', 6),
('ciencia', 6),
('science', 6),

-- Cultura / Entretenimiento
('cultura', 7),  -- Asumiendo que 7 es "Cultura"
('entretenimiento', 7),
('entertainment', 7),
('espectáculos', 7),
('espectaculos', 7),

-- Salud
('salud', 8),  -- Asumiendo que 8 es "Salud"
('health', 8),
('medicina', 8),

-- Educación
('educación', 9),  -- Asumiendo que 9 es "Educación"
('educacion', 9),
('education', 9);
