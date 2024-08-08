from typing import Dict, Any
from data.database import get_db_connection


## Capital Humano's main function
def capitalHumanoFunc(responseId: str, queryResult: Dict[str, Any]):
    intent_name = queryResult.get('intent', {}).get('displayName', '')
    if intent_name == 'Inicio-Chat':
        return handler_InicioChat(responseId)
    
    

def handler_InicioChat(responseId: str):
    ## Get information from dialogflow to check if the responseId is presented in our database
    ## if responseId is presented then proceed to "inicio_nombre event response" 
    ## if not presented "name_notrelated"
    
    
    ## Once we have the database table create we can start fetching information from this one
    try:
        with get_db_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM tabla_responsesId WHERE response_id = %s", (responseId,))
                result = cursor.fetchone()
        
                if result:
                    customer_name = result[0]
            
                    return {
                        "followupEventInput": {
                            "name": "inicio_nombre",
                            "parameters": {
                                "nombre": customer_name,
                                "parameter-name-2": "no parameter value"
                            },
                            "languageCode": "en-US" 
                        }
                    }
                else:
                    return {
                        "followupEventInput": {
                            "name": "name_notrelated",
                            "parameters": {
                            },
                            "languageCode": "en-US"
                        }
                    }
            
    except Exception as error:
        return "En estos momentos estamos teniendo un inconveniente en nuestro bot, por favor contactar mas tarde"
    
    finally: 
        # Close connection to database
        cursor.close()
        connection.close()