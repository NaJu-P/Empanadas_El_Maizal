-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Servidor: 127.0.0.1
-- Tiempo de generación: 18-07-2025 a las 16:21:46
-- Versión del servidor: 10.4.32-MariaDB
-- Versión de PHP: 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Base de datos: `empanadas_el_maizal`
--

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `administrador`
--

CREATE TABLE `administrador` (
  `id_administrador` int(10) NOT NULL,
  `nombre_admin` varchar(100) NOT NULL,
  `email_admin` varchar(100) NOT NULL,
  `contrasena_admin` varchar(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_general_ci;

--
-- Volcado de datos para la tabla `administrador`
--

INSERT INTO `administrador` (`id_administrador`, `nombre_admin`, `email_admin`, `contrasena_admin`) VALUES
(1, 'Admin General', 'admin@maizal.com', 'scrypt:32768:8:1$curOCT1bHVh0CrfR$cfd39e79a833a22056c8b2fa410a087f4ffccc88a72b9d7ba5e336d44a562606fb417d7c9079f25ed00005008aa1ca656a3bde32e59314fc9ce2808ed4511ce2');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `detalle_facturacion`
--

CREATE TABLE `detalle_facturacion` (
  `id_detalle` int(11) NOT NULL,
  `cantidad_producto` int(11) NOT NULL,
  `id_factura` int(11) NOT NULL,
  `id_producto` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_general_ci;

--
-- Volcado de datos para la tabla `detalle_facturacion`
--

INSERT INTO `detalle_facturacion` (`id_detalle`, `cantidad_producto`, `id_factura`, `id_producto`) VALUES
(1, 8, 1, 1),
(2, 10, 1, 3),
(3, 1, 2, 1),
(4, 10, 2, 3),
(5, 5, 2, 6),
(6, 7, 3, 10),
(7, 12, 3, 14),
(8, 8, 4, 3),
(9, 9, 4, 10),
(10, 6, 4, 8),
(11, 4, 5, 3),
(12, 5, 6, 14),
(13, 6, 7, 10),
(14, 4, 7, 15),
(15, 27, 8, 8),
(16, 13, 9, 5),
(17, 6, 10, 1),
(18, 34, 11, 9),
(19, 37, 12, 10),
(20, 6, 13, 1),
(21, 6, 13, 12),
(22, 8, 13, 10),
(23, 20, 13, 3),
(24, 1, 14, 3),
(25, 2, 14, 2),
(26, 4, 15, 2),
(27, 3, 15, 3),
(31, 1, 16, 2),
(32, 3, 16, 4),
(33, 1, 16, 14),
(34, 11, 17, 2),
(35, 9, 18, 4),
(39, 1, 22, 4),
(40, 7, 23, 14),
(41, 9, 23, 2),
(42, 5, 23, 1),
(43, 7, 24, 2),
(44, 12, 24, 15),
(45, 6, 25, 14),
(46, 9, 25, 10),
(47, 9, 25, 5),
(48, 11, 26, 6),
(49, 6, 27, 9),
(50, 7, 28, 9),
(51, 6, 29, 10),
(52, 8, 30, 10),
(53, 11, 31, 52);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `domiciliario`
--

CREATE TABLE `domiciliario` (
  `id_domiciliario` int(11) NOT NULL,
  `nombres_domiciliario` varchar(50) NOT NULL,
  `email_domiciliario` varchar(70) NOT NULL,
  `contraseña_domiciliario` varchar(255) NOT NULL,
  `telefono` varchar(15) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_general_ci;

--
-- Volcado de datos para la tabla `domiciliario`
--

INSERT INTO `domiciliario` (`id_domiciliario`, `nombres_domiciliario`, `email_domiciliario`, `contraseña_domiciliario`, `telefono`) VALUES
(1029132112, 'Cristian', 'cristian@gmail.com', 'scrypt:32768:8:1$FsT0Wx7I5SV1y5YS$518bfe5464abafeca77beee1bd53653cc9331f81eb95d796176c296a75413260ca8577f4de2c4a88f6b926f77712a1d842e09a420cdaf49835fc3d7eaf433e53', '3201986547'),
(1283912312, 'ASD', 'asd@gmial.com', 'scrypt:32768:8:1$VBfZAq62qkVY4ShN$10124b50efbd3e23c05924bf8867a9b5a22e5eddf29803aa66fec085cc856d2c258b7436b0da211fade16db069bba09bbff985663d17616233c4b025dfcf60bf', '3201986547');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `facturacion`
--

CREATE TABLE `facturacion` (
  `id_factura` int(11) NOT NULL,
  `fecha_compra` date NOT NULL,
  `hora` time(6) NOT NULL,
  `id_pago` int(11) NOT NULL,
  `id_usuario` int(11) NOT NULL,
  `id_tipo_entrega` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_general_ci;

--
-- Volcado de datos para la tabla `facturacion`
--

INSERT INTO `facturacion` (`id_factura`, `fecha_compra`, `hora`, `id_pago`, `id_usuario`, `id_tipo_entrega`) VALUES
(1, '2025-07-14', '12:31:56.000000', 1, 1, 1),
(2, '2025-07-14', '19:23:44.000000', 2, 2, 2),
(3, '2025-07-14', '19:28:52.000000', 2, 3, 3),
(4, '2025-07-14', '20:36:28.000000', 1, 2, 4),
(5, '2025-07-01', '17:54:06.000000', 1, 2, 5),
(6, '2025-07-01', '17:54:47.000000', 2, 2, 6),
(7, '2025-07-01', '17:58:01.000000', 2, 2, 7),
(8, '2025-07-01', '18:02:59.000000', 2, 2, 8),
(9, '2025-07-15', '18:34:14.000000', 1, 2, 9),
(10, '2025-07-15', '18:35:05.000000', 2, 2, 10),
(11, '2025-01-01', '18:40:46.000000', 1, 2, 11),
(12, '2025-07-15', '19:12:43.000000', 1, 2, 12),
(13, '2025-07-15', '21:25:04.000000', 1, 2, 13),
(14, '2025-07-15', '23:01:47.000000', 2, 2, 14),
(15, '2025-07-15', '23:05:37.000000', 2, 2, 15),
(16, '2025-07-15', '23:26:01.000000', 1, 2, 16),
(17, '2025-07-16', '00:13:06.000000', 2, 2, 17),
(18, '2025-07-16', '00:14:24.000000', 2, 2, 18),
(22, '2025-07-16', '01:07:06.000000', 1, 2, 22),
(23, '2025-07-16', '10:13:55.000000', 2, 2, 23),
(24, '2025-07-16', '14:16:54.000000', 2, 2, 24),
(25, '2025-07-16', '14:22:54.000000', 1, 2, 25),
(26, '2025-07-16', '14:35:19.000000', 2, 2, 26),
(27, '2025-07-16', '14:40:58.000000', 2, 2, 27),
(28, '2025-07-16', '14:47:45.000000', 2, 2, 28),
(29, '2025-07-16', '14:52:23.000000', 1, 2, 29),
(30, '2025-07-16', '19:25:54.000000', 2, 2, 30),
(31, '2025-07-18', '07:19:27.000000', 2, 2, 31);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `fecha_opinion`
--

CREATE TABLE `fecha_opinion` (
  `id_fecha_opinion` int(11) NOT NULL,
  `id_opiniones` int(11) NOT NULL,
  `fecha_opinion` date NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `metodo_pago`
--

CREATE TABLE `metodo_pago` (
  `id_pago` int(11) NOT NULL,
  `nombre_pago` varchar(50) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_general_ci;

--
-- Volcado de datos para la tabla `metodo_pago`
--

INSERT INTO `metodo_pago` (`id_pago`, `nombre_pago`) VALUES
(1, 'daviplata'),
(2, 'Nequi'),
(3, 'no_pago');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `opiniones`
--

CREATE TABLE `opiniones` (
  `id_opiniones` int(11) NOT NULL,
  `calificacion` decimal(3,0) NOT NULL,
  `descripcion_opinion` mediumtext NOT NULL,
  `fecha_creacion` datetime DEFAULT current_timestamp(),
  `publicar` tinyint(1) DEFAULT 0,
  `id_usuario` int(11) DEFAULT NULL,
  `id_producto` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_general_ci;

--
-- Volcado de datos para la tabla `opiniones`
--

INSERT INTO `opiniones` (`id_opiniones`, `calificacion`, `descripcion_opinion`, `fecha_creacion`, `publicar`, `id_usuario`, `id_producto`) VALUES
(1, 4, 'ASFASDASDwqejqweqweqwe123123', '2025-07-14 12:38:12', 1, 1, 2),
(2, 3, 'mucho atun pero me parecio increible la empanada', '2025-07-14 19:57:24', 1, 2, 14),
(3, 3, 'noghdfgfsdddfdfsdfdfdfdfassdf', '2025-07-16 10:54:45', 1, 2, 14),
(4, 4, 'mucho picate pero la entrega me sorprendio su rapidez y entrega y lo demas esta bien aqui', '2025-07-16 22:35:41', 1, 1, 5);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `producto`
--

CREATE TABLE `producto` (
  `id_producto` int(11) NOT NULL,
  `nombre_producto` mediumtext NOT NULL,
  `cantidad_disponible` int(11) NOT NULL,
  `id_tipo_producto` int(11) NOT NULL,
  `precio_producto` float NOT NULL,
  `img_producto` varchar(50) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_general_ci;

--
-- Volcado de datos para la tabla `producto`
--

INSERT INTO `producto` (`id_producto`, `nombre_producto`, `cantidad_disponible`, `id_tipo_producto`, `precio_producto`, `img_producto`) VALUES
(1, 'Empanada de Carne Molida', 173, 1, 1500, 'empanada-de-carne-molida.webp'),
(2, 'Empanada de Pollo', 83, 2, 1600, 'empanada-de-pollo.webp'),
(3, 'Empanada de Queso', 25, 3, 1400, 'empanada_queso.webp'),
(4, 'Empanada de Papa', 0, 4, 1200, 'empanada_papa.webp'),
(5, 'Empanada Mexicana', 37, 5, 2000, 'empanada_mexicana.webp'),
(6, 'Empanada Árabe', 19, 6, 2500, 'empanada_arabe.webp'),
(7, 'Empanada Vegana', 70, 7, 1800, 'empanada_vegana.webp'),
(8, 'Empanada Integral', 60, 8, 1700, 'empanada_integral.webp'),
(9, 'Empanada Picante', 67, 9, 1900, 'empanada_picante.webp'),
(10, 'Empanada Dulce', 47, 10, 1600, 'empanada_dulce.webp'),
(11, 'Empanada con Guacamole', 101, 11, 2200, 'empanada_guacamole.webp'),
(12, 'Empanada Gourmet', 40, 12, 3000, 'empanada_gourmet.webp'),
(13, 'Empanada Especial', 70, 13, 2400, 'empanada_especial.webp'),
(14, 'Empanada de Atún', 37, 14, 2000, 'empanada_atun.webp'),
(15, 'Empanada Colombiana', 118, 15, 1800, 'empanada_colombiana.webp'),
(51, 'Empanada de harina', 150, 51, 2000, 'Empanada_Pollo.jpeg'),
(52, 'empanada empanda', 139, 52, 1500, 'Empanada_hawaiana.jpg');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `reiniciar_contrasena_tokens`
--

CREATE TABLE `reiniciar_contrasena_tokens` (
  `id` int(11) NOT NULL,
  `id_usuario` int(11) NOT NULL,
  `email_usuario` varchar(255) NOT NULL,
  `token` varchar(255) NOT NULL,
  `expires_at` datetime NOT NULL,
  `used` tinyint(1) DEFAULT 0,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `telefono`
--

CREATE TABLE `telefono` (
  `id_telefono` int(11) NOT NULL,
  `id_domiciliario` int(11) NOT NULL,
  `telefono` bigint(20) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `tipo_entrega`
--

CREATE TABLE `tipo_entrega` (
  `id_tipo_entrega` int(11) NOT NULL,
  `id_domiciliario` int(11) NOT NULL,
  `estado_entrega` varchar(50) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_general_ci;

--
-- Volcado de datos para la tabla `tipo_entrega`
--

INSERT INTO `tipo_entrega` (`id_tipo_entrega`, `id_domiciliario`, `estado_entrega`) VALUES
(1, 1029132112, 'entregado'),
(2, 1029132112, 'no entregado'),
(3, 1283912312, 'no entregado'),
(4, 1029132112, 'no entregado'),
(5, 1283912312, 'no entregado'),
(6, 1283912312, 'no entregado'),
(7, 1029132112, 'no entregado'),
(8, 1029132112, 'no entregado'),
(9, 1283912312, 'no entregado'),
(10, 1029132112, 'no entregado'),
(11, 1283912312, 'no entregado'),
(12, 1283912312, 'no entregado'),
(13, 1283912312, 'no entregado'),
(14, 1283912312, 'no entregado'),
(15, 1283912312, 'no entregado'),
(16, 1283912312, 'no entregado'),
(17, 1283912312, 'no entregado'),
(18, 1283912312, 'no entregado'),
(19, 1283912312, 'no entregado'),
(20, 1029132112, 'no entregado'),
(21, 1283912312, 'no entregado'),
(22, 1029132112, 'no entregado'),
(23, 1283912312, 'no entregado'),
(24, 1029132112, 'no entregado'),
(25, 1029132112, 'no entregado'),
(26, 1029132112, 'no entregado'),
(27, 1029132112, 'no entregado'),
(28, 1283912312, 'no entregado'),
(29, 1283912312, 'no entregado'),
(30, 1029132112, 'entregado'),
(31, 1283912312, 'no entregado');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `tipo_producto`
--

CREATE TABLE `tipo_producto` (
  `id_tipo_producto` int(11) NOT NULL,
  `descripcion_producto` mediumtext NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_general_ci;

--
-- Volcado de datos para la tabla `tipo_producto`
--

INSERT INTO `tipo_producto` (`id_tipo_producto`, `descripcion_producto`) VALUES
(1, 'Empanada de carne jugosa y bien sazonada, perfecta para cualquier ocasión.'),
(2, 'Clásica y tradicional, con un relleno jugoso de pollo desmenuzado, pimientos dulces y un suave toque de comino.'),
(3, 'Deliciosa empanada con mezcla de quesos fundidos, perfecta para los amantes del queso que buscan un bocado cremoso y lleno de sabor.'),
(4, 'Masa dorada al horno, rellena con papas especiadas, cebollín y un delicado toque de pimentón ahumado.'),
(5, 'Explosión de sabores con carne sazonada al estilo mexicano, jalapeños frescos y queso cheddar fundido.'),
(6, 'Exquisito relleno de carne con un toque de canela y pimienta árabe, combinada con piñones y perejil fresco.'),
(7, 'Rellena de vegetales frescos salteados, garbanzos especiados y un toque de salsa tahini para un sabor 100% vegetal y nutritivo.'),
(8, 'Masa integral crujiente rellena de un mix de vegetales y granos, perfecta para quienes cuidan su alimentación sin sacrificar sabor.'),
(9, 'Para los valientes: carne jugosa con ají rojo, chiles y un toque de sriracha, todo envuelto en masa dorada.'),
(10, 'Delicada empanada elaborada con una suave masa de harina de trigo, rellena con dulce bocadillo de guayaba. Perfecta como postre o para disfrutar en cualquier momento del día.'),
(11, 'Original y fresca, rellena con guacamole casero, maíz tierno y un toque de limón para realzar el sabor.'),
(12, 'Creación exclusiva con lomo fino salteado, champiñones al vino y un toque de trufa negra.'),
(13, 'Receta secreta de la casa, rellena con una combinación única de carnes y vegetales con especias selectas.'),
(14, 'Rellena de atún fresco, aceitunas negras y huevo duro, con un toque de orégano para un sabor mediterráneo.'),
(15, 'Empanada tradicional con carne molida, papa criolla y un toque de ají casero, como hecha en casa.'),
(51, 'tiene harina que no es harina'),
(52, 'uan empanada que parece hawayana');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `ubicacion`
--

CREATE TABLE `ubicacion` (
  `id_ubicacion` int(11) NOT NULL,
  `id_usuario` int(11) NOT NULL,
  `direccion_usuario` varchar(50) NOT NULL,
  `ciudad` varchar(80) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `ubicacion`
--

INSERT INTO `ubicacion` (`id_ubicacion`, `id_usuario`, `direccion_usuario`, `ciudad`) VALUES
(1, 1, 'Avenida calle 64 diagonal 8', 'No especificada'),
(2, 2, 'Calle 12 int 8', 'No especificada'),
(3, 3, 'Calle 4 51 0601 barrio las nieves', 'No especificada');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `usuario`
--

CREATE TABLE `usuario` (
  `id_usuario` int(11) NOT NULL,
  `nombres_usuario` mediumtext NOT NULL,
  `apellidos_usuario` mediumtext NOT NULL,
  `email_usuario` varchar(70) NOT NULL,
  `contraseña` varchar(200) NOT NULL,
  `fecha_nacimiento` date NOT NULL,
  `telefono` bigint(20) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_general_ci;

--
-- Volcado de datos para la tabla `usuario`
--

INSERT INTO `usuario` (`id_usuario`, `nombres_usuario`, `apellidos_usuario`, `email_usuario`, `contraseña`, `fecha_nacimiento`, `telefono`) VALUES
(1, 'David', 'Sebastian', '', 'scrypt:32768:8:1$yYAvTlSZuLkaqc4A$3d5b9672fef84a977f756b7f8d36902b2dd4dde8a4e1beb963f078b31d199d5d2db6ec15b13f4e3e441e98355bd6ace4e8a3dba6c3bfa876ca43a26b6b1f6213', '2025-07-14', 3201986549),
(2, 'Fernando', 'Gomez', 'fernando.castro@example.com', 'scrypt:32768:8:1$D70eByex0DoSOXDK$2ded852d41b59ca1c08e64f9221437befa3a6caefcb1eec17cf7553361909261f4ea951ec5c0364a080989ec30dfc14853eda349b7f0615a361d854d487d308d', '2025-07-14', 3754467880),
(3, 'Juan', 'No se', 'juan@gmail.com', 'scrypt:32768:8:1$vMruFLupVS4ICYDb$d6e15790678fc89cc33abbfbbb32e4ef602b6234f1f384b793ad13f911686db46fd8540ab98fcbbb723aedb4603632e8540682c0546d534d0762283e9a259ebb', '2025-07-14', 3109888656);

--
-- Índices para tablas volcadas
--

--
-- Indices de la tabla `administrador`
--
ALTER TABLE `administrador`
  ADD PRIMARY KEY (`id_administrador`);

--
-- Indices de la tabla `detalle_facturacion`
--
ALTER TABLE `detalle_facturacion`
  ADD PRIMARY KEY (`id_detalle`),
  ADD KEY `id_factura` (`id_factura`,`id_producto`),
  ADD KEY `id_producto` (`id_producto`);

--
-- Indices de la tabla `domiciliario`
--
ALTER TABLE `domiciliario`
  ADD PRIMARY KEY (`id_domiciliario`);

--
-- Indices de la tabla `facturacion`
--
ALTER TABLE `facturacion`
  ADD PRIMARY KEY (`id_factura`),
  ADD KEY `codigo_pago` (`id_pago`),
  ADD KEY `id_usuario` (`id_usuario`),
  ADD KEY `id_pago` (`id_pago`),
  ADD KEY `id_tipo_entrega` (`id_tipo_entrega`);

--
-- Indices de la tabla `fecha_opinion`
--
ALTER TABLE `fecha_opinion`
  ADD PRIMARY KEY (`id_fecha_opinion`),
  ADD KEY `id_opinion` (`id_opiniones`);

--
-- Indices de la tabla `metodo_pago`
--
ALTER TABLE `metodo_pago`
  ADD PRIMARY KEY (`id_pago`);

--
-- Indices de la tabla `opiniones`
--
ALTER TABLE `opiniones`
  ADD PRIMARY KEY (`id_opiniones`),
  ADD KEY `id_usuario` (`id_usuario`,`id_producto`),
  ADD KEY `id_producto` (`id_producto`);

--
-- Indices de la tabla `producto`
--
ALTER TABLE `producto`
  ADD PRIMARY KEY (`id_producto`),
  ADD KEY `ID_tipo_producto` (`id_tipo_producto`);

--
-- Indices de la tabla `reiniciar_contrasena_tokens`
--
ALTER TABLE `reiniciar_contrasena_tokens`
  ADD PRIMARY KEY (`id`),
  ADD KEY `id_usuario` (`id_usuario`);

--
-- Indices de la tabla `telefono`
--
ALTER TABLE `telefono`
  ADD PRIMARY KEY (`id_telefono`),
  ADD KEY `id_domiciliario` (`id_domiciliario`);

--
-- Indices de la tabla `tipo_entrega`
--
ALTER TABLE `tipo_entrega`
  ADD PRIMARY KEY (`id_tipo_entrega`),
  ADD KEY `id_domiciliario` (`id_domiciliario`);

--
-- Indices de la tabla `tipo_producto`
--
ALTER TABLE `tipo_producto`
  ADD PRIMARY KEY (`id_tipo_producto`);

--
-- Indices de la tabla `ubicacion`
--
ALTER TABLE `ubicacion`
  ADD PRIMARY KEY (`id_ubicacion`),
  ADD KEY `id_usuario` (`id_usuario`);

--
-- Indices de la tabla `usuario`
--
ALTER TABLE `usuario`
  ADD PRIMARY KEY (`id_usuario`);

--
-- AUTO_INCREMENT de las tablas volcadas
--

--
-- AUTO_INCREMENT de la tabla `detalle_facturacion`
--
ALTER TABLE `detalle_facturacion`
  MODIFY `id_detalle` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=54;

--
-- AUTO_INCREMENT de la tabla `facturacion`
--
ALTER TABLE `facturacion`
  MODIFY `id_factura` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=32;

--
-- AUTO_INCREMENT de la tabla `fecha_opinion`
--
ALTER TABLE `fecha_opinion`
  MODIFY `id_fecha_opinion` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `metodo_pago`
--
ALTER TABLE `metodo_pago`
  MODIFY `id_pago` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=53;

--
-- AUTO_INCREMENT de la tabla `opiniones`
--
ALTER TABLE `opiniones`
  MODIFY `id_opiniones` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;

--
-- AUTO_INCREMENT de la tabla `producto`
--
ALTER TABLE `producto`
  MODIFY `id_producto` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=53;

--
-- AUTO_INCREMENT de la tabla `reiniciar_contrasena_tokens`
--
ALTER TABLE `reiniciar_contrasena_tokens`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=41;

--
-- AUTO_INCREMENT de la tabla `telefono`
--
ALTER TABLE `telefono`
  MODIFY `id_telefono` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=345;

--
-- AUTO_INCREMENT de la tabla `tipo_entrega`
--
ALTER TABLE `tipo_entrega`
  MODIFY `id_tipo_entrega` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=32;

--
-- AUTO_INCREMENT de la tabla `tipo_producto`
--
ALTER TABLE `tipo_producto`
  MODIFY `id_tipo_producto` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=53;

--
-- AUTO_INCREMENT de la tabla `ubicacion`
--
ALTER TABLE `ubicacion`
  MODIFY `id_ubicacion` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;

--
-- AUTO_INCREMENT de la tabla `usuario`
--
ALTER TABLE `usuario`
  MODIFY `id_usuario` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;

--
-- Restricciones para tablas volcadas
--

--
-- Filtros para la tabla `detalle_facturacion`
--
ALTER TABLE `detalle_facturacion`
  ADD CONSTRAINT `detalle_facturacion_ibfk_2` FOREIGN KEY (`id_producto`) REFERENCES `producto` (`id_producto`) ON DELETE CASCADE ON UPDATE CASCADE,
  ADD CONSTRAINT `detalle_facturacion_ibfk_3` FOREIGN KEY (`id_factura`) REFERENCES `facturacion` (`id_factura`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Filtros para la tabla `facturacion`
--
ALTER TABLE `facturacion`
  ADD CONSTRAINT `facturacion_ibfk_2` FOREIGN KEY (`id_pago`) REFERENCES `metodo_pago` (`id_pago`) ON DELETE CASCADE ON UPDATE CASCADE,
  ADD CONSTRAINT `facturacion_ibfk_3` FOREIGN KEY (`id_usuario`) REFERENCES `usuario` (`id_usuario`) ON DELETE CASCADE ON UPDATE CASCADE,
  ADD CONSTRAINT `facturacion_ibfk_4` FOREIGN KEY (`id_tipo_entrega`) REFERENCES `tipo_entrega` (`id_tipo_entrega`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Filtros para la tabla `fecha_opinion`
--
ALTER TABLE `fecha_opinion`
  ADD CONSTRAINT `fecha_opinion_ibfk_1` FOREIGN KEY (`id_opiniones`) REFERENCES `opiniones` (`id_opiniones`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Filtros para la tabla `opiniones`
--
ALTER TABLE `opiniones`
  ADD CONSTRAINT `opiniones_ibfk_3` FOREIGN KEY (`id_producto`) REFERENCES `producto` (`id_producto`) ON DELETE CASCADE ON UPDATE CASCADE,
  ADD CONSTRAINT `opiniones_ibfk_4` FOREIGN KEY (`id_usuario`) REFERENCES `usuario` (`id_usuario`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Filtros para la tabla `producto`
--
ALTER TABLE `producto`
  ADD CONSTRAINT `producto_ibfk_1` FOREIGN KEY (`id_tipo_producto`) REFERENCES `tipo_producto` (`id_tipo_producto`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Filtros para la tabla `reiniciar_contrasena_tokens`
--
ALTER TABLE `reiniciar_contrasena_tokens`
  ADD CONSTRAINT `reiniciar_contrasena_tokens_ibfk_1` FOREIGN KEY (`id_usuario`) REFERENCES `usuario` (`id_usuario`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Filtros para la tabla `tipo_entrega`
--
ALTER TABLE `tipo_entrega`
  ADD CONSTRAINT `tipo_entrega_ibfk_1` FOREIGN KEY (`id_domiciliario`) REFERENCES `domiciliario` (`id_domiciliario`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Filtros para la tabla `ubicacion`
--
ALTER TABLE `ubicacion`
  ADD CONSTRAINT `ubicacion_ibfk_1` FOREIGN KEY (`id_usuario`) REFERENCES `usuario` (`id_usuario`) ON DELETE CASCADE ON UPDATE CASCADE;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
