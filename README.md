# Mini CRM para Emprendedores

Web app simple para gestionar clientes, contactos y notas. Ideal para freelancers y pequeños negocios que necesitan una solución liviana sin complicaciones.

## Funcionalidades

- Registro de clientes con nombre, empresa, email y teléfono
- Estados por cliente: **Lead**, **Activo** o **Inactivo**
- Notas e historial de interacciones por cliente
- Buscador por nombre, empresa o email
- Filtro por estado
- Dashboard con gráfico de clientes por estado
- Login y registro de usuarios con contraseña encriptada

## Demo en vivo

[https://web-production-16cf7.up.railway.app](https://web-production-16cf7.up.railway.app)

## Requisitos

- Python 3.8 o superior

## Instalación

**1. Clona el repositorio:**
```bash
git clone https://github.com/DavidPm2405/mini-crm.git
cd mini-crm
```

**2. Instala las dependencias:**
```bash
pip install -r requirements.txt
```

**3. Corre la app:**
```bash
python minicrm.py
```

**4. Abre el navegador en:**
```
http://localhost:5000
```

**5. Regístrate con usuario y contraseña y listo.**

## Cómo usar

### Agregar un cliente
1. Clic en **"Nuevo cliente"** en el menú
2. Completa nombre, empresa, email, teléfono y estado
3. Clic en **"Guardar"**

### Registrar una nota o interacción
1. Entra al perfil del cliente
2. Escribe la nota en el campo de texto (ej: "Llamada realizada, interesado en propuesta")
3. Clic en **"Agregar nota"**

### Cambiar el estado de un cliente
1. Entra al perfil del cliente
2. Clic en **"Editar"**
3. Cambia el estado entre Lead / Activo / Inactivo

### Buscar clientes
- Usa la barra de búsqueda para encontrar por nombre, empresa o email
- Filtra por estado con el selector

## Tecnologías usadas

- Python + Flask
- SQLite (base de datos local)
- Bootstrap 5 (diseño)
- Chart.js (gráfico del dashboard)
