#!/usr/bin/env python3
"""
API Key Manager - Gestión Automática de Claves API
Jarvis crea, obtiene y gestiona API keys automáticamente
"""

import os
import json
import logging
import asyncio
import aiohttp
from typing import Dict, Optional, Any
from pathlib import Path
from cryptography.fernet import Fernet
import webbrowser
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

logger = logging.getLogger(__name__)

class APIKeyManager:
    """
    Gestor automático de API keys
    - Crea API keys automáticamente navegando por las páginas
    - Almacena de forma segura con encriptación
    - Solicita al usuario mediante voz cuando es necesario
    """
    
    def __init__(self, config_dir="/app/config/api_keys"):
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.keys_file = self.config_dir / "keys.encrypted"
        self.key = self._get_or_create_encryption_key()
        self.cipher = Fernet(self.key)
        self.api_keys = self._load_keys()
    
    def _get_or_create_encryption_key(self) -> bytes:
        """Obtiene o crea clave de encriptación"""
        key_file = self.config_dir / ".key"
        if key_file.exists():
            return key_file.read_bytes()
        else:
            key = Fernet.generate_key()
            key_file.write_bytes(key)
            key_file.chmod(0o600)
            return key
    
    def _load_keys(self) -> Dict[str, str]:
        """Carga API keys encriptadas"""
        if not self.keys_file.exists():
            return {}
        
        try:
            encrypted_data = self.keys_file.read_bytes()
            decrypted_data = self.cipher.decrypt(encrypted_data)
            return json.loads(decrypted_data.decode())
        except Exception as e:
            logger.error(f"Error cargando keys: {e}")
            return {}
    
    def _save_keys(self):
        """Guarda API keys encriptadas"""
        data = json.dumps(self.api_keys).encode()
        encrypted_data = self.cipher.encrypt(data)
        self.keys_file.write_bytes(encrypted_data)
        self.keys_file.chmod(0o600)
    
    async def request_api_key_from_user(self, service: str, instructions: str) -> Optional[str]:
        """Solicita API key al usuario mediante voz"""
        logger.info(f"🗣️ Solicitando API key de {service} al usuario...")
        
        # Aquí se integraría con el módulo de voz de Jarvis
        message = f"Necesito una clave API de {service}. {instructions}"
        logger.info(f"Mensaje al usuario: {message}")
        
        # Por ahora retorna None, se integraría con el sistema de voz
        return None
    
    async def auto_create_gemini_key(self) -> Optional[str]:
        """Crea automáticamente API key de Google Gemini"""
        try:
            logger.info("🔑 Creando API key de Gemini automáticamente...")
            
            # URL para crear API key
            url = "https://aistudio.google.com/app/apikey"
            
            logger.info(f"Abriendo navegador en: {url}")
            logger.info("El usuario debe iniciar sesión y crear la key")
            
            # Abrir en navegador para que usuario autorice
            webbrowser.open(url)
            
            # Solicitar al usuario que pegue la key
            api_key = await self.request_api_key_from_user(
                "Google Gemini",
                f"Por favor, crea una API key en {url} y dímela"
            )
            
            if api_key:
                self.api_keys["gemini"] = api_key
                self._save_keys()
                logger.info("✅ API key de Gemini guardada")
                return api_key
            
        except Exception as e:
            logger.error(f"Error creando key de Gemini: {e}")
        
        return None
    
    async def auto_create_openai_key(self) -> Optional[str]:
        """Ayuda a crear API key de OpenAI"""
        try:
            logger.info("🔑 Ayudando a crear API key de OpenAI...")
            url = "https://platform.openai.com/api-keys"
            webbrowser.open(url)
            
            api_key = await self.request_api_key_from_user(
                "OpenAI",
                f"Crea una API key en {url} y dímela"
            )
            
            if api_key:
                self.api_keys["openai"] = api_key
                self._save_keys()
                return api_key
                
        except Exception as e:
            logger.error(f"Error con key de OpenAI: {e}")
        
        return None
    
    async def get_or_create_key(self, service: str) -> Optional[str]:
        """Obtiene key existente o crea una nueva automáticamente"""
        service = service.lower()
        
        # Si ya existe, retornarla
        if service in self.api_keys:
            logger.info(f"✅ API key de {service} encontrada")
            return self.api_keys[service]
        
        logger.info(f"⚠️ No se encontró API key de {service}, creando...")
        
        # Crear según el servicio
        if service == "gemini":
            return await self.auto_create_gemini_key()
        elif service == "openai":
            return await self.auto_create_openai_key()
        elif service == "anthropic":
            url = "https://console.anthropic.com/settings/keys"
            webbrowser.open(url)
            return await self.request_api_key_from_user("Anthropic", f"Crea key en {url}")
        
        return None
    
    def get_key(self, service: str) -> Optional[str]:
        """Obtiene key de forma síncrona"""
        return self.api_keys.get(service.lower())
    
    def set_key(self, service: str, api_key: str):
        """Establece una API key manualmente"""
        self.api_keys[service.lower()] = api_key
        self._save_keys()
        logger.info(f"✅ API key de {service} guardada")
    
    def list_keys(self) -> Dict[str, str]:
        """Lista servicios con API keys (oculta valores)"""
        return {k: f"{v[:8]}..." for k, v in self.api_keys.items()}

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    async def main():
        manager = APIKeyManager()
        
        # Ejemplo: obtener o crear key de Gemini
        key = await manager.get_or_create_key("gemini")
        print(f"Gemini key: {key}")
        
        # Listar keys
        print("Keys disponibles:", manager.list_keys())
    
    asyncio.run(main())
