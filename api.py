import requests
from auth import SERVICE_ACCOUNT, USER_EMAIL, get_access_token


def obtener_access_token(service_account: dict) -> dict:
    """
    Obtiene un access_token usando el service account, según la doc de Saeko:
    POST /oauth/token
    {
      "client_id": "...",
      "client_secret": "...",
      "scope": "admin",
      "grant_type": "client_credentials"
    }
    """
    auth_url = service_account["auth_url"]

    body = {
        "client_id": service_account["client_id"],
        "client_secret": service_account["client_secret"],
        "scope": "admin",
        "grant_type": "client_credentials",
    }

    response = requests.post(auth_url, json=body)
    response.raise_for_status()
    return response.json()

url = "https://app.saeko.io/api/v1"

#GET /api/v1/core/schools/:school_id/terms
def obtener_term(school_id: str, access_token: str) -> dict:
    """
    Obtiene los términos de una escuela específica usando el access_token.
    GET /api/v1/core/schools/:school_id/terms
    """
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    response = requests.get(f"{url}/core/schools/{school_id}/terms", headers=headers)
    response.raise_for_status()
    return response.json()


def obtener_todos_los_terms(access_token: str, school_id: str = None) -> dict:
    """
    Obtiene los términos (terms).
    - Si se pasa school_id: GET /api/v1/core/schools/:school_id/terms
    - Si no se pasa school_id: GET /api/v1/core/terms (retorna un número limitado de registros)

    Parámetros opcionales:
        school_id: ID de la escuela. Filtra terms de esa escuela específica.
    """
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    if school_id:
        response = requests.get(f"{url}/core/schools/{school_id}/terms", headers=headers)
    else:
        response = requests.get(f"{url}/core/terms", headers=headers)
    response.raise_for_status()
    return response.json()

#DEF QUE OBTIENE LOS DATOS DE LA SCHOOL QUE RECIBA COMO PARAMETRO ID:
def obtener_datos_school(school_id: str, access_token: str) -> dict:
    """
    Obtiene los datos de una escuela específica usando el access_token.
    GET /api/v1/core/schools/:school_id
    """
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    response = requests.get(f"{url}/core/schools/{school_id}", headers=headers)
    response.raise_for_status()
    return response.json()

if __name__ == "__main__":
    token_data = get_access_token(SERVICE_ACCOUNT, USER_EMAIL)
    access_token = token_data["access_token"]
    print("Access token obtenido correctamente.\n")

    # Obtener todos los terms
    terms = obtener_todos_los_terms(access_token, school_id="320")
    print(f"=== TODOS LOS TERMS ({terms.get('meta', {}).get('total', '?')} total) ===\n")
    for term in terms.get("terms", []):
        print(f"ID: {term['id']} | {term['name']} | School: {term['school_id']} | "
              f"{term['begins_at']} → {term['ends_at']} | Actual: {term['is_current']}")
        respuesta = obtener_datos_school(term['school_id'], access_token)
        print(f"{respuesta['school']['id']} {respuesta['school']['name']}\n")

