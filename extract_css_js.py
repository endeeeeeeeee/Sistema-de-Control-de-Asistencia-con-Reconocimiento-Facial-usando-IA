"""
Script para extraer CSS y JavaScript de archivos HTML
y separarlos en archivos independientes
"""
import re
from pathlib import Path

# Páginas a procesar (todas las que tienen CSS/JS inline)
PAGES = [
    'login_flexible.html',
    'registro.html', 
    'equipo.html',
    'reportes.html',
    'tomar_asistencia.html',
    'validar_qr.html',
    'codigos_qr.html',
    'configuracion.html',
    'estudiantes.html',
    'materias.html',
    'registro_estudiante.html',
    'sesion_asistencia.html',
    'vincular_dispositivo.html',
    'dashboard.html',
    'login.html'
]

def extract_css(html_content, filename):
    """Extrae CSS del HTML"""
    pattern = r'<style>(.*?)</style>'
    match = re.search(pattern, html_content, re.DOTALL)
    
    if match:
        css_content = match.group(1).strip()
        
        # Guardar CSS
        css_file = f'static/css/{filename.replace(".html", ".css")}'
        Path(css_file).write_text(css_content, encoding='utf-8')
        print(f'✅ CSS extraído: {css_file}')
        
        # Remover CSS del HTML y agregar link
        html_content = re.sub(pattern, 
            f'<link rel="stylesheet" href="/static/css/{filename.replace(".html", ".css")}">',
            html_content, flags=re.DOTALL)
    
    return html_content

def extract_js(html_content, filename):
    """Extrae JavaScript del HTML"""
    # Buscar último bloque de script antes de </body>
    pattern = r'<script>(.*?)</script>\s*</body>'
    match = re.search(pattern, html_content, re.DOTALL)
    
    if match:
        js_content = match.group(1).strip()
        
        # Guardar JS
        js_file = f'static/js/{filename.replace(".html", ".js")}'
        Path(js_file).write_text(js_content, encoding='utf-8')
        print(f'✅ JS extraído: {js_file}')
        
        # Remover JS del HTML y agregar script tag
        html_content = re.sub(pattern,
            f'<script src="/static/js/{filename.replace(".html", ".js")}"></script>\n</body>',
            html_content, flags=re.DOTALL)
    
    return html_content

def process_file(filename):
    """Procesa un archivo HTML"""
    print(f'\n📄 Procesando: {filename}')
    
    html_file = Path(f'templates/{filename}')
    
    if not html_file.exists():
        print(f'⚠️  Archivo no encontrado: {filename}')
        return
    
    # Leer HTML
    html_content = html_file.read_text(encoding='utf-8')
    
    # Extraer CSS
    html_content = extract_css(html_content, filename)
    
    # Extraer JS
    html_content = extract_js(html_content, filename)
    
    # Guardar HTML modificado
    html_file.write_text(html_content, encoding='utf-8')
    print(f'✅ HTML actualizado: templates/{filename}')

def main():
    print('='*60)
    print('🎨 EXTRACTOR DE CSS Y JAVASCRIPT')
    print('='*60)
    
    # Crear directorios si no existen
    Path('static/css').mkdir(parents=True, exist_ok=True)
    Path('static/js').mkdir(parents=True, exist_ok=True)
    
    # Procesar cada archivo
    for page in PAGES:
        try:
            process_file(page)
        except Exception as e:
            print(f'❌ Error procesando {page}: {e}')
    
    print('\n' + '='*60)
    print('✨ Extracción completada!')
    print('='*60)

if __name__ == '__main__':
    main()
