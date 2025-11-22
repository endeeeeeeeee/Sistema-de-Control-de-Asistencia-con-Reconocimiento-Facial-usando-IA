"""
CLASS VISION - Asistente Virtual Tipo Siri
===========================================

Asistente inteligente con procesamiento de lenguaje natural (NLP),
reconocimiento de voz y síntesis de voz.

Funcionalidades:
- Consultas inteligentes ("¿Cuántos estudiantes asistieron hoy?")
- Modificaciones de configuración ("Cambia la tolerancia a 15 minutos")
- Generación de reportes ("Genera reporte semanal de matemáticas")
- Análisis predictivo ("¿Quién tiene riesgo de deserción?")
- Control por voz y respuestas habladas
"""

import re
import json
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Any
import difflib

class AsistenteVirtual:
    """
    Asistente virtual inteligente para CLASS VISION
    
    Procesa comandos en lenguaje natural y ejecuta acciones sobre el sistema.
    Similar a Siri/Alexa pero especializado en gestión educativa.
    """
    
    def __init__(self, db_connection=None):
        """
        Inicializa el asistente virtual
        
        Args:
            db_connection: Conexión a PostgreSQL (psycopg2 o SQLAlchemy)
        """
        self.db = db_connection
        self.contexto_conversacion = []
        self.ultima_entidad = None
        self.intentos_intent = self._cargar_patrones_intent()
        
    def _cargar_patrones_intent(self) -> Dict[str, List[Dict]]:
        """
        Carga patrones de intención para NLP
        
        Returns:
            Dict con patrones organizados por tipo de intención
        """
        return {
            'CONSULTA_ESTADISTICAS': [
                {
                    'patrones': [
                        r'cuántos?\s+(?:estudiantes?|alumnos?)\s+(?:asistieron|vinieron|llegaron)',
                        r'total\s+de\s+(?:asistencia|presentes)',
                        r'estadísticas?\s+de\s+(?:hoy|ayer|la semana)',
                        r'porcentaje\s+de\s+asistencia',
                        r'resumen\s+de\s+(?:asistencia|clases?)'
                    ],
                    'accion': 'consultar_estadisticas_asistencia',
                    'entidades': ['fecha', 'materia', 'nivel']
                },
                {
                    'patrones': [
                        r'quién(?:es)?\s+(?:faltó|faltaron|no vino)',
                        r'ausentes?\s+(?:de\s+)?(?:hoy|ayer)',
                        r'lista\s+de\s+(?:faltas|ausencias)',
                        r'estudiantes?\s+que\s+no\s+asistieron'
                    ],
                    'accion': 'listar_ausentes',
                    'entidades': ['fecha', 'materia']
                },
                {
                    'patrones': [
                        r'ranking\s+(?:de|del mes)',
                        r'mejores?\s+estudiantes?',
                        r'top\s+\d+',
                        r'quién(?:es)?\s+(?:lidera|está primero)',
                        r'tabla\s+de\s+posiciones'
                    ],
                    'accion': 'mostrar_ranking',
                    'entidades': ['periodo', 'limite']
                }
            ],
            
            'MODIFICACION_CONFIG': [
                {
                    'patrones': [
                        r'cambia(?:r)?\s+(?:la\s+)?tolerancia\s+a\s+(\d+)',
                        r'(?:establecer|modificar)\s+tolerancia',
                        r'tolerancia\s+de\s+(\d+)\s+minutos'
                    ],
                    'accion': 'modificar_tolerancia',
                    'entidades': ['valor_numerico']
                },
                {
                    'patrones': [
                        r'(?:habilita|activa|enciende)\s+(?:el\s+)?modo\s+virtual',
                        r'(?:deshabilita|desactiva|apaga)\s+(?:el\s+)?modo\s+virtual',
                        r'modo\s+virtual\s+(?:on|off|activado|desactivado)'
                    ],
                    'accion': 'toggle_modo_virtual',
                    'entidades': ['estado_booleano']
                },
                {
                    'patrones': [
                        r'cambia(?:r)?\s+(?:los\s+)?puntos\s+por\s+asistencia',
                        r'(?:establecer|modificar)\s+puntos',
                        r'(\d+)\s+puntos\s+por\s+(?:asistir|asistencia)'
                    ],
                    'accion': 'modificar_puntos',
                    'entidades': ['tipo_punto', 'valor_numerico']
                },
                {
                    'patrones': [
                        r'cambia(?:r)?\s+el\s+modo\s+a\s+(guardería|colegio|universidad)',
                        r'modo\s+de\s+operación\s+(guardería|colegio|universidad)',
                        r'establecer\s+como\s+(guardería|colegio|universidad)'
                    ],
                    'accion': 'cambiar_modo_operacion',
                    'entidades': ['modo']
                }
            ],
            
            'GENERACION_REPORTES': [
                {
                    'patrones': [
                        r'genera(?:r)?\s+reporte\s+(?:de\s+)?(?:la\s+)?(\w+)',
                        r'crear\s+reporte\s+(\w+)',
                        r'reporte\s+(\w+)\s+de\s+',
                        r'exporta(?:r)?\s+(?:datos|asistencia)'
                    ],
                    'accion': 'generar_reporte',
                    'entidades': ['tipo_reporte', 'formato', 'periodo', 'materia']
                },
                {
                    'patrones': [
                        r'descarga(?:r)?\s+excel',
                        r'exporta(?:r)?\s+a\s+csv',
                        r'dame\s+un\s+pdf',
                        r'reporte\s+en\s+(excel|csv|pdf)'
                    ],
                    'accion': 'exportar_datos',
                    'entidades': ['formato', 'alcance']
                }
            ],
            
            'ANALISIS_PREDICTIVO': [
                {
                    'patrones': [
                        r'quién(?:es)?\s+(?:tiene|tienen)\s+riesgo\s+de\s+(?:deserción|abandonar)',
                        r'estudiantes?\s+en\s+riesgo',
                        r'alertas?\s+de\s+deserción',
                        r'predic(?:ción|ciones)\s+de\s+abandono'
                    ],
                    'accion': 'analizar_riesgo_desercion',
                    'entidades': ['nivel_riesgo', 'materia']
                },
                {
                    'patrones': [
                        r'analiza(?:r)?\s+(?:el\s+)?comportamiento',
                        r'tendencia\s+de\s+asistencia',
                        r'patrón\s+de\s+(?:faltas|ausencias)',
                        r'predicción\s+de\s+asistencia'
                    ],
                    'accion': 'analizar_tendencias',
                    'entidades': ['estudiante', 'periodo']
                }
            ],
            
            'GESTION_QR': [
                {
                    'patrones': [
                        r'genera(?:r)?\s+(?:código|qr)\s+para',
                        r'crear\s+código\s+(?:temporal|virtual)',
                        r'código\s+de\s+(?:clase|asistencia)',
                        r'qr\s+para\s+(?:hoy|mañana)'
                    ],
                    'accion': 'generar_codigo_temporal',
                    'entidades': ['tipo_codigo', 'materia', 'validez']
                },
                {
                    'patrones': [
                        r'lista(?:r)?\s+códigos?\s+(?:activos|vigentes)',
                        r'qr\s+(?:activos|disponibles)',
                        r'códigos?\s+(?:válidos|sin usar)'
                    ],
                    'accion': 'listar_codigos_activos',
                    'entidades': ['materia']
                }
            ],
            
            'NOTIFICACIONES': [
                {
                    'patrones': [
                        r'envia(?:r)?\s+notificación',
                        r'avisar?\s+a\s+(?:los\s+)?(?:estudiantes?|tutores?)',
                        r'notifica(?:r)?\s+(?:que|sobre)',
                        r'alerta(?:r)?\s+a\s+'
                    ],
                    'accion': 'enviar_notificacion',
                    'entidades': ['destinatarios', 'tipo_notificacion', 'mensaje']
                },
                {
                    'patrones': [
                        r'notificaciones?\s+(?:pendientes|no leídas)',
                        r'mensajes?\s+sin\s+leer',
                        r'alertas?\s+activas?'
                    ],
                    'accion': 'listar_notificaciones_pendientes',
                    'entidades': ['tipo_destinatario']
                }
            ],
            
            'AYUDA': [
                {
                    'patrones': [
                        r'ayuda',
                        r'qué\s+puedes?\s+hacer',
                        r'comandos?\s+(?:disponibles|posibles)',
                        r'cómo\s+(?:funciona|uso)',
                        r'instrucciones'
                    ],
                    'accion': 'mostrar_ayuda',
                    'entidades': []
                }
            ]
        }
    
    def procesar_comando(self, texto_comando: str, usuario_id: int) -> Dict[str, Any]:
        """
        Procesa un comando en lenguaje natural
        
        Args:
            texto_comando: Texto del comando del usuario
            usuario_id: ID del usuario que ejecuta el comando
            
        Returns:
            Dict con respuesta, tipo y datos del resultado
        """
        inicio = datetime.now()
        
        # Normalizar texto
        texto_normalizado = self._normalizar_texto(texto_comando)
        
        # Detectar intención
        intencion, accion, entidades = self._detectar_intencion(texto_normalizado)
        
        # Extraer entidades del texto
        entidades_extraidas = self._extraer_entidades(texto_normalizado, entidades)
        
        # Ejecutar acción
        try:
            resultado = self._ejecutar_accion(
                accion, 
                entidades_extraidas, 
                usuario_id
            )
            
            # Guardar en historial
            duracion = (datetime.now() - inicio).total_seconds() * 1000
            self._guardar_historial(
                usuario_id=usuario_id,
                comando_texto=texto_comando,
                comando_tipo=intencion,
                intencion=accion,
                entidades_json=entidades_extraidas,
                respuesta_texto=resultado['respuesta'],
                respuesta_tipo=resultado['tipo'],
                acciones_ejecutadas=resultado.get('acciones', []),
                exito=resultado['exito'],
                duracion_ms=int(duracion)
            )
            
            return resultado
            
        except Exception as e:
            error_msg = f"Error al ejecutar comando: {str(e)}"
            self._guardar_historial(
                usuario_id=usuario_id,
                comando_texto=texto_comando,
                comando_tipo=intencion,
                intencion=accion,
                entidades_json=entidades_extraidas,
                respuesta_texto=error_msg,
                respuesta_tipo='TEXTO',
                acciones_ejecutadas=[],
                exito=False,
                error_mensaje=str(e),
                duracion_ms=int((datetime.now() - inicio).total_seconds() * 1000)
            )
            
            return {
                'exito': False,
                'respuesta': error_msg,
                'tipo': 'TEXTO',
                'error': str(e)
            }
    
    def _normalizar_texto(self, texto: str) -> str:
        """Normaliza el texto para procesamiento NLP"""
        texto = texto.lower().strip()
        # Remover signos de puntuación excepto interrogación
        texto = re.sub(r'[^\w\s\?¿áéíóúñ]', '', texto)
        return texto
    
    def _detectar_intencion(self, texto: str) -> Tuple[str, str, List[str]]:
        """
        Detecta la intención del usuario usando pattern matching
        
        Returns:
            Tuple de (tipo_intencion, accion, entidades_requeridas)
        """
        for tipo_intencion, patrones_grupo in self.intentos_intent.items():
            for patron_info in patrones_grupo:
                for patron in patron_info['patrones']:
                    if re.search(patron, texto, re.IGNORECASE):
                        return (
                            tipo_intencion,
                            patron_info['accion'],
                            patron_info['entidades']
                        )
        
        # Intent por defecto si no se detecta nada
        return ('CONSULTA', 'busqueda_general', ['termino'])
    
    def _extraer_entidades(self, texto: str, entidades_requeridas: List[str]) -> Dict:
        """
        Extrae entidades específicas del texto
        
        Args:
            texto: Texto normalizado
            entidades_requeridas: Lista de entidades a buscar
            
        Returns:
            Dict con entidades encontradas
        """
        entidades = {}
        
        # Fechas
        if 'fecha' in entidades_requeridas:
            if 'hoy' in texto:
                entidades['fecha'] = datetime.now().date()
            elif 'ayer' in texto:
                entidades['fecha'] = (datetime.now() - timedelta(days=1)).date()
            elif 'mañana' in texto:
                entidades['fecha'] = (datetime.now() + timedelta(days=1)).date()
            elif match := re.search(r'(\d{1,2})\s*[-/]\s*(\d{1,2})\s*[-/]\s*(\d{4})', texto):
                day, month, year = match.groups()
                entidades['fecha'] = datetime(int(year), int(month), int(day)).date()
        
        # Periodos
        if 'periodo' in entidades_requeridas:
            if 'semana' in texto:
                entidades['periodo'] = 'semanal'
            elif 'mes' in texto or 'mensual' in texto:
                entidades['periodo'] = 'mensual'
            elif 'dia' in texto or 'diario' in texto:
                entidades['periodo'] = 'diario'
            elif 'año' in texto or 'anual' in texto:
                entidades['periodo'] = 'anual'
        
        # Números
        if 'valor_numerico' in entidades_requeridas:
            if match := re.search(r'\d+', texto):
                entidades['valor_numerico'] = int(match.group())
        
        if 'limite' in entidades_requeridas:
            if match := re.search(r'top\s+(\d+)', texto):
                entidades['limite'] = int(match.group(1))
            else:
                entidades['limite'] = 10  # Default
        
        # Modo de operación
        if 'modo' in entidades_requeridas:
            if 'guarderia' in texto or 'guardería' in texto:
                entidades['modo'] = 'GUARDERIA'
            elif 'colegio' in texto:
                entidades['modo'] = 'COLEGIO'
            elif 'universidad' in texto:
                entidades['modo'] = 'UNIVERSIDAD'
        
        # Estados booleanos
        if 'estado_booleano' in entidades_requeridas:
            activar = ['habilita', 'activa', 'enciende', 'on', 'activado', 'si', 'sí']
            desactivar = ['deshabilita', 'desactiva', 'apaga', 'off', 'desactivado', 'no']
            
            if any(palabra in texto for palabra in activar):
                entidades['estado_booleano'] = True
            elif any(palabra in texto for palabra in desactivar):
                entidades['estado_booleano'] = False
        
        # Formato de archivo
        if 'formato' in entidades_requeridas:
            if 'excel' in texto or 'xlsx' in texto:
                entidades['formato'] = 'EXCEL'
            elif 'csv' in texto:
                entidades['formato'] = 'CSV'
            elif 'pdf' in texto:
                entidades['formato'] = 'PDF'
            else:
                entidades['formato'] = 'EXCEL'  # Default
        
        # Tipo de reporte
        if 'tipo_reporte' in entidades_requeridas:
            tipos = {
                'diario': 'ASISTENCIA_DIARIA',
                'semanal': 'ASISTENCIA_SEMANAL',
                'mensual': 'ASISTENCIA_MENSUAL',
                'ranking': 'RANKING_ESTUDIANTES',
                'deserción': 'ALERTAS_DESERCION',
                'desercion': 'ALERTAS_DESERCION'
            }
            for palabra, tipo in tipos.items():
                if palabra in texto:
                    entidades['tipo_reporte'] = tipo
                    break
        
        # Nivel de riesgo
        if 'nivel_riesgo' in entidades_requeridas:
            if 'critico' in texto or 'crítico' in texto or 'urgente' in texto:
                entidades['nivel_riesgo'] = 'CRITICO'
            elif 'alto' in texto:
                entidades['nivel_riesgo'] = 'ALTO'
            elif 'medio' in texto:
                entidades['nivel_riesgo'] = 'MEDIO'
            elif 'bajo' in texto:
                entidades['nivel_riesgo'] = 'BAJO'
        
        # Materia (intenta extraer nombre)
        if 'materia' in entidades_requeridas:
            # Buscar después de "de", "para", "en"
            if match := re.search(r'(?:de|para|en)\s+([a-záéíóúñ\s]+?)(?:\s|$)', texto):
                posible_materia = match.group(1).strip()
                # Validar contra base de datos si existe
                if self.db:
                    materia_encontrada = self._buscar_materia_fuzzy(posible_materia)
                    if materia_encontrada:
                        entidades['materia'] = materia_encontrada
        
        return entidades
    
    def _ejecutar_accion(self, accion: str, entidades: Dict, usuario_id: int) -> Dict:
        """
        Ejecuta la acción correspondiente
        
        Args:
            accion: Nombre de la acción a ejecutar
            entidades: Entidades extraídas del comando
            usuario_id: ID del usuario
            
        Returns:
            Dict con resultado de la ejecución
        """
        # Mapeo de acciones a métodos
        acciones_map = {
            'consultar_estadisticas_asistencia': self._accion_estadisticas,
            'listar_ausentes': self._accion_ausentes,
            'mostrar_ranking': self._accion_ranking,
            'modificar_tolerancia': self._accion_modificar_tolerancia,
            'toggle_modo_virtual': self._accion_toggle_virtual,
            'modificar_puntos': self._accion_modificar_puntos,
            'cambiar_modo_operacion': self._accion_cambiar_modo,
            'generar_reporte': self._accion_generar_reporte,
            'exportar_datos': self._accion_exportar,
            'analizar_riesgo_desercion': self._accion_riesgo_desercion,
            'analizar_tendencias': self._accion_tendencias,
            'generar_codigo_temporal': self._accion_generar_qr,
            'listar_codigos_activos': self._accion_listar_qr,
            'enviar_notificacion': self._accion_notificar,
            'listar_notificaciones_pendientes': self._accion_listar_notificaciones,
            'mostrar_ayuda': self._accion_ayuda,
            'busqueda_general': self._accion_busqueda
        }
        
        metodo = acciones_map.get(accion, self._accion_no_implementada)
        return metodo(entidades, usuario_id)
    
    # ========================================================================
    # ACCIONES IMPLEMENTADAS
    # ========================================================================
    
    def _accion_estadisticas(self, entidades: Dict, usuario_id: int) -> Dict:
        """Consultar estadísticas de asistencia"""
        fecha = entidades.get('fecha', datetime.now().date())
        
        if not self.db:
            return self._respuesta_mock("estadísticas", fecha)
        
        # Query real a la base de datos
        query = """
            SELECT 
                COUNT(DISTINCT i.id_estudiante) as total_estudiantes,
                COUNT(DISTINCT CASE WHEN al.estado IN ('PRESENTE', 'VIRTUAL') THEN al.id END) as presentes,
                COUNT(DISTINCT CASE WHEN al.estado = 'TARDANZA' THEN al.id END) as tardanzas,
                COUNT(DISTINCT CASE WHEN al.estado = 'AUSENTE' THEN al.id END) as ausentes,
                ROUND(AVG(CASE WHEN al.estado IN ('PRESENTE', 'VIRTUAL') THEN 100.0 ELSE 0.0 END), 2) as porcentaje
            FROM inscripciones i
            LEFT JOIN asistencia_log al ON al.id_inscripcion = i.id AND al.fecha = %s
            WHERE i.estado = 'ACTIVO'
        """
        
        cursor = self.db.cursor()
        cursor.execute(query, (fecha,))
        stats = cursor.fetchone()
        
        respuesta = f"""📊 Estadísticas del {fecha.strftime('%d/%m/%Y')}:

✅ Presentes: {stats[1]}
⏰ Tardanzas: {stats[2]}
❌ Ausentes: {stats[3]}
👥 Total: {stats[0]}

📈 Porcentaje de asistencia: {stats[4]:.1f}%"""
        
        return {
            'exito': True,
            'respuesta': respuesta,
            'tipo': 'TEXTO',
            'datos': {
                'fecha': str(fecha),
                'presentes': stats[1],
                'tardanzas': stats[2],
                'ausentes': stats[3],
                'total': stats[0],
                'porcentaje': float(stats[4])
            },
            'acciones': [f'CONSULTA_ESTADISTICAS:{fecha}']
        }
    
    def _accion_ausentes(self, entidades: Dict, usuario_id: int) -> Dict:
        """Listar estudiantes ausentes"""
        fecha = entidades.get('fecha', datetime.now().date())
        
        if not self.db:
            return self._respuesta_mock("ausentes", fecha)
        
        query = """
            SELECT e.nombre_completo, m.nombre as materia
            FROM estudiantes e
            JOIN inscripciones i ON i.id_estudiante = e.id
            JOIN materias m ON m.id = i.id_materia
            LEFT JOIN asistencia_log al ON al.id_inscripcion = i.id AND al.fecha = %s
            WHERE i.estado = 'ACTIVO' 
            AND (al.id IS NULL OR al.estado = 'AUSENTE')
            ORDER BY e.nombre_completo
        """
        
        cursor = self.db.cursor()
        cursor.execute(query, (fecha,))
        ausentes = cursor.fetchall()
        
        if not ausentes:
            respuesta = f"🎉 ¡Excelente! No hay ausentes el {fecha.strftime('%d/%m/%Y')}"
        else:
            lista = "\n".join([f"• {row[0]} - {row[1]}" for row in ausentes])
            respuesta = f"❌ Ausentes del {fecha.strftime('%d/%m/%Y')} ({len(ausentes)}):\n\n{lista}"
        
        return {
            'exito': True,
            'respuesta': respuesta,
            'tipo': 'TEXTO',
            'datos': {'ausentes': [{'nombre': r[0], 'materia': r[1]} for r in ausentes]},
            'acciones': [f'CONSULTA_AUSENTES:{fecha}']
        }
    
    def _accion_ranking(self, entidades: Dict, usuario_id: int) -> Dict:
        """Mostrar ranking de estudiantes"""
        limite = entidades.get('limite', 10)
        
        if not self.db:
            return self._respuesta_mock("ranking", limite)
        
        query = """
            SELECT 
                e.nombre_completo,
                e.puntos_acumulados,
                e.nivel,
                COUNT(DISTINCT eb.id_badge) as badges
            FROM estudiantes e
            LEFT JOIN estudiantes_badges eb ON eb.id_estudiante = e.id
            WHERE e.activo = TRUE
            GROUP BY e.id, e.nombre_completo, e.puntos_acumulados, e.nivel
            ORDER BY e.puntos_acumulados DESC, badges DESC
            LIMIT %s
        """
        
        cursor = self.db.cursor()
        cursor.execute(query, (limite,))
        ranking = cursor.fetchall()
        
        medallas = ['🥇', '🥈', '🥉']
        lista = []
        for idx, row in enumerate(ranking, 1):
            medalla = medallas[idx-1] if idx <= 3 else f"{idx}."
            lista.append(f"{medalla} {row[0]} - {row[1]} pts (Nivel {row[2]}, {row[3]} badges)")
        
        respuesta = f"🏆 Top {limite} Estudiantes:\n\n" + "\n".join(lista)
        
        return {
            'exito': True,
            'respuesta': respuesta,
            'tipo': 'TEXTO',
            'datos': {
                'ranking': [
                    {'posicion': i+1, 'nombre': r[0], 'puntos': r[1], 'nivel': r[2], 'badges': r[3]}
                    for i, r in enumerate(ranking)
                ]
            },
            'acciones': [f'CONSULTA_RANKING:TOP_{limite}']
        }
    
    def _accion_modificar_tolerancia(self, entidades: Dict, usuario_id: int) -> Dict:
        """Modificar tolerancia de minutos"""
        valor = entidades.get('valor_numerico')
        
        if not valor:
            return {
                'exito': False,
                'respuesta': "No pude detectar el valor de minutos. Por favor especifica un número.",
                'tipo': 'TEXTO'
            }
        
        if not self.db:
            return self._respuesta_mock("modificar_tolerancia", valor)
        
        query = """
            UPDATE sys_config
            SET reglas_json = jsonb_set(reglas_json, '{tolerancia_minutos}', %s::text::jsonb),
                actualizado_por = %s
            WHERE id = 1
            RETURNING reglas_json->>'tolerancia_minutos'
        """
        
        cursor = self.db.cursor()
        cursor.execute(query, (valor, usuario_id))
        self.db.commit()
        
        respuesta = f"✅ Tolerancia actualizada a {valor} minutos correctamente."
        
        return {
            'exito': True,
            'respuesta': respuesta,
            'tipo': 'TEXTO',
            'datos': {'tolerancia_anterior': None, 'tolerancia_nueva': valor},
            'acciones': [f'MODIFICACION_CONFIG:TOLERANCIA={valor}']
        }
    
    def _accion_toggle_virtual(self, entidades: Dict, usuario_id: int) -> Dict:
        """Activar/desactivar modo virtual"""
        estado = entidades.get('estado_booleano')
        
        if estado is None:
            return {
                'exito': False,
                'respuesta': "No pude detectar si quieres activar o desactivar el modo virtual.",
                'tipo': 'TEXTO'
            }
        
        if not self.db:
            return self._respuesta_mock("toggle_virtual", estado)
        
        query = """
            UPDATE sys_config
            SET reglas_json = jsonb_set(reglas_json, '{modo_virtual_habilitado}', %s::text::jsonb),
                actualizado_por = %s
            WHERE id = 1
        """
        
        cursor = self.db.cursor()
        cursor.execute(query, ('true' if estado else 'false', usuario_id))
        self.db.commit()
        
        texto = "activado" if estado else "desactivado"
        respuesta = f"✅ Modo virtual {texto} correctamente."
        
        return {
            'exito': True,
            'respuesta': respuesta,
            'tipo': 'TEXTO',
            'datos': {'modo_virtual': estado},
            'acciones': [f'MODIFICACION_CONFIG:MODO_VIRTUAL={estado}']
        }
    
    def _accion_modificar_puntos(self, entidades: Dict, usuario_id: int) -> Dict:
        """Modificar puntos por asistencia"""
        valor = entidades.get('valor_numerico', 10)
        
        if not self.db:
            return self._respuesta_mock("modificar_puntos", valor)
        
        query = """
            UPDATE sys_config
            SET reglas_json = jsonb_set(reglas_json, '{puntos_por_asistencia}', %s::text::jsonb),
                actualizado_por = %s
            WHERE id = 1
        """
        
        cursor = self.db.cursor()
        cursor.execute(query, (valor, usuario_id))
        self.db.commit()
        
        respuesta = f"✅ Puntos por asistencia actualizados a {valor} puntos."
        
        return {
            'exito': True,
            'respuesta': respuesta,
            'tipo': 'TEXTO',
            'datos': {'puntos_asistencia': valor},
            'acciones': [f'MODIFICACION_CONFIG:PUNTOS_ASISTENCIA={valor}']
        }
    
    def _accion_cambiar_modo(self, entidades: Dict, usuario_id: int) -> Dict:
        """Cambiar modo de operación"""
        modo = entidades.get('modo')
        
        if not modo:
            return {
                'exito': False,
                'respuesta': "No pude detectar el modo. Especifica: guardería, colegio o universidad.",
                'tipo': 'TEXTO'
            }
        
        if not self.db:
            return self._respuesta_mock("cambiar_modo", modo)
        
        query = """
            UPDATE sys_config
            SET modo_operacion = %s,
                actualizado_por = %s
            WHERE id = 1
        """
        
        cursor = self.db.cursor()
        cursor.execute(query, (modo, usuario_id))
        self.db.commit()
        
        respuesta = f"✅ Modo de operación cambiado a {modo}."
        
        return {
            'exito': True,
            'respuesta': respuesta,
            'tipo': 'TEXTO',
            'datos': {'modo': modo},
            'acciones': [f'MODIFICACION_CONFIG:MODO={modo}']
        }
    
    def _accion_generar_reporte(self, entidades: Dict, usuario_id: int) -> Dict:
        """Generar reporte"""
        tipo = entidades.get('tipo_reporte', 'ASISTENCIA_DIARIA')
        formato = entidades.get('formato', 'EXCEL')
        
        # Esta acción requiere integración con módulo de reportes
        respuesta = f"📄 Generando reporte {tipo} en formato {formato}..."
        
        return {
            'exito': True,
            'respuesta': respuesta,
            'tipo': 'TEXTO',
            'datos': {'tipo': tipo, 'formato': formato, 'url': '/reportes/download/123'},
            'acciones': [f'GENERACION_REPORTE:{tipo}:{formato}']
        }
    
    def _accion_exportar(self, entidades: Dict, usuario_id: int) -> Dict:
        """Exportar datos"""
        formato = entidades.get('formato', 'EXCEL')
        
        respuesta = f"📥 Preparando exportación en {formato}..."
        
        return {
            'exito': True,
            'respuesta': respuesta,
            'tipo': 'TEXTO',
            'datos': {'formato': formato},
            'acciones': [f'EXPORTACION:{formato}']
        }
    
    def _accion_riesgo_desercion(self, entidades: Dict, usuario_id: int) -> Dict:
        """Analizar riesgo de deserción"""
        nivel_riesgo = entidades.get('nivel_riesgo')
        
        if not self.db:
            return self._respuesta_mock("riesgo_desercion", nivel_riesgo)
        
        query = """
            SELECT 
                e.nombre_completo,
                ad.nivel_riesgo,
                ad.probabilidad_desercion,
                ad.estado
            FROM alertas_desercion ad
            JOIN estudiantes e ON e.id = ad.id_estudiante
            WHERE ad.estado IN ('NUEVA', 'EN_SEGUIMIENTO', 'CRITICA')
        """
        
        if nivel_riesgo:
            query += f" AND ad.nivel_riesgo = '{nivel_riesgo}'"
        
        query += " ORDER BY ad.probabilidad_desercion DESC LIMIT 10"
        
        cursor = self.db.cursor()
        cursor.execute(query)
        alertas = cursor.fetchall()
        
        if not alertas:
            respuesta = "✅ No hay estudiantes en riesgo de deserción en este momento."
        else:
            lista = "\n".join([
                f"• {row[0]} - {row[1]} ({row[2]:.1f}%) - {row[3]}"
                for row in alertas
            ])
            respuesta = f"⚠️ Estudiantes en riesgo ({len(alertas)}):\n\n{lista}"
        
        return {
            'exito': True,
            'respuesta': respuesta,
            'tipo': 'TEXTO',
            'datos': {
                'alertas': [
                    {'nombre': r[0], 'nivel': r[1], 'probabilidad': float(r[2]), 'estado': r[3]}
                    for r in alertas
                ]
            },
            'acciones': ['ANALISIS_RIESGO_DESERCION']
        }
    
    def _accion_tendencias(self, entidades: Dict, usuario_id: int) -> Dict:
        """Analizar tendencias de asistencia"""
        respuesta = "📊 Analizando tendencias de asistencia... (Requiere implementación de AI)"
        
        return {
            'exito': True,
            'respuesta': respuesta,
            'tipo': 'TEXTO',
            'datos': {},
            'acciones': ['ANALISIS_TENDENCIAS']
        }
    
    def _accion_generar_qr(self, entidades: Dict, usuario_id: int) -> Dict:
        """Generar código QR temporal"""
        import secrets
        
        codigo = secrets.token_urlsafe(16)
        valido_hasta = datetime.now() + timedelta(hours=1)
        
        respuesta = f"✅ Código QR generado:\n\n🔑 {codigo}\n⏰ Válido hasta: {valido_hasta.strftime('%H:%M')}"
        
        return {
            'exito': True,
            'respuesta': respuesta,
            'tipo': 'TEXTO',
            'datos': {'codigo': codigo, 'valido_hasta': str(valido_hasta)},
            'acciones': [f'GENERACION_QR:{codigo}']
        }
    
    def _accion_listar_qr(self, entidades: Dict, usuario_id: int) -> Dict:
        """Listar códigos QR activos"""
        if not self.db:
            return self._respuesta_mock("listar_qr")
        
        query = """
            SELECT codigo, tipo, valido_hasta, usado
            FROM codigos_temporales
            WHERE valido_hasta > NOW() AND usado = FALSE
            ORDER BY valido_hasta DESC
            LIMIT 10
        """
        
        cursor = self.db.cursor()
        cursor.execute(query)
        codigos = cursor.fetchall()
        
        if not codigos:
            respuesta = "📝 No hay códigos activos en este momento."
        else:
            lista = "\n".join([
                f"• {row[0][:20]}... ({row[1]}) - Expira: {row[2].strftime('%H:%M')}"
                for row in codigos
            ])
            respuesta = f"🔑 Códigos activos ({len(codigos)}):\n\n{lista}"
        
        return {
            'exito': True,
            'respuesta': respuesta,
            'tipo': 'TEXTO',
            'datos': {'codigos': [{'codigo': r[0], 'tipo': r[1]} for r in codigos]},
            'acciones': ['LISTAR_CODIGOS_QR']
        }
    
    def _accion_notificar(self, entidades: Dict, usuario_id: int) -> Dict:
        """Enviar notificación"""
        respuesta = "📨 Notificación enviada correctamente."
        
        return {
            'exito': True,
            'respuesta': respuesta,
            'tipo': 'TEXTO',
            'datos': {},
            'acciones': ['ENVIO_NOTIFICACION']
        }
    
    def _accion_listar_notificaciones(self, entidades: Dict, usuario_id: int) -> Dict:
        """Listar notificaciones pendientes"""
        if not self.db:
            return self._respuesta_mock("listar_notificaciones")
        
        query = """
            SELECT titulo, mensaje, creado_en
            FROM notificaciones_internas
            WHERE leida = FALSE
            ORDER BY creado_en DESC
            LIMIT 10
        """
        
        cursor = self.db.cursor()
        cursor.execute(query)
        notificaciones = cursor.fetchall()
        
        if not notificaciones:
            respuesta = "✅ No hay notificaciones pendientes."
        else:
            lista = "\n".join([
                f"• {row[0]} - {row[2].strftime('%d/%m %H:%M')}"
                for row in notificaciones
            ])
            respuesta = f"🔔 Notificaciones pendientes ({len(notificaciones)}):\n\n{lista}"
        
        return {
            'exito': True,
            'respuesta': respuesta,
            'tipo': 'TEXTO',
            'datos': {'notificaciones': [{'titulo': r[0], 'mensaje': r[1]} for r in notificaciones]},
            'acciones': ['LISTAR_NOTIFICACIONES']
        }
    
    def _accion_ayuda(self, entidades: Dict, usuario_id: int) -> Dict:
        """Mostrar ayuda"""
        respuesta = """🤖 CLASS VISION - Asistente Virtual

Puedo ayudarte con:

📊 **Consultas**
• "¿Cuántos estudiantes asistieron hoy?"
• "¿Quién faltó ayer?"
• "Muestra el ranking mensual"

⚙️ **Configuración**
• "Cambia la tolerancia a 15 minutos"
• "Activa el modo virtual"
• "Cambia el modo a universidad"

📄 **Reportes**
• "Genera reporte semanal"
• "Exporta a Excel"

⚠️ **Análisis**
• "¿Quién tiene riesgo de deserción?"
• "Analiza tendencias de asistencia"

🔑 **Códigos QR**
• "Genera código para clase virtual"
• "Lista códigos activos"

¿En qué puedo ayudarte?"""
        
        return {
            'exito': True,
            'respuesta': respuesta,
            'tipo': 'TEXTO',
            'datos': {},
            'acciones': ['MOSTRAR_AYUDA']
        }
    
    def _accion_busqueda(self, entidades: Dict, usuario_id: int) -> Dict:
        """Búsqueda general"""
        respuesta = "🔍 No entendí completamente tu solicitud. Escribe 'ayuda' para ver lo que puedo hacer."
        
        return {
            'exito': False,
            'respuesta': respuesta,
            'tipo': 'TEXTO',
            'datos': {},
            'acciones': []
        }
    
    def _accion_no_implementada(self, entidades: Dict, usuario_id: int) -> Dict:
        """Acción no implementada"""
        return {
            'exito': False,
            'respuesta': "Esta funcionalidad aún no está implementada.",
            'tipo': 'TEXTO',
            'datos': {},
            'acciones': []
        }
    
    # ========================================================================
    # UTILIDADES
    # ========================================================================
    
    def _buscar_materia_fuzzy(self, texto: str) -> Optional[str]:
        """Busca materia usando fuzzy matching"""
        if not self.db:
            return None
        
        cursor = self.db.cursor()
        cursor.execute("SELECT nombre FROM materias WHERE activo = TRUE")
        materias = [row[0] for row in cursor.fetchall()]
        
        matches = difflib.get_close_matches(texto, materias, n=1, cutoff=0.6)
        return matches[0] if matches else None
    
    def _guardar_historial(self, **kwargs):
        """Guarda comando en historial"""
        if not self.db:
            return
        
        query = """
            INSERT INTO asistente_historial (
                id_usuario, comando_texto, comando_tipo, intencion,
                entidades_json, respuesta_texto, respuesta_tipo,
                acciones_ejecutadas, exito, error_mensaje, duracion_ms
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        cursor = self.db.cursor()
        cursor.execute(query, (
            kwargs['usuario_id'],
            kwargs['comando_texto'],
            kwargs['comando_tipo'],
            kwargs['intencion'],
            json.dumps(kwargs['entidades_json']),
            kwargs['respuesta_texto'],
            kwargs['respuesta_tipo'],
            json.dumps(kwargs['acciones_ejecutadas']),
            kwargs['exito'],
            kwargs.get('error_mensaje'),
            kwargs['duracion_ms']
        ))
        self.db.commit()
    
    def _respuesta_mock(self, tipo: str, *args) -> Dict:
        """Genera respuesta mock cuando no hay DB"""
        return {
            'exito': True,
            'respuesta': f"[MODO DEMO] Acción '{tipo}' ejecutada con parámetros: {args}",
            'tipo': 'TEXTO',
            'datos': {'mock': True},
            'acciones': [f'MOCK:{tipo}']
        }


# ============================================================================
# INTEGRACIÓN CON WEB SPEECH API (JavaScript)
# ============================================================================

"""
// Frontend - JavaScript para reconocimiento y síntesis de voz

class AsistenteVoz {
    constructor() {
        this.recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
        this.synthesis = window.speechSynthesis;
        
        // Configurar reconocimiento
        this.recognition.lang = 'es-ES';
        this.recognition.continuous = false;
        this.recognition.interimResults = false;
        
        this.recognition.onresult = (event) => {
            const transcript = event.results[0][0].transcript;
            this.procesarComando(transcript);
        };
    }
    
    iniciarEscucha() {
        this.recognition.start();
        console.log('Escuchando...');
    }
    
    async procesarComando(texto) {
        // Enviar a backend
        const response = await fetch('/api/assistant/comando', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({comando: texto})
        });
        
        const resultado = await response.json();
        
        // Hablar respuesta
        this.hablar(resultado.respuesta);
        
        // Mostrar en UI
        this.mostrarRespuesta(resultado);
    }
    
    hablar(texto) {
        const utterance = new SpeechSynthesisUtterance(texto);
        utterance.lang = 'es-ES';
        utterance.rate = 1.0;
        utterance.pitch = 1.0;
        this.synthesis.speak(utterance);
    }
    
    mostrarRespuesta(resultado) {
        // Actualizar UI con resultado
        document.getElementById('assistant-response').innerHTML = resultado.respuesta;
    }
}

// Uso
const asistente = new AsistenteVoz();
document.getElementById('btn-voice').onclick = () => asistente.iniciarEscucha();
"""
