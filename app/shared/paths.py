PATHS = [
    {
        "path": "/my-board/services/time-off?action=vacation",
        "description": "Solicitar vacaciones anuales pagadas, pedir días de descanso continuos, holiday leave request, programar time off, definir fecha de inicio y fin, descanso remunerado, tiempo libre personal",
        "user_type": "direct",
        "short_description": "Vacations",
        "parametros": [
            {"id": "start_date", "text": "fecha de inicio de sus vacaciones"},
            {"id": "end_date",   "text": "fecha de fin de sus vacaciones"}
        ]
    },
    {
        "path": "/my-board/services/time-off?action=serviceInterruption",
        "description": "Solicitar interrupción temporal de servicio o contrato, days off sin goce, pausa laboral por motivos personales, break de proyecto, suspensión breve de actividades",
        "user_type": "contractor",
        "short_description": "Service interruption"
    },
    {
        "path": "/my-board/services/hustle-for-the-muscle?action=create",
        "description": "Solicitar subsidio o reembolso de gimnasio, fitness membership, beneficio para mantenerse en forma, salud física, ejercicio, “hustle for the muscle”, fitness allowance",
        "user_type": "any",
        "short_description": "Hustle for the Muscle"
    },
    {
        "path": "/my-board/services/time-off?action=takeCareTime",
        "description": "Solicitar Paid Time Off (PTO), día personal o familiar, tiempo libre pagado sin consumir vacaciones, single day off, descanso corto remunerado",
        "user_type": "direct",
        "short_description": "PTO"
    },
    {
        "path": "/my-board/services/time-off?action=otherServiceInterruption",
        "description": "Solicitar día de la familia u otra interrupción especial, tiempo libre excepcional para contratistas, pausa breve sin afectar PTO, permiso extraordinario",
        "user_type": "contractor",
        "short_description": "Other service interruption"
    },
    {
        "path": "/my-board/services/brain-power?action=create",
        "description": "Solicitar beneficio educativo Brain Power: libro físico o digital, curso online, bono para material de estudio, recurso de aprendizaje, capacitación, upskilling",
        "user_type": "any",
        "short_description": "Brain power"
    },
    {
        "path": "/my-board/services/time-off?action=birthday",
        "description": "Solicitar día libre de cumpleaños, birthday leave, celebrar mi cumpleaños sin trabajar, licencia pagada por cumpleaños",
        "user_type": "direct",
        "short_description": "Birthday"
    },
    {
        "path": "/my-board/services/special-occasions?action=create",
        "description": "Pedir regalo de condolencias, boda, enfermedad, nacimiento u ocasión especial; detalle para compañero; special occasion gift request, gesture of support",
        "user_type": "any",
        "short_description": "Special occasion"
    },
    {
        "path": "/my-board/services/documents",
        "description": "Solicitar documentos laborales: carta de trabajo, constancia salarial, referencia laboral, employment verification letter",
        "user_type": "any",
        "short_description": "Document request"
    },
    {
        "path": "/warrior-checkup",
        "description": "Consultar resultados de mi evaluación anual (Warrior Checkup), performance review, feedback de desempeño, puntuación de evaluación",
        "user_type": "any",
        "short_description": "Warrior checkup"
    },
    {
        "path": "/my-board/growth/etp?action=create",
        "description": "Solicitar English Training Program (ETP): clases de inglés, prueba de nivel, mejorar fluidez, evaluación de competencia lingüística",
        "user_type": "any",
        "short_description": "ETP"
    },
    {
        "path": "/my-board/growth/technical-plan?action=create",
        "description": "Crear o revisar Growth Plan: plan de carrera, roadmap de crecimiento profesional, aumentar seniority, metas de desarrollo y promoción",
        "user_type": "any",
        "short_description": "Growth plan"
    },
    {
        "path": "/my-board/services/update-info?action=create",
        "description": "Actualizar información personal: dirección, teléfono, correo electrónico, datos de contacto, perfil de empleado, update personal data",
        "user_type": "any",
        "short_description": "Update info"
    },
    {
        "path": "https://walt.lean-tech.io/my-board/services/it-support",
        "description": "Solicitar ayuda técnica general: problema con el equipo, software, conexión, actualizaciones, configuración, soporte técnico, IT support, technical issue",
        "user_type": "any",
        "short_description": "IT support"
    }
]
