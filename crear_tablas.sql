-- 1. Tabla de Ciclos (El periodo de la cosecha, ej: 2026)
CREATE TABLE ciclos (
    id SERIAL PRIMARY KEY,
    nombre_ciclo VARCHAR(50) NOT NULL UNIQUE, -- Ej. "Ciclo 2026" o "Cosecha 2026"
    fecha_inicio DATE NOT NULL,
    fecha_fin DATE,
    descripcion TEXT,
    activo BOOLEAN DEFAULT TRUE -- Para saber cuál es el ciclo en curso
);

-- 2. Tabla de Ingresos (Ventas de nuez y subproductos)
CREATE TABLE ingresos (
    id SERIAL PRIMARY KEY,
    ciclo_id INT REFERENCES ciclos(id) ON DELETE CASCADE, -- Conecta el ingreso a un ciclo
    fecha DATE NOT NULL DEFAULT CURRENT_DATE,
    concepto VARCHAR(150) NOT NULL, -- Ej. "Venta Nuez Primera", "Venta Nuez Segunda"
    kilogramos NUMERIC(10, 2) NOT NULL, -- Control estricto de peso
    precio_por_kilo NUMERIC(10, 2) NOT NULL, -- Precio pactado
    total_ingreso NUMERIC(12, 2) GENERATED ALWAYS AS (kilogramos * precio_por_kilo) STORED, -- PostgreSQL lo calcula en automático
    notas TEXT
);

-- 3. Tabla de Egresos (Gastos operativos de la nogalera)
CREATE TABLE egresos (
    id SERIAL PRIMARY KEY,
    ciclo_id INT REFERENCES ciclos(id) ON DELETE CASCADE, -- Conecta el gasto a un ciclo
    fecha DATE NOT NULL DEFAULT CURRENT_DATE,
    categoria VARCHAR(100) NOT NULL, -- Ej. 'Riego', 'Fertilizantes', 'Mano de Obra', 'Combustible'
    monto NUMERIC(12, 2) NOT NULL,
    descripcion TEXT NOT NULL,
    proveedor VARCHAR(150)
);