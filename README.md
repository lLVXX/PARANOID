# 🟦 PARANOID — BLUE

> **Context-aware Nmap reconnaissance framework with traffic intelligence and Active Directory awareness**

PARANOID es una herramienta de **reconocimiento de red avanzada**, diseñada como un wrapper inteligente sobre **Nmap**, que combina análisis activo y pasivo para entregar **contexto real**, reducir ruido y mantener **control humano total** sobre cada acción.

PARANOID **no es un exploit framework**.
No ejecuta ataques.
No toma decisiones ofensivas por el usuario.

> PARANOID **observa, correlaciona y contextualiza**.

---

## ✨ Características principales

* Wrapper avanzado para Nmap
* Modos de escaneo integrados:

  * Quick Scan
  * Full Scan
  * Service Scan
  * Stealth Scan
* Análisis pasivo de tráfico en tiempo real:

  * PPS (Packets Per Second)
  * RTT estimado
  * Retransmisiones
  * Nivel de ruido
  * Indicadores de posible firewall
* Detección automática de hostnames:

  * Certificados TLS (CN / SAN)
  * HTTP redirects
* **Conciencia de Active Directory**:

  * Identificación de Domain Controllers
  * Detección de dominio raíz AD
* Gestión opcional de `/etc/hosts`:

  * Hostnames confirmados
  * Hostnames inferidos
* Selección manual de interfaz de red:

  * `eth0`, `wlan0`, `tun0`, etc.
* Resultados organizados por objetivo

---

## 🧠 Filosofía del proyecto

PARANOID sigue un principio simple:

> **Más contexto, menos ruido.**
> **Más control humano, menos automatización ciega.**

La herramienta entrega información **clara, correlacionada y accionable**, sin asumir intención ofensiva ni ejecutar acciones destructivas.

---

## 🖥️ Requisitos

* Linux (probado en Kali Linux y Debian-based)
* Arquitectura x86_64
* Python 3.9 o superior
* Nmap instalado
* Permisos de root (requeridos para):

  * Escaneos SYN
  * Captura pasiva de tráfico
  * Acceso a interfaces de red
  * Modificación opcional de `/etc/hosts`

> ⚠️ No se recomienda el uso de PARANOID en contenedores Docker o entornos virtuales altamente restringidos.

---

## 🚀 Instalación rápida

```bash
git clone https://github.com/lLVXX/PARANOID.git
cd PARANOID
pip3 install -r requirements.txt
sudo python3 r-recon.py
```

📘 Guía completa de instalación:
👉 [INSTALL.md](INSTALL.md)

---

## 🧪 Flujo de uso básico

1. Seleccionar interfaz de red
2. Definir target (IP o red)
3. Elegir tipo de escaneo
4. Analizar:

   * Puertos
   * Hostnames
   * Tráfico
   * Contexto del objetivo

Los resultados se almacenan automáticamente en:

```
results/<target>/
```

---

## 📚 Documentación

* 📦 [Guía de instalación](INSTALL.md)
* ⚠️ [Disclaimer legal](DISCLAIMER.md)
* 📄 [Licencia](LICENSE)

---

## ⚠️ Advertencia legal

PARANOID está destinado **exclusivamente** a:

* Auditorías autorizadas
* Laboratorios
* Investigación
* Aprendizaje

El uso de esta herramienta contra sistemas sin autorización explícita **puede ser ilegal**.

Consulta el archivo:
👉 [DISCLAIMER.md](DISCLAIMER.md)

---

## 📄 Licencia

Este proyecto se distribuye bajo la licencia **MIT**.

Consulta:
👉 [LICENSE](LICENSE)

---

## 🟦 Estado del proyecto

* Versión actual: **PARANOID 2.0 — BLUE**
* Estado: estable / en evolución
* Enfoque: madurez, claridad y cumplimiento legal

---

> **PARANOID no ataca.**
> **PARANOID entiende.**
