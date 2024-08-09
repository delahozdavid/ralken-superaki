from typing import Dict, Any
from data.database import get_db_connection


## Capital Humano's main function
async def capitalHumanoFunc(responseId: str, queryResult: Dict[str, Any]):
    intent_name = queryResult.get('intent', {}).get('displayName', '')
    
    async with get_db_connection() as connection:
        async with connection.cursor() as cursor:
            if intent_name == 'Inicio-Chat':
                return await handler_InicioChat(responseId, connection, cursor)
            elif intent_name == 'name_notrelated':
                return await handler_nameNotRelated(responseId, queryResult, cursor, connection)
            elif intent_name == 'Inicio-Nombre':
                return await handler_InicioNombre(responseId, queryResult, cursor, connection)
            elif intent_name == 'proceso_seleccion':
                return await handler_ProcesoSeleccion(queryResult, cursor, connection)
    
    

async def handler_InicioChat(responseId: str, cursor):
    ## Get information from dialogflow to check if the responseId is presented in our database
    ## if responseId is presented then proceed to "inicio_nombre event response" 
    ## if not presented "name_notrelated"
    ## Once we have the database table create we can start fetching information from this one
    try:
        cursor.execute("SELECT * FROM tabla_responsesId WHERE response_id = %s", (responseId,))
        result = cursor.fetchone()
        
        if result:
            customer_name = result[1]
            return {
                "followupEventInput": {
                    "name": "inicio-nombre",
                    "parameters": {
                        "nombre": customer_name,
                    },
                    "languageCode": "en-US"
                }
            }
            
        else:
            return {
                "followupEventInput": {
                    "name": "name_notrelated",
                    "parameters": {},
                    "languageCode": "en-US"
                }
            }
            
    except Exception as error:
        return {
                "followupEventInput": {
                    "name": "error-webhook",
                    "parameters": {},
                    "languageCode": "en-US"
                }
            }

async def handler_nameNotRelated(responseId: str, queryResult: Dict[str, Any], cursor, connection):
    # if responseId is not presented then proceed to create a record with the data
    #Then proceed to "inicio_nombre" event response
    try:
        nombre = queryResult['parameters']['nombre']
        cursor.execute("INSERT INTO tabla_responseId (response_id, nombre) VALUES (%s, %s)", (responseId, nombre))
        connection.commit()
        return {
            "followupEventInput": {
                "name": "inicio-nombre",
                "parameters": {
                    "nombre": nombre
                },
                "languageCode": "en-US"
            }
        }
        
    except Exception as error:
        return {
                "followupEventInput": {
                    "name": "error-webhook",
                    "parameters": {},
                    "languageCode": "en-US"
                }
            }
        


async def handler_InicioNombre(responseId: str, queryResult: Dict[str, Any], cursor):
    # Here we check if the queryResult contains the CPMexicano
    # if it contains the cp we proceed with "cm_identified" event
    # if not we proceed with cp_notidentified
    try:
        cp = queryResult['parameters']['cp_mexicano']
        cursor.execute("SELECT * FROM codigo_postal WHERE cp = %s", (cp,))
        result = cursor.fetchone()
        
        if result:
            return {
                "followupEventInput": {
                    "name": "cp_identified",
                    "parameters": {},
                    "languageCode": "en-US"
                }
            }
            
        else:
            return {
                "followupEventInput": {
                    "name": "cp_notidentified",
                    "parameters": {},
                    "languageCode": "en-US"
                }
            }
            
    except Exception as error:
        return {
                "followupEventInput": {
                    "name": "cp_identified",
                    "parameters": {
                        "error": error
                    },
                    "languageCode": "en-US"
                }
            }



async def handler_ProcesoSeleccion(queryResult: Dict[str, Any], cursor):
    # Here we check in the queryResult the parameter "codigo_postulante"
    # we query if it exists in the database, if exists we proceed to "proceso_identified"
    # if not we proceed with "proceso_notidentified"
    try:
        codigo_postulante = queryResult['parameters']['codigo_postulante']
        cursor.execute("SELECT * FROM proceso_reclutamiento_prueba WHERE codigo_reclutamiento = %s", (codigo_postulante,))
        result = cursor.fetchone()
        
        if result:
            return {
                "followupEventInput": {
                    "name": "proceso_identified",
                    "parameters": {
                        "nombre": result[1],
                        "apellido": result[2],
                        "status_reclutamiento": result[3]
                    },
                    "languageCode": "en-US"
                }
            }
            
        else:
            return {
                "followupEventInput": {
                    "name": "proceso_notidentified",
                    "parameters": {},
                    "languageCode": "en-US"
                }
            }
            
    except Exception as error:
        return {
                "followupEventInput": {
                    "name": "cp_identified",
                    "parameters": {
                        "error": error
                    },
                    "languageCode": "en-US"
                }
            }