# Instalación de PARANOID

Este documento describe el proceso de instalación de PARANOID en sistemas Linux.
PARANOID es una herramienta de reconocimiento de red que **requiere permisos elevados**
para funcionar correctamente.

---

## 🖥️ Sistemas soportados

- Linux (probado en:
  - Kali Linux
  - Debian-based)
- Arquitectura x86_64
- Python 3.9 o superior

> ⚠️ No se recomienda su uso en contenedores o entornos virtuales muy restringidos.

---

## 📦 Dependencias del sistema

Antes de instalar PARANOID, asegúrate de contar con las siguientes herramientas:

### Requeridas
- `python3`
- `pip3`
- `nmap`

### Recomendadas
- `tcpdump` (para captura de tráfico)
- `iproute2`
- `net-tools`

### Instalación de dependencias (Debian / Kali)

```bash
sudo apt update
sudo apt install -y \
  python3 \
  python3-pip \
  nmap \
  tcpdump \
  iproute2 \
  net-tools
