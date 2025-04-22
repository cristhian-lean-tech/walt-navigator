PATHS = [
    {
        "path": "/services?request=VACATION",
        "description": "Solicitar vacaciones, Vacaciones, tiempo libre, tiempo para mi",
        "user_type": "direct",
        "short_description": "Vacations",
        "parametros": [
            {
                "id": "start_date",
                "text": "fecha de inicio de sus vacaciones"
            },
            {
                "id": "end_date",
                "text": "fecha de fin de sus vacaciones"
            }
        ]
    },
    {
        "path": "/services?request=SERVICE_INTERRUPTION",
        "description": "Solicitar vacaciones, service interruption, tiempo libre, tiempo para mi, days off",
        "user_type": "contractor",
        "short_description": "Service interruption"
    },
    {
        "path": "/services?request=GYM",   
        "description": "Solicitar beneficio de gimnasio, mantenerse en forma, hustle for the muscle",
        "user_type": "any",
        "short_description": "Hustle for the Muscle",
    },
    {
        "path": "/services?request=PTO",   
        "description": "Quisiera poder solicitar mi dia de la familia. Solicitar un tiempo libre sin afectar mis vacaciones",
        "user_type": "direct",
        "short_description": "PTO",
    },
    {
        "path": "/services?request=OTHER_SERVICE_INTERRUPTION",   
        "description": "Quisiera poder solicitar mi dia de la familia. Solicitar un tiempo libre sin afectar mis PTOs",
        "user_type": "contractor",  
        "short_description": "Other service interruption",
    },
    {
        "path": "/my-board/brain-power-requests",
        "description": "Quisiera poder solicitar un libro, un curso, bono para libro o curso, recurso educativo",
        "user_type": "any",
        "short_description": "Brain power",
    },
    {
        "path": "/services?request=BIRTHDAY",
        "description": "Quisiera poder solicitar libre mi dia de cumpleaños",
        "user_type": "direct",
        "short_description": "Birthday"
    },
    {
        "path": "/services?request=SPECIAL_REQUEST",
        "description": "Como pido un regalo de condolencias, matrimonio, enfermedad medica para un compañero de trabajo, ocacion especial, detalle para un compañero",
        "user_type": "any",
        "short_description": "Special occasion"
    },
    {
         "path": "/services?request=DOCUMENT_REQUEST",
         "description": "Como pido un documento, carta de trabajo, referencia laboral",
         "user_type": "any",
         "short_description": "Document request"
    },
    {
        "path": "/warrior-checkup",        
        "description": "Donde veo los resultados de mi evaluacion anual",
         "user_type": "any",
         "short_description": "Warrior checkup"
    },
    {
        "path": "/requests?request=ETP",        
        "description": "Solicitar clases de ingles, mejorar mi nivel de ingles, evaluar nivel de ingles",
         "user_type": "any",
         "short_description": "ETP"
    },
    {
        "path": "/requests?request=GROWTH_PLAN",        
        "description": "Subir mi seniority, plan de crecimiento, plan de carrera, como subo de nivel",
         "user_type": "any",
         "short_description": "Growth plan"
    },
    {
        "path": "/my-board/services/update-info",        
        "description": "Actualizar mis datos personales, actualizar mi direccion, actualizar mi telefono, actualizar mi correo",
        "user_type": "any",
        "short_description": "Update info"
    }
]