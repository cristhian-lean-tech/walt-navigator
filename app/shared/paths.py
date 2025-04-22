PATHS = [
    {
        "path": "/services?request=VACATION",
        "description": "Solicitar vacaciones anuales pagadas, pedir días de descanso continuos, holiday leave request, programar time off, definir fecha de inicio y fin, descanso remunerado, tiempo libre personal",
        "user_type": "direct",
        "short_description": "Vacations",
        "parametros": [
            {"id": "start_date", "text": "fecha de inicio de sus vacaciones"},
            {"id": "end_date",   "text": "fecha de fin de sus vacaciones"}
        ]
    },
    {
        "path": "/services?request=SERVICE_INTERRUPTION",
        "description": "Solicitar interrupción temporal de servicio o contrato, days off sin goce, pausa laboral por motivos personales, break de proyecto, suspensión breve de actividades",
        "user_type": "contractor",
        "short_description": "Service interruption"
    },
    {
        "path": "/services?request=GYM",
        "description": "Solicitar subsidio o reembolso de gimnasio, fitness membership, beneficio para mantenerse en forma, salud física, ejercicio, “hustle for the muscle”, fitness allowance",
        "user_type": "any",
        "short_description": "Hustle for the Muscle"
    },
    {
        "path": "/services?request=PTO",
        "description": "Solicitar Paid Time Off (PTO), día personal o familiar, tiempo libre pagado sin consumir vacaciones, single day off, descanso corto remunerado",
        "user_type": "direct",
        "short_description": "PTO"
    },
    {
        "path": "/services?request=OTHER_SERVICE_INTERRUPTION",
        "description": "Solicitar día de la familia u otra interrupción especial, tiempo libre excepcional para contratistas, pausa breve sin afectar PTO, permiso extraordinario",
        "user_type": "contractor",
        "short_description": "Other service interruption"
    },
    {
        "path": "/my-board/brain-power-requests",
        "description": "Solicitar beneficio educativo Brain Power: libro físico o digital, curso online, bono para material de estudio, recurso de aprendizaje, capacitación, upskilling",
        "user_type": "any",
        "short_description": "Brain power"
    },
    {
        "path": "/services?request=BIRTHDAY",
        "description": "Solicitar día libre de cumpleaños, birthday leave, celebrar mi cumpleaños sin trabajar, licencia pagada por cumpleaños",
        "user_type": "direct",
        "short_description": "Birthday"
    },
    {
        "path": "/services?request=SPECIAL_REQUEST",
        "description": "Pedir regalo de condolencias, boda, enfermedad, nacimiento u ocasión especial; detalle para compañero; special occasion gift request, gesture of support",
        "user_type": "any",
        "short_description": "Special occasion"
    },
    {
        "path": "/services?request=DOCUMENT_REQUEST",
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
        "path": "/requests?request=ETP",
        "description": "Solicitar English Training Program (ETP): clases de inglés, prueba de nivel, mejorar fluidez, evaluación de competencia lingüística",
        "user_type": "any",
        "short_description": "ETP"
    },
    {
        "path": "/requests?request=GROWTH_PLAN",
        "description": "Crear o revisar Growth Plan: plan de carrera, roadmap de crecimiento profesional, aumentar seniority, metas de desarrollo y promoción",
        "user_type": "any",
        "short_description": "Growth plan"
    },
    {
        "path": "/my-board/services/update-info",
        "description": "Actualizar información personal: dirección, teléfono, correo electrónico, datos de contacto, perfil de empleado, update personal data",
        "user_type": "any",
        "short_description": "Update info"
    }
]
