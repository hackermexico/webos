# webos
Webshell para linux escrita en python3

🐚 Web Shell - Control Remoto

Este proyecto implementa un Web Shell seguro con interfaz web usando Flask, permitiendo ejecutar comandos en el sistema de manera remota, con distinción entre comandos básicos y comandos privilegiados (requieren un token de administrador).

⚠ ADVERTENCIA: Este código es únicamente para fines educativos, auditorías de seguridad y entornos controlados. No debe usarse en sistemas de producción ni en máquinas sin autorización expresa.

🚀 Características

Interfaz tipo terminal web con estilo retro (verde sobre negro).

Autenticación por token para ejecutar comandos privilegiados.

Ejecución de comandos básicos seguros sin necesidad de token:

ls, pwd, whoami, date, uname, ps, df, free, uptime

Ejecución de cualquier comando del sistema con token de administrador.

Información del sistema en tiempo real: hostname, usuario, directorio actual, UID/GID, etc.

Panel web interactivo con botones de ayuda, limpiar salida, listar archivos, etc.
