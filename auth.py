import time
import hashlib
import requests
import jwt  # PyJWT
import json
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()


# ============================================================
# CONFIGURACIÓN: DATOS CARGADOS DESDE .env
# ============================================================

#LIGA DE LA API:
#https://app.saeko.io/api/v1/core/enrollments?include_fields=extended&include_fields=student

SERVICE_ACCOUNT = {
    "auth_url": os.environ["SAEKO_AUTH_URL"],
    "api_url": os.environ["SAEKO_API_URL"],
    "client_id": os.environ["SAEKO_CLIENT_ID"],
    "private_key_id": os.environ["SAEKO_PRIVATE_KEY_ID"],
    "private_key": os.environ["SAEKO_PRIVATE_KEY"].replace("\\n", "\n"),
    "expires_at": os.environ["SAEKO_EXPIRES_AT"],
}

# Usuario al que se delega autoridad (debe existir en Saeko)
USER_EMAIL = os.environ["SAEKO_USER_EMAIL"]


def build_jwt(service_account: dict, user_email: str) -> str:
    """
    Construye y firma el JWT con RS256 siguiendo la documentación de Saeko.
    payload:
      iss: client_id
      sub: user_email
      scope: "admin"
      iat: timestamp_epoch
      jti: MD5(f"{private_key_id}:{timestamp_epoch}")
    """
    client_id = service_account["client_id"]
    private_key_id = service_account["private_key_id"]
    private_key = service_account["private_key"]

    timestamp_epoch = int(time.time())
    jti_raw = f"{private_key_id}:{timestamp_epoch}".encode("utf-8")
    jti = hashlib.md5(jti_raw).hexdigest()

    payload = {
        "iss": client_id,
        "sub": user_email,
        "scope": "admin",
        "iat": timestamp_epoch,
        "jti": jti,
    }

    token = jwt.encode(
        payload,
        private_key,
        algorithm="RS256",
        headers={
            "typ": "JWT",
            "alg": "RS256",
        },
    )

    # En PyJWT>=2, jwt.encode devuelve str; en versiones viejas, bytes.
    if isinstance(token, bytes):
        token = token.decode("utf-8")

    return token


def get_access_token(service_account: dict, user_email: str) -> dict:
    """
    Pide el access_token al auth server de Saeko usando el JWT.
    Devuelve el JSON completo de la respuesta (incluye access_token, refresh_token, etc.).
    """
    auth_url = service_account["auth_url"]
    assertion_jwt = build_jwt(service_account, user_email)

    body = {
        "grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer",
        "assertion": assertion_jwt,
    }

    headers = {
        "Content-Type": "application/json",
    }

    resp = requests.post(auth_url, json=body, headers=headers, timeout=30)

    if resp.status_code != 200:
        raise RuntimeError(
            f"Error al obtener access_token: {resp.status_code} {resp.text}"
        )

    return resp.json()


def refresh_access_token(service_account: dict, refresh_token: str) -> dict:
    """
    Refresca el access_token usando el refresh_token, según la doc de Saeko:
    POST /oauth/token
    {
      "refresh_token": "...",
      "scope": "admin",
      "grant_type": "refresh_token"
    }
    """
    auth_url = service_account["auth_url"]

    body = {
        "refresh_token": refresh_token,
        "scope": "admin",
        "grant_type": "refresh_token",
    }

    headers = {
        "Content-Type": "application/json",
    }

    resp = requests.post(auth_url, json=body, headers=headers, timeout=30)

    if resp.status_code != 200:
        raise RuntimeError(
            f"Error al refrescar access_token: {resp.status_code} {resp.text}"
        )

    return resp.json()


def list_schools(service_account: dict, access_token: str) -> dict:
    """
    Llama al endpoint GET /api/v1/core/schools para validar que el token funciona.
    """
    api_url = service_account["api_url"].rstrip("/")
    url = f"{api_url}/api/v1/core/schools"

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json; charset=utf-8",
    }

    resp = requests.get(url, headers=headers, timeout=30)

    if resp.status_code != 200:
        raise RuntimeError(
            f"Error al listar schools: {resp.status_code} {resp.text}"
        )

    return resp.json()


def save_tokens_to_file(token_data: dict, filename: str = "tokens.txt"):
    """
    Guarda los tokens de autenticación en un archivo de texto.
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    with open(filename, "w", encoding="utf-8") as f:
        f.write(f"=== TOKENS DE AUTENTICACIÓN SAEKO ===\n")
        f.write(f"Generado: {timestamp}\n")
        f.write(f"{'='*50}\n\n")
        
        f.write(f"ACCESS TOKEN:\n{token_data.get('access_token', 'N/A')}\n\n")
        
        if token_data.get('refresh_token'):
            f.write(f"REFRESH TOKEN:\n{token_data.get('refresh_token')}\n\n")
        
        f.write(f"TOKEN TYPE: {token_data.get('token_type', 'N/A')}\n")
        f.write(f"EXPIRES IN: {token_data.get('expires_in', 'N/A')} segundos\n")
        f.write(f"SCOPE: {token_data.get('scope', 'N/A')}\n\n")
        
        f.write(f"{'='*50}\n")
        f.write(f"Datos completos (JSON):\n")
        f.write(json.dumps(token_data, indent=2, ensure_ascii=False))
    
    print(f"\n✓ Tokens guardados en: {filename}")


def main():
    # 1) Obtener access_token inicial
    print("Obteniendo access_token inicial...")
    token_data = get_access_token(SERVICE_ACCOUNT, USER_EMAIL)
    access_token = token_data["access_token"]
    refresh_token = token_data.get("refresh_token")
    expires_in = token_data.get("expires_in")

    print(f"access_token: {access_token[:40]}...")  # solo para debug
    print(f"expires_in: {expires_in} segundos")
    if refresh_token:
        print(f"refresh_token: {refresh_token[:40]}...")

    # Guardar tokens en archivo
    save_tokens_to_file(token_data)

    # 2) Probar una llamada a la API de Saeko
    print("\nLlamando a /api/v1/core/schools ...")
    schools = list_schools(SERVICE_ACCOUNT, access_token)
    print("Respuesta de /schools:")
    print(schools)

    # 3) Ejemplo opcional de refresh del token (solo si tienes refresh_token)
    if refresh_token:
        print("\nRefrescando el token...")
        refreshed = refresh_access_token(SERVICE_ACCOUNT, refresh_token)
        new_access_token = refreshed["access_token"]
        print(f"Nuevo access_token: {new_access_token[:40]}...")
        
        # Guardar tokens refrescados
        save_tokens_to_file(refreshed, "tokens_refreshed.txt")


if __name__ == "__main__":
    main()
