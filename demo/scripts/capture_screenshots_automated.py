#!/usr/bin/env python3
"""
Script automatizado para capturar screenshots del sistema usando Playwright.
Útil para entornos sin GUI o para automatización CI/CD.

Requisitos:
    pip install playwright
    playwright install chromium

Uso:
    python capture_screenshots_automated.py
"""

import asyncio
import os
from pathlib import Path
from playwright.async_api import async_playwright

# Configuración
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
GRAPHQL_URL = f"{BACKEND_URL}/api/graphql/"
OUTPUT_DIR = Path(__file__).parent.parent / "screenshots"
VIEWPORT_SIZE = {"width": 1920, "height": 1080}

# Credenciales demo
ADMIN_USER = "admin.demo"
ADMIN_PASS = "Demo2025!"
REVIEWER_USER = "revisor.demo"
REVIEWER_PASS = "Demo2025!"

# Crear directorio de salida
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


async def wait_for_load(page, timeout=10000):
    """Esperar a que la página cargue completamente"""
    try:
        await page.wait_for_load_state("networkidle", timeout=timeout)
    except Exception as e:
        print(f"   ⚠️  Timeout esperando carga completa: {e}")
        await asyncio.sleep(2)  # Esperar 2 segundos adicionales


async def login(page, username, password):
    """Realizar login en el sistema"""
    print(f"   🔐 Login como {username}...")
    
    try:
        # Navegar a login
        await page.goto(f"{FRONTEND_URL}/login")
        await wait_for_load(page)
        
        # Rellenar formulario
        await page.fill('input[name="username"], input[type="text"]', username)
        await page.fill('input[name="password"], input[type="password"]', password)
        
        # Click submit
        await page.click('button[type="submit"]')
        await wait_for_load(page)
        
        print(f"   ✓ Login exitoso")
        return True
        
    except Exception as e:
        print(f"   ❌ Error en login: {e}")
        return False


async def capture_screenshot(page, filename, full_page=False):
    """Capturar screenshot y guardar"""
    filepath = OUTPUT_DIR / filename
    try:
        await page.screenshot(path=str(filepath), full_page=full_page)
        file_size = filepath.stat().st_size / 1024  # KB
        print(f"   ✅ Capturado: {filename} ({file_size:.1f} KB)")
        return True
    except Exception as e:
        print(f"   ❌ Error capturando {filename}: {e}")
        return False


async def screenshot_dashboard(page):
    """Screenshot 1: Dashboard Principal"""
    print("\n📸 Screenshot 1: Dashboard Principal")
    
    try:
        await page.goto(f"{FRONTEND_URL}/dashboard")
        await wait_for_load(page)
        await asyncio.sleep(1)  # Esperar animaciones
        
        return await capture_screenshot(page, "01-dashboard.png")
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False


async def screenshot_document_viewer(page):
    """Screenshot 2: Visor de Documentos"""
    print("\n📸 Screenshot 2: Visor de Documentos")
    
    try:
        # Navegar a primer documento (ajustar según tu routing)
        await page.goto(f"{FRONTEND_URL}/documents/1")
        await wait_for_load(page)
        await asyncio.sleep(2)  # Esperar rendering de PDF
        
        return await capture_screenshot(page, "02-document-viewer.png")
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False


async def screenshot_annotations(page):
    """Screenshot 3: Sistema de Anotaciones"""
    print("\n📸 Screenshot 3: Sistema de Anotaciones")
    
    try:
        # Login como revisor si es necesario
        await login(page, REVIEWER_USER, REVIEWER_PASS)
        
        # Navegar a documento con anotaciones
        await page.goto(f"{FRONTEND_URL}/documents/2")
        await wait_for_load(page)
        await asyncio.sleep(2)
        
        # Intentar abrir sidebar de anotaciones (ajustar selector)
        try:
            await page.click('button[aria-label="Annotations"], .annotations-toggle')
            await asyncio.sleep(1)
        except:
            pass
        
        return await capture_screenshot(page, "03-annotations.png")
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False


async def screenshot_comparison(page):
    """Screenshot 4: Comparación de Documentos"""
    print("\n📸 Screenshot 4: Comparación de Documentos")
    
    try:
        await page.goto(f"{FRONTEND_URL}/comparison")
        await wait_for_load(page)
        await asyncio.sleep(2)
        
        return await capture_screenshot(page, "04-comparison.png")
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False


async def screenshot_graphql(page):
    """Screenshot 5: GraphQL Playground"""
    print("\n📸 Screenshot 5: GraphQL Playground")
    
    try:
        await page.goto(GRAPHQL_URL)
        await wait_for_load(page)
        await asyncio.sleep(2)
        
        # Intentar escribir query de ejemplo
        try:
            query = """query GetDocuments {
  documents(limit: 5) {
    id
    title
    version
    status
  }
}"""
            # Buscar el editor de GraphQL (ajustar selector)
            await page.fill('.graphiql-editor textarea, .CodeMirror textarea', query)
            await asyncio.sleep(1)
            
            # Click en execute (ajustar selector)
            await page.click('button[title="Execute"], .execute-button')
            await asyncio.sleep(1)
        except Exception as e:
            print(f"   ⚠️  No se pudo interactuar con playground: {e}")
        
        return await capture_screenshot(page, "05-graphql-playground.png", full_page=True)
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False


async def screenshot_placeholder(filename, text):
    """Crear screenshot placeholder para features no implementadas"""
    print(f"\n📸 Screenshot Placeholder: {text}")
    
    try:
        from PIL import Image, ImageDraw, ImageFont
        
        # Crear imagen en blanco
        img = Image.new('RGB', (1920, 1080), color=(243, 244, 246))
        draw = ImageDraw.Draw(img)
        
        # Agregar texto
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 48)
        except:
            font = ImageFont.load_default()
        
        text_lines = [
            text,
            "",
            "Feature pendiente de implementación",
            "o captura manual requerida"
        ]
        
        y_offset = 400
        for line in text_lines:
            bbox = draw.textbbox((0, 0), line, font=font)
            text_width = bbox[2] - bbox[0]
            x = (1920 - text_width) // 2
            draw.text((x, y_offset), line, fill=(107, 114, 128), font=font)
            y_offset += 80
        
        # Guardar
        filepath = OUTPUT_DIR / filename
        img.save(filepath)
        print(f"   ✅ Placeholder creado: {filename}")
        return True
        
    except Exception as e:
        print(f"   ❌ Error creando placeholder: {e}")
        return False


async def main():
    """Función principal"""
    print("=" * 70)
    print("📸 CAPTURA AUTOMATIZADA DE SCREENSHOTS")
    print("=" * 70)
    print()
    print(f"Frontend URL: {FRONTEND_URL}")
    print(f"Backend URL: {BACKEND_URL}")
    print(f"Output: {OUTPUT_DIR}")
    print()
    
    # Verificar que servicios estén corriendo
    print("🔍 Verificando servicios...")
    try:
        import requests
        
        # Check backend
        try:
            r = requests.get(f"{BACKEND_URL}/health", timeout=5)
            if r.status_code == 200:
                print(f"   ✓ Backend: OK")
            else:
                print(f"   ⚠️  Backend: Responde pero status {r.status_code}")
        except:
            print(f"   ❌ Backend: No responde en {BACKEND_URL}")
            print(f"   💡 Iniciar con: cd backend && uvicorn app.main:app --reload")
        
        # Check frontend
        try:
            r = requests.get(FRONTEND_URL, timeout=5)
            if r.status_code == 200:
                print(f"   ✓ Frontend: OK")
            else:
                print(f"   ⚠️  Frontend: Responde pero status {r.status_code}")
        except:
            print(f"   ❌ Frontend: No responde en {FRONTEND_URL}")
            print(f"   💡 Iniciar con: cd frontend && npm run dev")
            print()
            print("   ⚠️  Generando screenshots placeholder...")
            print()
            
            # Generar placeholders si frontend no está disponible
            screenshot_placeholder("01-dashboard.png", "Dashboard Principal")
            screenshot_placeholder("02-document-viewer.png", "Visor de Documentos")
            screenshot_placeholder("03-annotations.png", "Sistema de Anotaciones")
            screenshot_placeholder("04-comparison.png", "Comparación de Documentos")
            
            # GraphQL sí podemos capturar
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                page = await browser.new_page(viewport=VIEWPORT_SIZE)
                await screenshot_graphql(page)
                await browser.close()
            
            screenshot_placeholder("06-sharepoint-integration.png", "Integración SharePoint")
            screenshot_placeholder("07-sap-integration.png", "Integración SAP DMS")
            
            print()
            print("=" * 70)
            print("✅ PLACEHOLDERS GENERADOS")
            print("=" * 70)
            print()
            print("📝 Para capturas reales:")
            print("   1. Iniciar frontend: cd frontend && npm run dev")
            print("   2. Ejecutar script nuevamente")
            print("   3. O capturar manualmente según SCREENSHOT_CAPTURE_GUIDE.md")
            return
            
    except ImportError:
        print("   ⚠️  requests no instalado. Saltando verificación.")
        print("   Ejecutar: pip install requests")
    
    print()
    
    # Iniciar Playwright
    async with async_playwright() as p:
        print("🚀 Iniciando navegador headless...")
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport=VIEWPORT_SIZE)
        page = await context.new_page()
        
        # Login inicial
        if await login(page, ADMIN_USER, ADMIN_PASS):
            # Capturar screenshots
            await screenshot_dashboard(page)
            await screenshot_document_viewer(page)
            await screenshot_annotations(page)
            await screenshot_comparison(page)
        
        # GraphQL (no requiere login)
        await screenshot_graphql(page)
        
        # Cerrar navegador
        await browser.close()
    
    # Placeholders para integraciones (si no están implementadas)
    print("\n📝 Generando placeholders para integraciones...")
    screenshot_placeholder("06-sharepoint-integration.png", "Integración SharePoint")
    screenshot_placeholder("07-sap-integration.png", "Integración SAP DMS")
    
    print()
    print("=" * 70)
    print("✅ CAPTURA COMPLETADA")
    print("=" * 70)
    print()
    print(f"📁 Screenshots guardados en: {OUTPUT_DIR}")
    print()
    print("Archivos generados:")
    for f in sorted(OUTPUT_DIR.glob("*.png")):
        size_kb = f.stat().st_size / 1024
        print(f"   • {f.name} ({size_kb:.1f} KB)")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  Captura interrumpida por usuario")
    except Exception as e:
        print(f"\n\n❌ Error inesperado: {e}")
        import traceback
        traceback.print_exc()
