"""
Inserta datos de prueba para TODAS las funcionalidades:
- Tutores (para GUARDERÍA/COLEGIO)
- Códigos QR temporales
- Asistencias (facial y QR)
- Asistencia virtual
- Notificaciones
- Justificaciones
- Alertas de deserción
- Badges ganados
- Reportes
- Comandos del asistente
- Audit log
"""

import os
from dotenv import load_dotenv
from datetime import datetime, timedelta, date, time
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import secrets
import hashlib

load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()

print("\n" + "="*100)
print("📝 INSERTANDO DATOS DE PRUEBA PARA TODAS LAS FUNCIONALIDADES")
print("="*100)

try:
    # 1. TUTORES (Padres para GUARDERÍA/COLEGIO)
    print("\n👨‍👩‍👧 Insertando tutores...")
    
    tutores_data = [
        ("12345678", "María González", "71234567", "maria.gonzalez@email.com", "Av. Principal 123", "MADRE"),
        ("87654321", "Juan Pérez", "72345678", "juan.perez@email.com", "Calle Secundaria 456", "PADRE"),
        ("11223344", "Ana Rodríguez", "73456789", "ana.rodriguez@email.com", "Zona Norte 789", "MADRE"),
    ]
    
    tutor_ids = []
    for ci, nombre, tel, email, dir, rel in tutores_data:
        qr_code = hashlib.md5(f"{ci}{nombre}".encode()).hexdigest()[:20]
        
        result = session.execute(text("""
            INSERT INTO tutores (ci, nombre_completo, telefono, email, direccion, relacion, qr_code_pickup, activo)
            VALUES (:ci, :nombre, :tel, :email, :dir, :rel, :qr, true)
            RETURNING id
        """), {
            'ci': ci, 'nombre': nombre, 'tel': tel, 'email': email, 
            'dir': dir, 'rel': rel, 'qr': qr_code
        })
        tutor_id = result.fetchone()[0]
        tutor_ids.append(tutor_id)
        print(f"  ✅ {nombre} (QR: {qr_code})")
    
    session.commit()
    
    # Asignar tutores a algunos estudiantes
    print("\n  🔗 Asignando tutores a estudiantes...")
    session.execute(text("UPDATE estudiantes SET id_tutor = :tutor_id WHERE codigo_estudiante = '13245'"), {'tutor_id': tutor_ids[0]})
    session.execute(text("UPDATE estudiantes SET id_tutor = :tutor_id WHERE codigo_estudiante = '555'"), {'tutor_id': tutor_ids[1]})
    session.execute(text("UPDATE estudiantes SET id_tutor = :tutor_id WHERE codigo_estudiante = '111'"), {'tutor_id': tutor_ids[2]})
    session.commit()
    print("  ✅ 3 estudiantes ahora tienen tutores asignados")
    
    # 2. CÓDIGOS QR TEMPORALES
    print("\n📱 Insertando códigos QR temporales...")
    
    # Obtener IDs de materias
    materias = session.execute(text("SELECT id, nombre FROM materias ORDER BY id LIMIT 2")).fetchall()
    
    codigos_qr = []
    for materia_id, materia_nombre in materias:
        codigo = secrets.token_urlsafe(16)
        hash_ver = hashlib.sha256(codigo.encode()).hexdigest()
        
        valido_desde = datetime.now()
        valido_hasta = valido_desde + timedelta(minutes=30)
        
        result = session.execute(text("""
            INSERT INTO codigos_temporales (
                codigo, tipo, id_materia, fecha_valido, valido_desde, valido_hasta,
                usado, hash_verificacion, max_usos, usos_actuales, generado_por
            ) VALUES (
                :codigo, 'QR_CLASE_VIRTUAL', :materia_id, CURRENT_DATE, :desde, :hasta,
                false, :hash, 50, 0, 1
            ) RETURNING id
        """), {
            'codigo': codigo, 'materia_id': materia_id, 'desde': valido_desde,
            'hasta': valido_hasta, 'hash': hash_ver
        })
        codigo_id = result.fetchone()[0]
        codigos_qr.append((codigo_id, codigo))
        print(f"  ✅ QR para {materia_nombre}: {codigo[:20]}...")
    
    session.commit()
    
    # 3. ASISTENCIAS (con diferentes métodos)
    print("\n📝 Insertando registros de asistencia...")
    
    # Obtener inscripciones
    inscripciones = session.execute(text("SELECT id, id_estudiante, id_materia FROM inscripciones")).fetchall()
    
    hoy = date.today()
    ayer = hoy - timedelta(days=1)
    
    asistencias = []
    for i, (insc_id, est_id, mat_id) in enumerate(inscripciones):
        # Asistencia de hoy (FACIAL)
        hora_entrada = datetime.combine(hoy, time(8, 15 + i*5))
        result = session.execute(text("""
            INSERT INTO asistencia_log (
                id_inscripcion, fecha, hora_entrada, metodo_entrada, estado, score_liveness, ip_address
            ) VALUES (
                :insc_id, :fecha, :hora, 'FACIAL', 'PRESENTE', 0.95, '192.168.1.100'
            ) RETURNING id
        """), {'insc_id': insc_id, 'fecha': hoy, 'hora': hora_entrada})
        asist_id = result.fetchone()[0]
        asistencias.append(asist_id)
        print(f"  ✅ Asistencia FACIAL - Estudiante {est_id} - HOY - PRESENTE")
        
        # Asistencia de ayer (QR - TARDANZA)
        hora_tardanza = datetime.combine(ayer, time(8, 25 + i*5))
        result = session.execute(text("""
            INSERT INTO asistencia_log (
                id_inscripcion, fecha, hora_entrada, metodo_entrada, estado, 
                ip_address, id_codigo_temporal
            ) VALUES (
                :insc_id, :fecha, :hora, 'QR', 'TARDANZA', '192.168.1.101', :codigo_id
            ) RETURNING id
        """), {'insc_id': insc_id, 'fecha': ayer, 'hora': hora_tardanza, 'codigo_id': codigos_qr[0][0]})
        asist_id = result.fetchone()[0]
        asistencias.append(asist_id)
        print(f"  ✅ Asistencia QR - Estudiante {est_id} - AYER - TARDANZA")
    
    # Asistencia con PICKUP (para guardería)
    if inscripciones and tutor_ids:
        hora_pickup = datetime.combine(hoy, time(17, 30))
        session.execute(text("""
            UPDATE asistencia_log 
            SET id_tutor_pickup = :tutor_id, hora_pickup = :hora
            WHERE id = :asist_id
        """), {'tutor_id': tutor_ids[0], 'hora': hora_pickup, 'asist_id': asistencias[0]})
        print(f"  ✅ PICKUP registrado - Tutor {tutor_ids[0]} recogió estudiante")
    
    session.commit()
    
    # 4. ASISTENCIA VIRTUAL
    print("\n💻 Insertando asistencia virtual...")
    
    if asistencias:
        session.execute(text("""
            INSERT INTO asistencia_virtual (
                id_asistencia_log, id_codigo_temporal, plataforma, duracion_minutos,
                verificacion_intermitente, capturas_pantalla, ip_address, user_agent
            ) VALUES (
                :asist_id, :codigo_id, 'ZOOM', 45, true, 3,
                '192.168.1.102', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
            )
        """), {'asist_id': asistencias[1], 'codigo_id': codigos_qr[0][0]})
        print(f"  ✅ Asistencia virtual en ZOOM - 45 minutos - 3 capturas")
    
    session.commit()
    
    # 5. NOTIFICACIONES
    print("\n🔔 Insertando notificaciones...")
    
    notificaciones = [
        ('DOCENTE', 1, 'ASISTENCIA', '🎉 Excelente asistencia', 
         'La materia PROGRAMACIÓN IV tiene 100% de asistencia hoy', 'NORMAL'),
        ('DOCENTE', 1, 'ALERTA', '⚠️ Estudiante con tardanzas', 
         'Alberto Figue ha llegado tarde 2 veces esta semana', 'ALTA'),
        ('DOCENTE', 5, 'GAMIFICACION', '🏆 Badge otorgado', 
         'Ender Rosales ganó el badge "Puntualidad Extrema"', 'NORMAL'),
    ]
    
    for dest_tipo, dest_id, tipo, titulo, mensaje, prioridad in notificaciones:
        expira = datetime.now() + timedelta(days=7)
        session.execute(text("""
            INSERT INTO notificaciones_internas (
                destinatario_tipo, destinatario_id, tipo, titulo, mensaje, 
                metadata_json, leida, prioridad, expira_en
            ) VALUES (
                :dest_tipo, :dest_id, :tipo, :titulo, :mensaje,
                '{"origen": "sistema_automatico"}'::jsonb, false, :prioridad, :expira
            )
        """), {
            'dest_tipo': dest_tipo, 'dest_id': dest_id, 'tipo': tipo,
            'titulo': titulo, 'mensaje': mensaje, 'prioridad': prioridad, 'expira': expira
        })
        print(f"  ✅ {titulo}")
    
    session.commit()
    
    # 6. JUSTIFICACIONES
    print("\n📄 Insertando justificaciones...")
    
    # Obtener un estudiante
    estudiante = session.execute(text("SELECT id FROM estudiantes LIMIT 1")).fetchone()
    materia = session.execute(text("SELECT id FROM materias LIMIT 1")).fetchone()
    
    if estudiante and materia:
        session.execute(text("""
            INSERT INTO justificaciones (
                id_estudiante, id_materia, fecha_inicio, fecha_fin, motivo, tipo,
                documento_url, estado, comentario_aprobacion
            ) VALUES (
                :est_id, :mat_id, CURRENT_DATE - 2, CURRENT_DATE - 1,
                'Consulta médica por gripe', 'MEDICO',
                '/uploads/certificados/cert_001.pdf', 'APROBADO',
                'Certificado médico válido - Aprobado'
            )
        """), {'est_id': estudiante[0], 'mat_id': materia[0]})
        print(f"  ✅ Justificación médica aprobada")
    
    session.commit()
    
    # 7. ALERTAS DE DESERCIÓN
    print("\n⚠️  Insertando alertas de deserción...")
    
    # Crear alerta para un estudiante con muchas faltas (simulado)
    estudiantes = session.execute(text("SELECT id, codigo_estudiante, nombre_completo FROM estudiantes LIMIT 3")).fetchall()
    
    niveles = ['MEDIO', 'ALTO', 'BAJO']
    probabilidades = [65.5, 82.3, 45.0]
    
    for i, (est_id, codigo, nombre) in enumerate(estudiantes):
        session.execute(text("""
            INSERT INTO alertas_desercion (
                id_estudiante, nivel_riesgo, probabilidad_desercion, factores_riesgo,
                recomendaciones, estado, asignado_a, detectado_en
            ) VALUES (
                :est_id, :nivel, :prob,
                '{"faltas_consecutivas": 3, "promedio_bajo": false, "participacion_baja": true}'::jsonb,
                '{"accion_1": "Entrevista con orientador", "accion_2": "Llamar a tutor"}'::jsonb,
                'ACTIVA', 1, CURRENT_TIMESTAMP
            )
        """), {'est_id': est_id, 'nivel': niveles[i], 'prob': probabilidades[i]})
        print(f"  ⚠️  {nombre} - Riesgo {niveles[i]} ({probabilidades[i]}%)")
    
    session.commit()
    
    # 8. BADGES GANADOS
    print("\n🏆 Asignando badges ganados...")
    
    # Obtener badges
    badges = session.execute(text("SELECT id, nombre FROM badges LIMIT 3")).fetchall()
    estudiantes = session.execute(text("SELECT id FROM estudiantes LIMIT 3")).fetchall()
    
    for i, (badge_id, badge_nombre) in enumerate(badges):
        if i < len(estudiantes):
            session.execute(text("""
                INSERT INTO estudiantes_badges (
                    id_estudiante, id_badge, fecha_obtencion, periodo_academico,
                    metadata_json
                ) VALUES (
                    :est_id, :badge_id, CURRENT_TIMESTAMP, '2025-2',
                    '{"razon": "Cumplió requisitos automáticamente"}'::jsonb
                )
            """), {'est_id': estudiantes[i][0], 'badge_id': badge_id})
            print(f"  🏆 Badge '{badge_nombre}' otorgado")
    
    # Actualizar puntos de estudiantes
    session.execute(text("""
        UPDATE estudiantes 
        SET puntos_acumulados = 150, nivel = 2
        WHERE id IN (SELECT id FROM estudiantes LIMIT 3)
    """))
    print(f"  ✅ Actualizado puntos y nivel de 3 estudiantes")
    
    session.commit()
    
    # 9. RANKING MENSUAL
    print("\n🏅 Generando ranking mensual...")
    
    for i, (est_id,) in enumerate(estudiantes):
        session.execute(text("""
            INSERT INTO ranking_mensual (
                anio, mes, id_estudiante, total_puntos, total_asistencias,
                porcentaje_puntualidad, badges_obtenidos, posicion
            ) VALUES (
                2025, 11, :est_id, :puntos, :asist, :puntual, :badges, :pos
            )
        """), {
            'est_id': est_id, 'puntos': 150 - i*20, 'asist': 20 - i*2,
            'puntual': 95.0 - i*5, 'badges': 3 - i, 'pos': i + 1
        })
    print(f"  ✅ Ranking de noviembre 2025 generado")
    
    session.commit()
    
    # 10. ESTADÍSTICAS DIARIAS
    print("\n📊 Generando estadísticas diarias...")
    
    for materia_id, materia_nombre in materias:
        session.execute(text("""
            INSERT INTO estadisticas_diarias (
                fecha, id_materia, total_estudiantes, total_presentes, total_ausentes,
                total_tardanzas, total_justificados, total_virtuales,
                porcentaje_asistencia, porcentaje_puntualidad
            ) VALUES (
                CURRENT_DATE, :mat_id, 1, 1, 0, 0, 0, 1, 100.0, 100.0
            )
        """), {'mat_id': materia_id})
        print(f"  📊 Stats para {materia_nombre} - 100% asistencia")
    
    session.commit()
    
    # 11. REPORTES GENERADOS
    print("\n📑 Registrando reportes generados...")
    
    reportes = [
        ('ASISTENCIA_MENSUAL', 'reporte_asistencia_nov_2025.pdf', 'PDF'),
        ('ESTUDIANTES_RIESGO', 'alertas_desercion_2025.xlsx', 'EXCEL'),
        ('RANKING_MATERIA', 'ranking_programacion_iv.pdf', 'PDF'),
    ]
    
    for tipo, archivo, formato in reportes:
        session.execute(text("""
            INSERT INTO reportes_generados (
                tipo, nombre_archivo, formato, filtros_json, ruta_archivo,
                tamano_bytes, generado_por, expira_en
            ) VALUES (
                :tipo, :archivo, :formato,
                '{"periodo": "2025-11", "materia": "PROGRAMACIÓN IV"}'::jsonb,
                '/reportes/2025/11/' || :archivo, 524288, 1,
                CURRENT_TIMESTAMP + INTERVAL '30 days'
            )
        """), {'tipo': tipo, 'archivo': archivo, 'formato': formato})
        print(f"  📑 {archivo}")
    
    session.commit()
    
    # 12. ASISTENTE - Historial de comandos
    print("\n🎤 Registrando comandos del asistente por voz...")
    
    comandos = [
        ("Muéstrame la asistencia de hoy", "CONSULTAR_ASISTENCIA", 
         "Hoy asistieron 2 estudiantes de 2 inscritos (100%)", True),
        ("Genera un reporte de la semana", "GENERAR_REPORTE",
         "Reporte semanal generado exitosamente", True),
        ("Quién tiene más faltas", "CONSULTAR_ESTADISTICAS",
         "No hay estudiantes con faltas esta semana", True),
    ]
    
    for comando, intencion, respuesta, exito in comandos:
        session.execute(text("""
            INSERT INTO asistente_historial (
                id_usuario, comando_texto, comando_tipo, intencion, 
                entidades_json, respuesta_texto, respuesta_tipo,
                acciones_ejecutadas, exito, duracion_ms
            ) VALUES (
                1, :comando, 'VOZ', :intencion,
                '{"entidades": ["asistencia", "hoy"]}'::jsonb,
                :respuesta, 'TEXTO',
                '{"accion": "query_ejecutado"}'::jsonb,
                :exito, 1250
            )
        """), {
            'comando': comando, 'intencion': intencion,
            'respuesta': respuesta, 'exito': exito
        })
        print(f"  🎤 '{comando}'")
    
    session.commit()
    
    # 13. AUDIT LOG
    print("\n📋 Registrando acciones en audit log...")
    
    acciones = [
        ('DOCENTE', 1, 'LOGIN', 'PersonalAdmin', 'Inicio de sesión exitoso'),
        ('DOCENTE', 1, 'CREAR', 'Materia', 'Creó materia PROGRAMACIÓN IV'),
        ('DOCENTE', 1, 'TOMAR_ASISTENCIA', 'AsistenciaLog', 'Tomó asistencia facial'),
        ('DOCENTE', 1, 'APROBAR', 'Justificacion', 'Aprobó justificación médica'),
        ('DOCENTE', 1, 'GENERAR', 'CodigoTemporal', 'Generó código QR para clase virtual'),
    ]
    
    for usuario_tipo, usuario_id, accion, entidad, descripcion in acciones:
        session.execute(text("""
            INSERT INTO audit_log (
                usuario_tipo, usuario_id, accion, entidad, descripcion,
                datos_anteriores, datos_nuevos, ip_address, user_agent
            ) VALUES (
                :tipo, :uid, :accion, :entidad, :desc,
                '{}'::jsonb, '{"estado": "completado"}'::jsonb,
                '192.168.1.1', 'Mozilla/5.0'
            )
        """), {
            'tipo': usuario_tipo, 'uid': usuario_id, 'accion': accion,
            'entidad': entidad, 'desc': descripcion
        })
    print(f"  📋 {len(acciones)} acciones registradas")
    
    session.commit()
    
    # RESUMEN FINAL
    print("\n" + "="*100)
    print("✅ DATOS DE PRUEBA INSERTADOS EXITOSAMENTE")
    print("="*100)
    
    # Contar registros
    counts = {
        'tutores': session.execute(text("SELECT COUNT(*) FROM tutores")).scalar(),
        'codigos_temporales': session.execute(text("SELECT COUNT(*) FROM codigos_temporales")).scalar(),
        'asistencia_log': session.execute(text("SELECT COUNT(*) FROM asistencia_log")).scalar(),
        'asistencia_virtual': session.execute(text("SELECT COUNT(*) FROM asistencia_virtual")).scalar(),
        'notificaciones_internas': session.execute(text("SELECT COUNT(*) FROM notificaciones_internas")).scalar(),
        'justificaciones': session.execute(text("SELECT COUNT(*) FROM justificaciones")).scalar(),
        'alertas_desercion': session.execute(text("SELECT COUNT(*) FROM alertas_desercion")).scalar(),
        'estudiantes_badges': session.execute(text("SELECT COUNT(*) FROM estudiantes_badges")).scalar(),
        'ranking_mensual': session.execute(text("SELECT COUNT(*) FROM ranking_mensual")).scalar(),
        'estadisticas_diarias': session.execute(text("SELECT COUNT(*) FROM estadisticas_diarias")).scalar(),
        'reportes_generados': session.execute(text("SELECT COUNT(*) FROM reportes_generados")).scalar(),
        'asistente_historial': session.execute(text("SELECT COUNT(*) FROM asistente_historial")).scalar(),
        'audit_log': session.execute(text("SELECT COUNT(*) FROM audit_log")).scalar(),
    }
    
    print("\n📊 REGISTROS POR TABLA:")
    for tabla, count in counts.items():
        print(f"  ✅ {tabla:<25} {count:>3} registros")
    
    print("\n🎉 ¡LISTO PARA PROBAR TODAS LAS FUNCIONALIDADES!")
    print("\nAhora puedes:")
    print("  1. Ver notificaciones en el dashboard")
    print("  2. Ver asistencias de hoy y ayer")
    print("  3. Ver alertas de deserción")
    print("  4. Ver badges ganados por estudiantes")
    print("  5. Ver ranking mensual")
    print("  6. Ver historial del asistente por voz")
    print("  7. Ver justificaciones aprobadas")
    print("  8. Ver tutores asignados")
    print("  9. Ver códigos QR generados")
    print("  10. Ver audit log completo")
    
    print("\n" + "="*100 + "\n")

except Exception as e:
    print(f"\n❌ ERROR: {e}")
    session.rollback()
    import traceback
    traceback.print_exc()
finally:
    session.close()
