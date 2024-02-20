import datetime
import logging
import smtplib
import json
import requests
import csv
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Configuración de registro de errores
#logging.basicConfig(filename='log.txt', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


url = "https://demo-cadera.fundaciontrauma.org.ar/api/importador"

csv_file = 'C:/Users/Hernán Ifrán/Downloads/RAFCAprueba2 - cadera.csv'

with open(csv_file, 'r') as csvfile:
    
    df = csv.DictReader(csvfile)

    success_count = 0
    error_count = 0
    error_ids = []
    failed_records=[]
    data = []



    for row in df:
       
            patient_data = {
                "Id": row['Id'],
                "OrganizacionId": 57,
                "Token": "c8fab994-8686-4ec1-964e-330ffc9e9d7d",
                "Hechos": [
                    {
                        "IdExterno": row['a1_03'],
                        "FechaHecho": datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),           
                        "FechaHechoSeDesconoce": row['FechaHechoSeDesconoce'],
                        "EsReinternacion": row['EsReinternacion'],
                        "Paciente": {
                            "PacienteMayor60": True,
                            "HistoriaClinica": row['a2_01'],
                            "TipoDocId": 99,
                            "FechaNacimiento": datetime.datetime.strptime(row['a2_08'], '%d/%m/%Y').strftime('%Y-%m-%d'),
                            "SexoId": row['a2_09'],
                            "GeneroId": row['a2_10'],
                            "DomicilioSeDesconoce": True,
                            "CodPostalSeDesconoce": True,
                            "TelefonoSeDesconoce": True,
                            "CorreoElectronicoSeDesconoce": True,
                            "ResidenciaAtencionId": row['a2_16'],
                            "CoberturaMedicaSNDId": row['a2_17'],
                            "TipoCoberturaId": row['a2_18']
                        },
                        "IngresoYAntecedentes": {
                            "FechaYHoraIngreso_HoraSeDesconoce": row['FechaYHoraIngreso_HoraSeDesconoce'],
                            "FechaYHoraIngreso": datetime.datetime.strptime(row['a3_01'], '%d/%m/%Y %H:%M').strftime('%Y-%m-%d %H:%M:%S'),
                            "DerivadosSNDId": 99,
                            "LugarPrimeraAtencionId": row['a3_04'],
                            "Peso": row['a3_05'],
                            "PesoSeDesconoce": row['PesoSeDesconoce'],
                            "Talla": row['a3_06'],
                            "TallaSeDesconoce": row['TallaSeDesconoce'],
                            "ValoracionCognitivaSNDId": row['ValoracionCognitivaSNDId'],
                            "ValoracionCognitiva": row['a3_07'],
                            "valoracionFuncionalSNDId": 99,
                            "riesgoNutricionalSNDId": 99,
                            "escalaFragilidadSNDId": 99,
                            "DolorIngresoSNDId": row['a3_11'],
                            "DolorIngresoId": row['a3_12'],
                            "IngresoYAntecedentes_ManejoDolor": [],
                            "CaidasPreviasSNDId": row['a3_14'],
                            "FracturasPreviasSNDId": row['a3_15'],
                            "MomentoFracturaPreviaId": row['a3_16'],
                            "IngresoYAntecedentes_LocalizacionFracturaPrevia": [],
                            "IngresoYAntecedentes_TratamientoIngreso": [],
                            "EvaluacionComorbilidadSNDId": row['EvaluacionComorbilidadSNDId'],
                            "IngresoYAntecedentes_EvaluacionComorbilidad": [],
                            "FracturaConcomitanteEnOtroLugarDelCuerpoSNDId": row['a4_02'],
                            "IngresoYAntecedentes_FracturaConcomitanteEnOtroLugarDelCuerpo": [],
                            "TratamientoOsteoprotectorSNDId": row['TratamientoOsteoprotectorSNDId'],
                            "TiempoTratamientoSNDId": "",
                            "TiempoTratamiento": "",
                            "TiempoSuspensionTratamientoSNDId": "",
                            "TiempoSuspensionTratamiento": "",
                            "FechaFractura":datetime.datetime.strptime(row['a4_01'], '%d/%m/%Y').strftime('%Y-%m-%d '),
                            "FechaFracturaSeDesconoce": row['FechaFracturaSeDesconoce'],
                            "LugarDondeFracturaId": row['a4_02'],
                            "FracturaPeriprotesicaSNDId": row['a4_08a'],
                            "MecanismoId": 9999,  
                            "CaderaAfectadaId": row['a4_04'],
                            "EvaluacionMovilidadPrefracturaSNDid": row['EvaluacionMovilidadPrefracturaSNDid'],
                            "puntajeEvaluacionMovilidadPrefractura": row['a3_22'],
                        },
                         "FracturaAtipica":  {
                           "ArbolFracturaAtipicaHecho": [],
                           "ArbolFractruaAtipicaTratamientoHecho": [
                               {
                                 "FracturaRelProtesisPreviaSND": int(row['FracturaRelProtesisPreviaSNDi']),
                                 "EsCaderaDerecha": False
                               },
                               {
                                 "FracturaRelProtesisPreviaSND": int(row['FracturaRelProtesisPreviaSNDd']),
                                 "EsCaderaDerecha": True  
                             }
                            ]
                            
                        },
                        "EstadiaYProcedimiento": {
                            "FechaHoraEvaluacionServicioSeDesconoce": True,
                            "TromboprofilaxisSNDId": row['a5_03'],
                            "Laboratorios": row['Laboratorios'],
                            "EstadoFisicoId": row['a5_07'],
                            "IntervencionQuirurgicaSNDId": row['a5_08'],
                            "FechaHoraCirugia": datetime.datetime.strptime(row['a5_09'], '%d/%m/%Y %H:%M:%S').strftime('%Y-%m-%d %H:%M:%S'),
                            "RetrasoCirugiaSNDId": 99,  
                            "EstadiaYProcedimiento_TipoCirugia": row['a5_12'], 
                            "OrigenMaterialId": row['a5_13'],
                            "EstadiaYProcedimiento_TipoAnestesia": [],
                            "RetiroSondaId": row['a5_15'],
                            "FechaHoraRetiroSondaSeDesconoce": True,
                            "MovilizacionPrecozId": row['a5_17'],
                            "EstadiaYProcedimiento_Complicaciones": [],
                            "ReintervencionQuirurgicaSNDId": row['a5_19'],  
                            "EvaluacionDeliriumId": row['a5_21'],
                            "EstadiaUCI_SNDId": 2,  
                            "LaboratorioSNDId": row['LaboratorioSNDId'],
                            "BaseInternacionId": row['a6_03'],
                            "FechaHoraCirugiaSeDesconoce": row['FechaHoraCirugiaSeDesconoce'],
                            "EstadiaYProcedimiento_PrimeraEvaluacionPorServiciosEspecificos": []
                        },
                        "Egreso": {
                            "ValoracionCognitivaEgresoSNDId": row['ValoracionCognitivaEgresoSNDId'],
                            "ValoracionCognitivaEgreso": row['a7_01'],
                            "EvaluacionRiesgoCaidaSNDId": 2,  
                            "EGRESO_TratamientoActualPrevio": [],
                            "DerivacionId": row['a7_05'],
                            "FechaHoraEgreso": datetime.datetime.strptime(row['a7_06'], '%d/%m/%Y %H:%M').strftime('%Y-%m-%d %H:%M:%S'),
                            "FechaHoraEgresoSeDesconoce": row['FechaHoraEgresoSeDesconoce'],
                            "CondicionEgresoId": row['a7_07'],
                            "DestinoEgresoId": row['a7_08']
                        },
                        "Seguimiento": {
                        }
                    }
                ]
            }
            
           
            
            for key, value in row.items():
                if key.startswith('a3_08') and value == '1':
                    id_comorbilidad = key.split('_')[-1][2:]
                    if id_comorbilidad:
                        patient_data['Hechos'][0]['IngresoYAntecedentes']['IngresoYAntecedentes_EvaluacionComorbilidad'].append(int(id_comorbilidad))
                if key.startswith('a3_21') and value == '1':
                    patient_data['Hechos'][0]['IngresoYAntecedentes']['IngresoYAntecedentes_EvaluacionComorbilidad'].append(int(key.split('_')[-1]))

            
            codigo_to_id = {
                'a4_02a1': 1,
                'a4_02a2': 25,
                'a4_02a3': 7,
                'a4_02a99': 99 
            }
            for key, value in row.items():
                if key in codigo_to_id and value == '1':
                    mapped_id = codigo_to_id[key]
                    patient_data['Hechos'][0]['IngresoYAntecedentes']['IngresoYAntecedentes_FracturaConcomitanteEnOtroLugarDelCuerpo'].append(mapped_id)

           
            for key, value in row.items():
                if key.startswith('a3_13') and value == '1':
                    id_manejo_dolor = key.split('_')[-1][2:]
                    if id_manejo_dolor:
                        patient_data['Hechos'][0]['IngresoYAntecedentes']['IngresoYAntecedentes_ManejoDolor'].append(int(id_manejo_dolor))

            
            for key, value in row.items():
                if key.startswith('a3_18') and value == '1':
                    id_tratamiento = key.split('_')[-1]
                    if id_tratamiento:
                        patient_data['Hechos'][0]['IngresoYAntecedentes']['IngresoYAntecedentes_TratamientoIngreso'].append(int(id_tratamiento))

            
            for key, value in row.items():
                if key.startswith('a3_17') and value == '1':
                    id_locfractura = key.split('_')[-1][2:]
                    if id_locfractura:
                        patient_data['Hechos'][0]['IngresoYAntecedentes']['IngresoYAntecedentes_LocalizacionFracturaPrevia'].append(int(id_locfractura))

            
            
            for key, value in row.items():
                if key.startswith('a5_14') and value == '1':
                    id_anestesia = key.split('_')[-1][2:]
                    if id_anestesia:
                        patient_data['Hechos'][0]['EstadiaYProcedimiento']['EstadiaYProcedimiento_TipoAnestesia'].append(int(id_anestesia))

            
            for key, value in row.items():
                if key.startswith('a5_18') and value == '1':
                    id_complicaciones = key.split('_')[-1][2:]
                    if id_complicaciones:
                     patient_data['Hechos'][0]['EstadiaYProcedimiento']['EstadiaYProcedimiento_Complicaciones'].append(int(id_complicaciones))

            
            for key, value in row.items():
                if key.startswith('a5_01') and value == '1':
                    id_PriSer = key.split('_')[-1][2:]
                    if id_PriSer:
                       patient_data['Hechos'][0]['EstadiaYProcedimiento']['EstadiaYProcedimiento_PrimeraEvaluacionPorServiciosEspecificos'].append(int(id_PriSer))              

            
            
            for key, value in row.items():
                if key.startswith('a7_04') and value == '1':
                   id_tratamientoegreso = key.split('_')[-1][2:]
                   if id_tratamientoegreso:
                     patient_data['Hechos'][0]['Egreso']['EGRESO_TratamientoActualPrevio'].append(int(id_tratamientoegreso)) 

            
         
            if row['Laboratorios']:
             labs_data = row['Laboratorios'].split(';')
             labs_list = []
             for lab_str in labs_data:
                lab_info = lab_str.split(',')
                labs_list.append({
                   'fechaLaboratorio': lab_info[0], 
                   'laboratorioId': lab_info[1],
                   'valor': lab_info[2]
                })
             patient_data['Hechos'][0]['EstadiaYProcedimiento']['EstadiaYProcedimiento_Laboratorio'] = labs_list
            else:
           
             patient_data['Hechos'][0]['EstadiaYProcedimiento']['EstadiaYProcedimiento_Laboratorio'] = []
            
            criterios_list_derecha = []
            if row['a4_05d'] == '3' and row['a4_06d'] in ['31', '32', '33', '34']:
            
             for i in range(1, 13):
                criterio_column_name = f'criterio_{i}'
                if row[criterio_column_name] == '1':
                 criterios_list_derecha.append({
                  'ArbolFracturaAtipicaCriteriosId': i,  
                  'FracturaRelProtesisPreviaSNDd':99,
                  "EsCaderaDerecha": True, 
                  
                 })

            
            criterios_list_izquierda = []
            if row['a4_05i'] == '3' and row['a4_06i'] in ['31', '32', '33', '34']:
            
             for i in range(1, 13):
                criterio_column_name = f'criterios_{i}'
                if row[criterio_column_name] == '1':
                 criterios_list_izquierda.append({
                  'ArbolFracturaAtipicaCriteriosId': i,  
                  'FracturaRelProtesisPreviaSNDi':99,
                  "EsCaderaDerecha": False,  
                  
                 })

            
            patient_data['Hechos'][0]['FracturaAtipica']['ArbolFracturaAtipicaCriteriosHecho'] = criterios_list_izquierda + criterios_list_derecha

          
            if row['a4_04'] == '3':
            
               patient_data['Hechos'][0]['FracturaAtipica']['ArbolFracturaAtipicaHecho']=[
               {   
                "EsCaderaDerecha": False,  # Izquierda
                "Nivel1Id": row['a4_05i'],
                "Nivel2Id": row['a4_06i'],
                "Nivel3Id": row['a4_07i'],
                "AplicaFormularioEspecial": row['AplicaFormularioEspeciali'],
                "MasEspecificaciones": row['MasEspecificaciones']
            },
            { 
               
                "EsCaderaDerecha": True,  # Derecha
                "Nivel1Id": row['a4_05d'],
                "Nivel2Id": row['a4_06d'],
                "Nivel3Id": row['a4_07d'],
                "AplicaFormularioEspecial": row['AplicaFormularioEspeciald'],
                "MasEspecificaciones": row['MasEspecificaciones']
            }
            ]
            elif row['a4_04'] == '1':
            
               patient_data['Hechos'][0]['FracturaAtipica']['ArbolFracturaAtipicaHecho'] = [
                {
                    "EsCaderaDerecha": False,
                    "Nivel1Id": row['a4_05i'],
                    "Nivel2Id": row['a4_06i'],
                    "Nivel3Id": row['a4_07i'],
                    "AplicaFormularioEspecial": row['AplicaFormularioEspeciali'],
                    "MasEspecificaciones": row['MasEspecificaciones']
                }
            ]
            elif row['a4_04'] == '2':
            
              patient_data['Hechos'][0]['FracturaAtipica']['ArbolFracturaAtipicaHecho'] = [
                {
                    "EsCaderaDerecha": True,
                    "Nivel1Id": row['a4_05d'],
                    "Nivel2Id": row['a4_06d'],
                    "Nivel3Id": row['a4_07d'],
                    "AplicaFormularioEspecial": row['AplicaFormularioEspeciald'],
                    "MasEspecificaciones": row['MasEspecificaciones']
                }
            ]
            else:
            
             patient_data['Hechos'][0]['FracturaAtipica']=[]


            if row['a7_07'] == '1': 
               seguimiento_data={}
               

               if row.get('HabilitarSeguimiento30dias','').lower() == 'true':
                seguimiento_data["HabilitarSeguimiento30dias"]=True
                seguimiento_data["FechaHoraContacto30SeDesconoce"]= row['FechaHoraContacto30SeDesconoce']
                seguimiento_data["FechaHoraContacto30"]=datetime.datetime.strptime(row['a8_01'], '%d/%m/%Y %H:%M:%S.%f').strftime('%Y-%m-%d %H:%M:%S.%f')
                seguimiento_data["Condicion30Id"]=row['a8_021']
                seguimiento_data["Residencia30Id"]= 99
                seguimiento_data["Reingreso30SNDId"]= 99
                seguimiento_data["Reintervencion30SNDId"]= 99
                seguimiento_data["CausaReingreso30Id"]= 99
                seguimiento_data["TratamientoOsteo30SND"]= row['TratamientoOsteo30SND']
                seguimiento_data["FechaInicioDeTratamiento30"]= datetime.datetime.strptime(row['a8_10'], '%d/%m/%Y %H:%M:%S').strftime('%Y-%m-%d %H:%M:%S')
                seguimiento_data["Seguimiento_TipoOsteo30"]= []
                
                if row.get('TratamientoOsteo30SND') == '1':
                 for key, value in row.items():
                  if key.startswith('a8_08_') and value == '1':
                    id_tiposteo30 = key.split('_')[-1]
                    if id_tiposteo30:
                     seguimiento_data['Seguimiento_TipoOsteo30'].append(int(id_tiposteo30))
                
                seguimiento_data["Seguimiento_MovilidadPostfractura30SNDId"]= row['MovilidadPostfractura30SNDId']
                seguimiento_data["Seguimiento_ValoracionDeambulacion30SNDId"]= 99
                seguimiento_data["ValoracionDependencia30SNDId"]= row['a8_09']
                seguimiento_data["ValoracionDependencia30"]= row['ValoracionDependencia30']
               else:
                 seguimiento_data["HabilitarSeguimiento30dias"] = False

               if row.get('HabilitarSeguimiento120dias','').lower() == 'true':
                 seguimiento_data["HabilitarSeguimiento120dias"]= True
                 seguimiento_data["FechaHoraContacto120diasSeDesconoce"]= row['FechaHoraContacto120diasSeDesconoce']
                 seguimiento_data["FechaHoraContacto120"]= datetime.datetime.strptime(row['a8_11'], '%d/%m/%Y %H:%M:%S.%f').strftime('%Y-%m-%d %H:%M:%S.%f')
                 seguimiento_data["Condicion120Id"]= row['a8_12']
                 seguimiento_data["Residencia120Id"]= 99
                 seguimiento_data["Reingreso120SNDId"]= 99
                 seguimiento_data["Reintervencion120SNDId"]: 99
                 seguimiento_data["CausaReingreso120Id"]= 99
                 seguimiento_data["TratamientoOsteo120SND"]= row['a8_13']
                 seguimiento_data["FechaInicioDeTratamiento120"]= datetime.datetime.strptime(row['FechaInicioDeTratamiento120'], '%d/%m/%Y %H:%M:%S').strftime('%Y-%m-%d %H:%M:%S')
                 seguimiento_data["Seguimiento_TipoOsteo120"]= []

                 if row.get('TratamientoOsteo120SND') == '1':
                  for key, value in row.items():
                   if key.startswith('a8_15_') and value == '1':
                    id_tiposteo120 = key.split('_')[-1]
                    if id_tiposteo120:
                      seguimiento_data['Seguimiento_TipoOsteo120'].append(int(id_tiposteo120))
                 seguimiento_data["Seguimiento_MovilidadPostFractura120SNDId"]= 99
                 seguimiento_data["Seguimiento_ValoracionDeambulacion120SNDId"]= 99
                 seguimiento_data["ValoracionDependencia120SNDId"]= row['ValoracionDependencia120SNDId']
                 seguimiento_data["ValoracionDependencia120"]= row['ValoracionDependencia120']
               else:
                 seguimiento_data["HabilitarSeguimiento120dias"] = False

               if row.get('HabilitarSeguimiento365dias','').lower() == 'true':
                  
                 seguimiento_data["HabilitarSeguimiento365dias"] = True
                 seguimiento_data["FechaHoraContacto365diasSeDesconoce"]= row['FechaHoraContacto365diasSeDesconoce']
                 seguimiento_data["FechaHoraContacto365dias"]=datetime.datetime.strptime(row['FechaHoraContacto365dias'], '%d/%m/%Y %H:%M:%S').strftime('%Y-%m-%d %H:%M:%S')
                 seguimiento_data["Condicion365Id"]= row['Condicion365Id']
                 seguimiento_data["TratamientoOsteo365SND"]= row['TratamientoOsteo365SND']
                 seguimiento_data["Seguimiento_TipoOsteo365"]= []
                 
                 if row.get('TratamientoOsteo365SND') == '1':
                  for key, value in row.items():
                   if key.startswith('a8_17_') and value == '1':
                    id_tiposteo365 = key.split('_')[-1]
                    if id_tiposteo365:
                     seguimiento_data['Seguimiento_TipoOsteo365'].append(int(id_tiposteo365)) 

                 seguimiento_data["ValoracionDependencia365SNDId"]= row['ValoracionDependencia365SNDId']
                 seguimiento_data["ValoracionDependencia365"]= row['ValoracionDependencia365']
               else:
                 seguimiento_data["HabilitarSeguimiento365dias"] = False

               if any(seguimiento_data.values()):
              
                patient_data['Hechos'][0]['Seguimiento'] = seguimiento_data
               else:
            
                patient_data['Hechos'][0]['Seguimiento'] = {
                "HabilitarSeguimiento30dias":False,
                "HabilitarSeguimiento120dias":False,
                "HabilitarSeguimiento365dias":False,
              }
            elif row['a7_07'] in ['2','99']:
            
             
             patient_data['Hechos'][0]['Seguimiento'] = {
             "HabilitarSeguimiento30dias": False,
             "HabilitarSeguimiento120dias": False,
             "HabilitarSeguimiento365dias": False,
             }
            else:
             patient_data['Hechos'][0]['Seguimiento'] = {}

        
            data.append(patient_data)
            with open('data.json', 'w') as jsonfile:
             json.dump(patient_data, jsonfile,indent=2,ensure_ascii=False)
            
            response = requests.post(url, json=patient_data)

           
            if response.status_code == 200:
               success_count += 1
         
            else:
             error_count += 1
             logging.error(f'Error en la solicitud POST: {response.text}')
             failed_records.append(row['Id'])

            


print(f"Registros exitosos: {success_count}")
print(f"Registros con errores: {error_count}")



log_message = f'Total de registros exportados: {success_count}\nExportaciones con errores e inconsistencias: {error_count}'
sender_email = 'desarrollo@fundaciontrauma.org.ar'
receiver_email = ['hernaninef11@gmail.com']#,'hifran@fundaciontrauma.org.ar']



email_message = MIMEMultipart("alternative")
email_message['Subject'] = 'Informe de procesamiento'
email_message['From'] = sender_email
email_message['To'] = ', '.join(receiver_email)
listahc = ', '.join(failed_records)

if failed_records:
   listahc= ', '.join(failed_records)
  
   html_content = f"""
    <html>
    <head>
        <style>
            .logo {{
                max-width: 125px;
                float: center;
                margin-right: 100px;
            }}
            .content {{
                overflow: hidden;
            }}
        </style>
    </head>
    <body>
        <div class="content">
            <img src="https://fundaciontrauma.org.ar/wp-content/uploads/2021/11/FT-LogoArriba-340x156-1.png" class="logo">
            <p>{log_message}</p>
            <p>Ids de exportación con errores: {listahc}</p>
            <p>Por favor ingrese <a href="https://comunidad.fundaciontrauma.org.ar/Account/Login">aquí</a> para acceder al Registro de Fractura de cadera al módulo de importación.</p>
            <p>Ante cualquier duda puede enviar un correo electrónico a hifran@fundaciontruma.org.ar</p>
            <img src="https://fundaciontrauma.org.ar/wp-content/uploads/2022/08/ESP-Pasos-1940x705-2.jpg" alt="Firma"style="width: 256px; height: auto;">
        </div>
    </body>
    </html>
    """
else:
    
   html_content = f"""
    <html>
    <head>
        <style>
            .logo {{
                max-width: 125px;
                float: center;
                margin-right: 100px;
            }}
            .content {{
                overflow: hidden;
            }}
        </style>
    </head>
    <body>
        <div class="content">
            <img src="https://fundaciontrauma.org.ar/wp-content/uploads/2021/11/FT-LogoArriba-340x156-1.png" class="logo">
            <p>{log_message}</p>
            <p>Por favor ingrese <a href="https://comunidad.fundaciontrauma.org.ar/Account/Login">aquí</a> para acceder al Registro de Fractura de cadera al módulo de importación.</p>
            <p>Ante cualquier duda puede enviar un correo electrónico a hifran@fundaciontruma.org.ar</p>
            <img src="https://fundaciontrauma.org.ar/wp-content/uploads/2022/08/ESP-Pasos-1940x705-2.jpg" alt="Firma"style="width: 256px; height: auto;">
        </div>
    </body>
    </html>
    """

 
html_part = MIMEText(html_content, "html")
email_message.attach(html_part)





with smtplib.SMTP('smtp.gmail.com', 587) as smtp_server:
     smtp_server.starttls()
     smtp_server.login('', '')
     smtp_server.sendmail(sender_email, receiver_email, email_message.as_string())
