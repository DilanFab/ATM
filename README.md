# Sistema de Cajero Automatizado

## Descripción
Este es un sistema de cajero automatizado desarrollado en Python que permite la gestión de clientes y sus transacciones bancarias. Ofrece funcionalidades como depósitos, retiros, transferencias, consulta de saldo y generación de reportes. También cuenta con un módulo de administración para gestionar clientes y configurar los datos del banco.

## Características
- Registro y autenticación de clientes.
- Manejo de claves de acceso con restablecimiento.
- Depósitos, retiros y transferencias entre clientes.
- Consulta de saldo con opción de impresión.
- Gestión de clientes y datos bancarios desde un panel de administrador.
- Registro y reporte de transacciones.

## Requisitos
### Software
- Python 3.6 o superior

### Dependencias
El sistema usa las siguientes bibliotecas:
- `os` (manejo de archivos y sistema operativo)
- `random` y `string` (generación de claves aleatorias)
- `datetime` y `time` (manejo de fechas y tiempos)
- `re` (validación de datos como correos electrónicos)
- `getpass` (lectura segura de contraseñas)
- `pyautogui` y `webbrowser` (automatización del envío de mensajes vía WhatsApp Web)

## Instalación
1. Clona este repositorio o descarga los archivos.
2. Instala las dependencias necesarias con:
   ```sh
   pip install pyautogui
   ```
3. Ejecuta el sistema con:
   ```sh
   python cajero_modificado.py
   ```

## Uso
### Inicio de Sesión
1. **Cliente:** Ingresa tu cédula y clave.
2. **Administrador:** Ingresa con el usuario `admin` y la clave predeterminada `2025` (puede cambiarse luego).

### Operaciones Disponibles
#### Cliente
- **Depositar:** Agrega saldo a la cuenta.
- **Retirar:** Extrae dinero con límite diario.
- **Consultar Saldo:** Verifica el saldo actual.
- **Transferencias:** Envía dinero a otros clientes.
- **Cambio de Clave:** Modifica la clave de acceso.

#### Administrador
- **Registrar datos del banco.**
- **Gestionar clientes:** Registrar, modificar, eliminar y restablecer claves.
- **Generar reportes de transacciones.**

## Archivos del Proyecto
- `cajero_modificado.py`: Código principal del sistema.
- `clientes.txt`: Base de datos de clientes.
- `banco.txt`: Información del banco.
- `transacciones.txt`: Registro de transacciones.

## Consideraciones de Seguridad
- Las claves se almacenan en texto plano (se recomienda cifrado en futuras versiones).
- Se usa WhatsApp Web para enviar notificaciones de transacciones.
- Implementa un límite de intentos fallidos antes de bloquear la cuenta.

## Contribuciones
Si deseas mejorar el proyecto, puedes enviar un pull request o reportar problemas en la sección de Issues.

## Licencia
Este proyecto se distribuye bajo la licencia MIT. Puedes usarlo y modificarlo libremente.

