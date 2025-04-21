PATHS = [
{
   "path": "/services?request=VACATION",
   "description": "Solicitar vacaciones, Vacaciones, tiempo libre, tiempo para mi",
   "contract_type": "direct",
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
   "contract_type": "contractor",
   "short_description": "Service interruption"
},
  {
   "path": "/services?request=GYM",   
   "description": "Solicitar beneficio de gimnasio, mantenerse en forma, hustle for the muscle",
   "contract_type": "any",
   "short_description": "Hustle for the Muscle",
},
   {
   "path": "/services?request=PTO",   
   "description": "Quisiera poder solicitar mi dia de la familia. Solicitar un tiempo libre sin afectar mis vacaciones",
   "contract_type": "direct",
   "short_description": "PTO",
},
   {
   "path": "/services?request=OTHER_SERVICE_INTERRUPTION",   
   "description": "Quisiera poder solicitar mi dia de la familia. Solicitar un tiempo libre sin afectar mis PTOs",
   "contract_type": "contractor",  
   "short_description": "Other service interruption",
},
  {
   "path": "/services?request=EDUCATION",
   "description": "Quisiera poder solicitar un libro, un curso, bono para libro o curso, recurso educativo",
   "contract_type": "any",
   "short_description": "Brain power",
},
{
   "path": "/services?request=BIRTHDAY",
   "description": "Quisiera poder solicitar libre mi dia de cumpleaños",
   "contract_type": "direct",
   "short_description": "Birthday",
},
{
   "path": "/services?request=SPECIAL_REQUEST",
   "description": "Como pido un regalo de condolencias, matrimonio, enfermedad medica para un compañero de trabajo"
},
{
   "path": "/warrior-checkup",
   "description": "Donde veo los resultados de mi evaluacion anual"
}
]
