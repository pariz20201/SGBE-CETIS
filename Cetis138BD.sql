CREATE DATABASE CETIS138 CHARACTER SET utf8mb4 COLLATE utf8mb4_spanish_ci;
USE CETIS138;

CREATE TABLE Libros(
    id_Libro INT AUTO_INCREMENT PRIMARY KEY,
    Codigo INT NOT NULL UNIQUE,
    Titulo VARCHAR(100) NOT NULL,
    Autor VARCHAR(100) NOT NULL,
    Cantidad INT NOT NULL CHECK (Cantidad >= 0),
    Genero VARCHAR(40) DEFAULT "Sin género",
    Descripcion TEXT DEFAULT NULL,
    Activo BOOLEAN NOT NULL DEFAULT 1
);

CREATE TABLE Usuarios(
    Id_Usuario INT AUTO_INCREMENT PRIMARY KEY,
    Nombre_Us VARCHAR(100) NOT NULL,
    Rol ENUM('Administrador','Bibliotecario','Alumno') NOT NULL,
    Contrasena VARCHAR(200) NOT NULL,
    Userlogin VARCHAR(50) NOT NULL UNIQUE
);

CREATE TABLE Alumnos(
    Id_Alumno INT PRIMARY KEY,
    Identificacion INT NOT NULL UNIQUE,
    Penalizaciones TEXT,
    Pen_Act BOOLEAN DEFAULT 0,
    FOREIGN KEY (Id_Alumno) REFERENCES Usuarios(Id_Usuario) ON DELETE CASCADE
);

CREATE TABLE Prestamos(
    Id_Prestamo INT AUTO_INCREMENT PRIMARY KEY,
    id_alum INT NOT NULL,
    id_libro INT NOT NULL,
    fecha_salida DATE,
    fecha_devolucion DATE DEFAULT NULL,
    estado BOOLEAN DEFAULT 0,
    fecha_entrada DATE,
    FOREIGN KEY (id_alum) REFERENCES Alumnos(Id_Alumno) ON DELETE CASCADE,
    FOREIGN KEY (id_libro) REFERENCES Libros(id_Libro) ON DELETE CASCADE
);