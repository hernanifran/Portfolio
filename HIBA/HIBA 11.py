import datetime
import logging
import smtplib
import json
import requests
import csv
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


url = "https://demo-cadera.fundaciontrauma.org.ar/api/importador"

csv_file = 'C:/Users/Hernán Ifrán/Downloads/HIBA CSV Modelo - cadera.csv'


with open(csv_file, 'r') as csvfile:
    
    df = csv.DictReader(csvfile)

    success_count = 0
    error_count = 0
    error_ids = []
    failed_records=[]
    data = []

    def convert_to_bool(value):
              if value.lower() == 'true':
               return True
              elif value.lower() == 'false':
                return False
              else:
           # Manejar otros casos si es necesario
                return None  

    for row in df:
         
            patient_data = {
                "Id": row['Id'],
                "OrganizacionId": 57,
                "Token": "c8fab994-8686-4ec1-964e-330ffc9e9d7d",
                "Hechos": [
                    {
                        "IdExterno": int(row['a1_03']),
                        "FechaHecho": datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S'),  
                        "FechaHechoSeDesconoce": False,
                        "OrganizacionId": 57,
                        "EsReinternacion": convert_to_bool(row['EsReinternacion']),
                        "EstadoId":int (row['EstadoId']),
                        "Paciente": {
                            "PacienteMayor60": True,
                            "HistoriaClinica": row['a2_01'],
                            "TipoDocId": 99,
                            "NroDoc":None,
                            "OtrosApellidoSeDesconoce":True,
                            "FechaNacimiento": datetime.datetime.strptime(row['a2_08'], '%d/%m/%Y').strftime('%Y-%m-%d'),
                            "SexoId": int(row['a2_09']),
                            "GeneroId": int(row['a2_10']),
                            "DomicilioSeDesconoce": True,
                            "CodPostalSeDesconoce": True,
                            "HistoriaClinicaSeDesconoce": False,
                            "TelefonoSeDesconoce": True,
                            "CorreoElectronicoSeDesconoce": True,
                            "ResidenciaAtencionId": int(row['a2_16']),
                            "CoberturaMedicaSNDId": int(row['a2_17']),
                            "TipoCoberturaId": int(row['a2_18'])
                        },
                        "IngresoYAntecedentes": {
                            "FechaYHoraIngreso_HoraSeDesconoce": convert_to_bool(row['FechaYHoraIngreso_HoraSeD']),
                            "FechaYHoraIngreso": datetime.datetime.strptime(row['a3_01'], '%d/%m/%Y %H:%M:%S').isoformat(),
                            "DerivadosSNDId": 99,
                            "LugarPrimeraAtencionId": int(row['a3_04']),
                            "Peso": int(row['a3_05'])if row['a3_05'] else None,
                            "PesoSeDesconoce": convert_to_bool (row['PesoSeDesconoce']),
                            "Talla":int( row['a3_06'])if row['a3_06'] else None,
                            "TallaSeDesconoce": convert_to_bool(row['TallaSeDesconoce']),
                            "ValoracionCognitivaSNDId": int( row['ValoracionCognitivaSNDId']),
                            "ValoracionCognitiva":int( row['a3_07'])if row['a3_07'] else None,
                            "valoracionFuncionalSNDId": 99,
                            "riesgoNutricionalSNDId": 99,
                            "escalaFragilidadSNDId": 99,
                            "DolorIngresoSNDId":int( row['a3_11'])if row['a3_11'] else None,
                            "DolorIngresoId": int( row['a3_12'])if row['a3_12'] else None,
                            "IngresoYAntecedentes_ManejoDolor": [],
                            "CaidasPreviasSNDId": row['a3_14'],
                            "FracturasPreviasSNDId": int(row['a3_15'])if row['a3_15'] else None,
                            "MomentoFracturaPreviaId":int( row['a3_16'])if row['a3_16'] else None,
                            "IngresoYAntecedentes_LocalizacionFracturaPrevia": [],
                            "IngresoYAntecedentes_TratamientoIngreso": [],  
                            "EvaluacionComorbilidadSNDId": int(row['a3_08'])if row['a3_08'] else None, 
                            "IngresoYAntecedentes_EvaluacionComorbilidad": [],
                            "FracturaConcomitanteEnOtroLugarDelCuerpoSNDId": int (row['FracturaConcomitante'])if row['FracturaConcomitante'] else None,
                            "IngresoYAntecedentes_FracturaConcomitanteEnOtroLugarDelCuerpo": [],
                            "TratamientoOsteoprotectorSNDId": int(row['TratamientoOsteoprotectorSNDId'])if row['TratamientoOsteoprotectorSNDId'] else None,
                            "TiempoTratamientoSNDId": row['TiempoTratamientoSNDId'],
                            "TiempoTratamiento": row['a3_19'],
                            "TiempoSuspensionTratamientoSNDId": row['TiempoSuspensionTratamientoSNDId'],
                            "TiempoSuspensionTratamiento": row['a3_20'],
                            "FechaFractura":datetime.datetime.strptime(row['a4_01'], '%d/%m/%Y').isoformat() if row['a4_01'] else None, 
                            "FechaFracturaSeDesconoce": convert_to_bool(row['FechaFracturaSeDesconoce']),
                            "LugarDondeFracturaId": int(row['a4_02'])if row['a4_02'] else None,
                            "FracturaPeriprotesicaSNDId": int(row['a4_08a'])if row['a4_08a'] else None,
                            "MecanismoId": 9999,  
                            "CaderaAfectadaId": int (row['a4_04'])if row['a4_04'] else None,
                            "EvaluacionMovilidadPrefracturaSNDid": int(row['EvalMovilidadPreSNDid'])if row['EvalMovilidadPreSNDid'] else None,
                            "puntajeEvaluacionMovilidadPrefractura": int(row['a3_22'])if row['a3_22'] else None,
                        },
                        "FracturaAtipica":  {
                           "ArbolFracturaAtipicaHecho": [],
                           "ArbolFractruaAtipicaTratamientoHecho": [
                               {
                                 "DesconoceSuspencionTratamientoMeses": True,
                                 "FracturaRelProtesisPreviaSND": int(row['FracturaRelProtesisPreviaSNDi'])if row['FracturaRelProtesisPreviaSNDi'] else None,
                                 "EsCaderaDerecha": False
                               },
                               {
                                 "DesconoceSuspencionTratamientoMeses": True,
                                 "FracturaRelProtesisPreviaSND": int (row['FracturaRelProtesisPreviaSNDd'])if row['FracturaRelProtesisPreviaSNDd'] else None,
                                 "EsCaderaDerecha": True  
                             }
                            ],
                            "ArbolFracturaAtipicaConsumoDrogasHecho": [],
                            "ArbolFracturaAtipicaCriteriosHecho": [
                             {
                              "ArbolFracturaAtipicaCriteriosId": 1,
                              "EsCaderaDerecha": False
                             },    
                            ]
                         

                        },
                        "EstadiaYProcedimiento": {
                            "FechaHoraEvaluacionServicioSeDesconoce": True,
                            "TromboprofilaxisSNDId": int (row['a5_03'])if row['a5_03'] else None,
                            "EstadoFisicoId": int(row['a5_07'])if row['a5_07'] else None,
                            "IntervencionQuirurgicaSNDId": row['a5_08'],#if row['a5_08'] else None,
                            "FechaHoraCirugiaSeDesconoce": convert_to_bool (row['a5_09']),
                            "FechaHoraCirugia": datetime.datetime.strptime(row['a5_10'], '%d/%m/%Y %H:%M:%S').isoformat()if row['a5_10'] else None,
                            "RetrasoCirugiaSNDId": int(row['RetrasoCirugiaSNDId'])if row['RetrasoCirugiaSNDId'] else None,
                            "EstadiaYProcedimiento_MotivoDemora":[99],
                            "EstadiaYProcedimiento_TipoCirugia":[],
                            "OrigenMaterialId": int(row['a5_13'])if row['a5_13'] else None,
                            "EstadiaYProcedimiento_TipoAnestesia": [],
                            "RetiroSondaId": int(row['a5_15']) if row['a5_15'] is None else 99,
                            "FechaHoraRetiroSondaSeDesconoce": True,
                            "MovilizacionPrecozId": int(row['a5_17'])if row['a5_17'] else None,
                            "EstadiaYProcedimiento_Complicaciones": [],
                            "ReintervencionQuirurgicaSNDId":int( row['a5_19'])if row['a5_19'] else None,
                            "EstadiaYProcedimiento_TipoReintervencion": [],
                            "EvaluacionDeliriumId": int(row['a5_21'])if row['a5_21'] else None,
                            "EstadiaUCI_SNDId": int (row['UnidadCerradaSNSDId'])if row['UnidadCerradaSNSDId'] else None, 
                            "EstadiaYProcedimiento_EstadiaUCI": [], 
                            "LaboratorioSNDId":  int (row['LaboratorioSNDId'])if row['LaboratorioSNDId'] else None,
                            "EstadiaYProcedimiento_Laboratorio": [],
                            "BaseInternacionId":int( row['a6_03'])if row['a6_03'] else None,
                            "EstadiaYProcedimiento_PrimeraEvaluacionPorServiciosEspecificos": []
                        },
                        "Egreso": {
                            "ValoracionCognitivaEgresoSNDId": int (row['ValoracionCognitivaEgresoSNDId'])if row['ValoracionCognitivaEgresoSNDId'] else None,
                            "ValoracionCognitivaEgreso": int (row['a7_01'])if row['a7_01'] else None,
                            "EvaluacionRiesgoCaidaSNDId": 2,  
                            "EGRESO_TratamientoActualPrevio": [],
                            "DerivacionId": int (row['a7_05'])if row['a7_05'] else None,
                            "FechaHoraEgreso":datetime.datetime.strptime(row['a7_06'], '%d/%m/%Y %H:%M:%S').isoformat(),
                            "FechaHoraEgresoSeDesconoce": convert_to_bool( row['FechaHoraEgresoSeDesconoce']),
                            "CondicionEgresoId": int (row['a7_07'])if row['a7_07'] else None,
                            "DestinoEgresoId": int(row['a7_08'])if row['a7_08'] else None
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
                if key.startswith('a3_99') and value == '1':
                    patient_data['Hechos'][0]['IngresoYAntecedentes']['IngresoYAntecedentes_ManejoDolor'].append(int(key.split('_')[-1]))
            
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

            # Verificar y eliminar el campo TiempoTratamiento si es necesario
            if row['TiempoTratamientoSNDId'] in ['2', '99'] or row['TiempoTratamientoSNDId'] is None:
             patient_data['Hechos'][0]['IngresoYAntecedentes'].pop('TiempoTratamiento', None)
             
             # Verificar y eliminar el campo TiempoSuspensionTratamiento si es necesario
            if row['TiempoSuspensionTratamientoSNDId'] in ['2', '99'] or row['TiempoSuspensionTratamientoSNDId'] is None:
             patient_data['Hechos'][0]['IngresoYAntecedentes'].pop('TiempoSuspensionTratamiento', None)

            if row['a5_08'] == '1':
              patient_data['Hechos'][0]['EstadiaYProcedimiento']['EstadiaYProcedimiento_TipoCirugia'] = [row['a5_12']]
            elif row['a5_08'] in ['2', '99']:
              patient_data['Hechos'][0]['EstadiaYProcedimiento']['EstadiaYProcedimiento_TipoCirugia'] = []

            if row['a5_19'] == '1':
              patient_data['Hechos'][0]['EstadiaYProcedimiento']['EstadiaYProcedimiento_TipoReintervencion'] = [row['a5_20']]
            elif row['a5_08'] in ['2', '99']:
              patient_data['Hechos'][0]['EstadiaYProcedimiento']['EstadiaYProcedimiento_TipoReintervencion'] = []
            
            if row ['a3_18_99'] =='1':
             patient_data['Hechos'][0]['IngresoYAntecedentes']['TiempoTratamientoSNDId'] = None
             patient_data['Hechos'][0]['IngresoYAntecedentes']['TiempoSuspensionTratamientoSNDId'] = None
            
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

            


            if row['a6_01']:
             UCI_data=row['a6_01'].split(';')
             UCI_list = []
             for UCI_str in UCI_data:
                UCI_info = UCI_str.split(',')
                UCI_list.append({
                   'Dias': UCI_info[0], 
                   'Fecha':UCI_info[1],
                   'UnidadCerradaId': UCI_info[2]
                })
             patient_data['Hechos'][0]['EstadiaYProcedimiento']['EstadiaYProcedimiento_EstadiaUCI'] = UCI_list
            else:
           
             patient_data['Hechos'][0]['EstadiaYProcedimiento']['EstadiaYProcedimiento_EstadiaUCI'] = []
            
            if row['LaboratorioSNDId'] == '1': 
             if row['Laboratorios']:
              labs_data = row['Laboratorios'].split(';')
              labs_list = []
              for lab_str in labs_data:
                lab_info = lab_str.split(',')
                if len(lab_info) >= 2:
                 laboratorio_id = int(lab_info[1]) if lab_info[1] else 99
                 labs_list.append({
                   'fechaLaboratorio': lab_info[0], 
                   'laboratorioId': laboratorio_id,
                   'valor': lab_info[2]
                 })

                else:
                
                 print("Error: Formato incorrecto en los datos de laboratorio en la historia clínica:", row['Id'])
                 print("Datos de laboratorio que causaron el error:", lab_str) 
              patient_data['Hechos'][0]['EstadiaYProcedimiento']['EstadiaYProcedimiento_Laboratorio'] = labs_list
             else:
           
              patient_data['Hechos'][0]['EstadiaYProcedimiento']['EstadiaYProcedimiento_Laboratorio'] = []
            
            elif row['LaboratorioSNDId'] in ['2', '99']:
                patient_data['Hechos'][0]['EstadiaYProcedimiento']['EstadiaYProcedimiento_Laboratorio'] = []
                 
            criterios_list_derecha = []
            if row['a4_05d'] == '3' and row['a4_06d'] in ['31', '32', '33', '34']:
            
             for i in range(1, 13):
                criterio_column_name = f'criterio_{i}'
                if row[criterio_column_name] == '1':
                 criterios_list_derecha.append({
                  'ArbolFracturaAtipicaCriteriosId': i,  
                  #'FracturaRelProtesisPreviaSNDd':99,
                  "EsCaderaDerecha": True, 
                  
                 })

            
            criterios_list_izquierda = []
            if row['a4_05i'] == '3' and row['a4_06i'] in ['31', '32', '33', '34']:
            
             for i in range(1, 13):
                criterio_column_name = f'criterios_{i}'
                if row[criterio_column_name] == '1':
                 criterios_list_izquierda.append({
                  'ArbolFracturaAtipicaCriteriosId': i,  
                  #'FracturaRelProtesisPreviaSNDi':99,
                  "EsCaderaDerecha": False,  
                  
                 })

            
            patient_data['Hechos'][0]['FracturaAtipica']['ArbolFracturaAtipicaCriteriosHecho'] = criterios_list_izquierda + criterios_list_derecha

            
            

            if row['a4_04'] == '3':
               if row['a4_06i'] == '13'and row['a4_06d'] == '13':
                   row['a4_07i'] = None
                   row['a4_07d'] = None
               patient_data['Hechos'][0]['FracturaAtipica']['ArbolFracturaAtipicaHecho']=[
               {   
                "EsCaderaDerecha": False,  # Izquierda
                "Nivel1Id": row['a4_05i'],
                "Nivel2Id": row['a4_06i'],
                #"Nivel3Id": row['a4_07i'],
                **({"Nivel3Id": row['a4_07i']} if row['a4_07i'] is not None else {}),
                "AplicaFormularioEspecial": convert_to_bool(row['AplicaFormularioEspeciali']),
              #  "MasEspecificaciones": row['MasEspecificaciones']
            },
            { 
            
                "EsCaderaDerecha": True,  # Derecha
                "Nivel1Id": row['a4_05d'],
                "Nivel2Id": row['a4_06d'],
                #"Nivel3Id": row['a4_07d'],
                **({"Nivel3Id": row['a4_07d']} if row['a4_07d'] is not None else {}),
                "AplicaFormularioEspecial": convert_to_bool(row['AplicaFormularioEspeciald']),
              #  "MasEspecificaciones": row['MasEspecificaciones']
            }
            ]
            elif row['a4_04'] == '1':
                if row['a4_06i'] == '13':
                   row['a4_07i'] = None
                patient_data['Hechos'][0]['FracturaAtipica']['ArbolFracturaAtipicaHecho'] = [
                {
                    "EsCaderaDerecha": False,
                    "Nivel1Id": row['a4_05i'],
                    "Nivel2Id": row['a4_06i'],
                    #"Nivel3Id": row['a4_07i'],
                    **({"Nivel3Id": row['a4_07i']} if row['a4_07i'] is not None else {}),
                    "AplicaFormularioEspecial": convert_to_bool(row['AplicaFormularioEspeciali']),
                   # "MasEspecificaciones": row['MasEspecificaciones']
                }
            ]
            elif row['a4_04'] == '2':
                if row['a4_06d'] == '13':
                   row['a4_07d'] = None
                patient_data['Hechos'][0]['FracturaAtipica']['ArbolFracturaAtipicaHecho'] = [
                {
                    "EsCaderaDerecha": True,
                    "Nivel1Id": row['a4_05d'],
                    "Nivel2Id": row['a4_06d'],
                    #"Nivel3Id": row['a4_07d'],
                    **({"Nivel3Id": row['a4_07d']} if row['a4_07d'] is not None else {}),
                    "AplicaFormularioEspecial":convert_to_bool(row['AplicaFormularioEspeciald']),
                    #"MasEspecificaciones": row['MasEspecificaciones']
                }
            ]
            else:
            
             patient_data['Hechos'][0]['FracturaAtipica']=[]

            
            


            if row['a7_07'] == '1': 
               seguimiento_data={}
               

               if row.get('HabilitarSeguimiento30dias','').lower() == 'true':
                seguimiento_data["HabilitarSeguimiento30dias"]=True
                seguimiento_data["FechaHoraContacto30SeDesconoce"]= convert_to_bool (row['FechaHoraContacto30SeDesconoce'])
                seguimiento_data["FechaHoraContacto30"]=datetime.datetime.strptime(row['a8_01'], '%d/%m/%Y %H:%M:%S').isoformat(),
                seguimiento_data["Condicion30Id"]=int (row['a8_021'])if row['a8_021'] else None 
                seguimiento_data["Residencia30Id"]= 99
                seguimiento_data["Reingreso30SNDId"]= 99
                seguimiento_data["Reintervencion30SNDId"]= 99
                seguimiento_data["CausaReingreso30Id"]= 99
                seguimiento_data["TratamientoOsteo30SND"]= int(row['TratamientoOsteo30SND'])if row['TratamientoOsteo30SND'] else None
                seguimiento_data["FechaInicioDeTratamiento30"]= datetime.datetime.strptime(row['a8_10'], '%d/%m/%Y %H:%M:%S').strftime('%Y-%m-%d %H:%M:%S')
                seguimiento_data["Seguimiento_TipoOsteo30"]= []
                
                if row.get('TratamientoOsteo30SND') == '1':
                 for key, value in row.items():
                  if key.startswith('a8_08_') and value == '1':
                    id_tiposteo30 = key.split('_')[-1]
                    if id_tiposteo30:
                     seguimiento_data['Seguimiento_TipoOsteo30'].append(int(id_tiposteo30))
                
                seguimiento_data["Seguimiento_MovilidadPostfractura30SNDId"]= int(row['Seguimiento_MovilidadPostfractura30SNDId'])if row['Seguimiento_MovilidadPostfractura30SNDId'] else None
                seguimiento_data["Seguimiento_ValoracionDeambulacion30SNDId"]= 99
                seguimiento_data["ValoracionDependencia30SNDId"]= int(row['a8_09'])if row['a8_09'] else None
                seguimiento_data["ValoracionDependencia30"]= int (row['ValoracionDependencia30'])if row['ValoracionDependencia30'] else None
               else:
                 seguimiento_data["HabilitarSeguimiento30dias"] = False

               if row.get('HabilitarSeguimiento120dias','').lower() == 'true':
                 seguimiento_data["HabilitarSeguimiento120dias"]= True
                 seguimiento_data["FechaHoraContacto120diasSeDesconoce"]= row['FechaHoraContacto120diasSeDesconoce']
                 seguimiento_data["FechaHoraContacto120"]= datetime.datetime.strptime(row['a8_11'], '%d/%m/%Y %H:%M:%S.%f').strftime('%Y-%m-%d %H:%M:%S.%f')
                 seguimiento_data["Condicion120Id"]= row['a8_12']
                 seguimiento_data["Residencia120Id"]= 99
                 seguimiento_data["Reingreso120SNDId"]= 99
                 seguimiento_data["Reintervencion120SNDId"]: 99 # type: ignore
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
             if 'Seguimiento' in patient_data['Hechos'][0]:
                del patient_data['Hechos'][0]['Seguimiento']
            
            
            
            


            
        
            data.append(patient_data)
            with open('data.json', 'w') as jsonfile:
             json.dump(patient_data, jsonfile,indent=2,ensure_ascii=False)

             print(json.dumps(patient_data, indent=2, ensure_ascii=False))
            
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
     smtp_server.login('desarrollo@fundaciontrauma.org.ar', 'Desarrollo352')
     smtp_server.sendmail(sender_email, receiver_email, email_message.as_string())
