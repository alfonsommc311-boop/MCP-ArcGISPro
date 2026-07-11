# Empaquetado y firma del add-in (`.esriAddinX`) para distribución confiable

> El `.esriAddinX` es, por dentro, un ZIP. ArcGIS Pro decide si **confía** en un
> add-in según su **firma digital de Esri**, aplicada con la utilidad
> **`ESRISignAddIn.exe`** (incluida en el **ArcGIS Pro SDK for .NET**, no en Pro).
> NO uses `signtool` sobre el `.esriAddinX`: la confianza del add-in la gobierna la
> firma de Esri sobre el paquete, no la Authenticode del DLL. (Puedes, opcionalmente,
> Authenticode-firmar también el DLL interno.)

## 0. ¿Por qué firmar?

- Sin firma, Pro marca el add-in como **Untrusted** y muchas organizaciones lo
  **bloquean** por política (cargar solo add-ins de editores de confianza).
- Firmado + el certificado del editor en **Trusted Publishers** del cliente → el
  add-in carga **sin avisos** y es apto para despliegue corporativo.

---

## 1. Conseguir un certificado de firma de código

### A) Producción (recomendado) — certificado de una CA
- Compra un **Code Signing Certificate** (OV o EV) a una CA: DigiCert, Sectigo, GlobalSign…
- Desde 2023, el CA/Browser Forum exige que la **clave privada viva en hardware
  FIPS 140-2** (token USB) o en un **HSM/servicio de firma en la nube**. La firma se
  hace contra ese token/servicio.
- Ventaja: encadena a una **raíz ya confiable** en Windows → no hay que distribuir la raíz.

### B) Interno / pruebas — certificado autofirmado (PowerShell)
```powershell
# 1) Crear el certificado de firma (CurrentUser\My), válido 3 años
$cert = New-SelfSignedCertificate `
  -Type CodeSigningCert `
  -Subject "CN=Tu Empresa - MCP Bridge" `
  -KeyUsage DigitalSignature `
  -KeyAlgorithm RSA -KeyLength 3072 `
  -CertStoreLocation Cert:\CurrentUser\My `
  -NotAfter (Get-Date).AddYears(3)

# 2) Exportar el certificado PÚBLICO (.cer) para confiar en los clientes
Export-Certificate -Cert $cert -FilePath ".\MCPBridge-Publisher.cer"

# 3) (Opcional) Exportar a PFX con clave privada para firmar en otra máquina
$pwd = ConvertTo-SecureString "CAMBIA-ESTO" -Force -AsPlainText
Export-PfxCertificate -Cert $cert -FilePath ".\MCPBridge-Signing.pfx" -Password $pwd
```

---

## 2. Generar el paquete `.esriAddinX`

Al compilar el proyecto del Pro SDK en **Release**, los *build targets* de Esri generan
el `MCPBridge.esriAddinX` en la carpeta de salida (`bin\Release\…`). Verifica que
incluya `MCP_Bridge.pyt` y `pro_bridge.py` (marcados como *Content / Copy always*).

---

## 3. Firmar con `ESRISignAddIn.exe`

Ubicación tras instalar el SDK (confírmala): `C:\Program Files\ArcGIS\Pro\bin\ESRISignAddIn.exe`.

### Modo GUI (el más fiable)
1. Ejecuta `ESRISignAddIn.exe`.
2. **Add-in file:** selecciona `MCPBridge.esriAddinX`.
3. **Certificate:** elige desde el **almacén** (tu cert en `CurrentUser\My`) o desde
   **archivo PFX** (+ contraseña).
4. **Timestamp server (¡importante!):** p. ej. `http://timestamp.digicert.com`
   — el sellado de tiempo mantiene la firma válida aunque el certificado caduque.
5. **Sign.**

### Modo línea de comandos (para CI/automatizar)
La utilidad acepta parámetros, pero **los flags exactos varían por versión** —
confírmalos con:
```powershell
& "C:\Program Files\ArcGIS\Pro\bin\ESRISignAddIn.exe" /?
```
Forma típica documentada (verifícala con `/?`):
```powershell
& "C:\Program Files\ArcGIS\Pro\bin\ESRISignAddIn.exe" `
    ".\MCPBridge.esriAddinX" `
    /c:".\MCPBridge-Signing.pfx" /p:"CAMBIA-ESTO" `
    /t:"http://timestamp.digicert.com"
```
(Para firmar con un cert del almacén en lugar de PFX, usa la opción de *store/thumbprint*
que muestre la ayuda.)

---

## 4. Distribuir la confianza a las máquinas cliente

### Certificado de CA (producción)
- La raíz ya es de confianza. Según política, importa el cert del editor en
  **Trusted Publishers** para carga 100% silenciosa.

### Certificado autofirmado (interno)
Importa el **.cer público** en cada cliente (idealmente por **GPO**):
```powershell
# Raíz de confianza (porque el autofirmado no encadena a una CA pública)
Import-Certificate -FilePath ".\MCPBridge-Publisher.cer" -CertStoreLocation Cert:\LocalMachine\Root
# Editores de confianza
Import-Certificate -FilePath ".\MCPBridge-Publisher.cer" -CertStoreLocation Cert:\LocalMachine\TrustedPublisher
```
**Empresa (GPO):** Configuración del equipo → Configuración de Windows → Configuración
de seguridad → Directivas de clave pública → *Trusted Root Certification Authorities* y
*Trusted Publishers*.

---

## 5. (Opcional) Forzar que Pro solo cargue add-ins firmados/confiables

ArcGIS Pro → **Project → Options → Add-In Manager → Options**:
- Define las **carpetas** desde las que Pro busca add-ins.
- Activa la opción de **cargar solo add-ins de fuentes de confianza** (publisher firmado).
En despliegues gestionados esto se fija por política para toda la organización.

---

## 6. Verificar la firma

- En Pro: **Project → Options → Add-In Manager** → selecciona el add-in →
  comprueba **Digitally Signed = Yes** y el **Publisher** correcto.
- En Windows: clic derecho sobre el `.esriAddinX` extraído / DLL → *Propiedades →
  Firmas digitales* (si firmaste también el DLL).

---

## Checklist de release

- [ ] Compilar en **Release** → `MCPBridge.esriAddinX` con los `.py` incluidos
- [ ] Firmar con `ESRISignAddIn.exe` **+ timestamp**
- [ ] (Prod) Cert de CA en token/HSM · (Interno) `.cer` distribuido por GPO
- [ ] Verificar *Digitally Signed = Yes* en el Add-In Manager
- [ ] Probar en una máquina limpia (sin tu cert en `My`) que carga sin avisos
- [ ] Documentar versión de Pro soportada y versión del add-in
