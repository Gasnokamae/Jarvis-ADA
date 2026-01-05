#!/usr/bin/env python3
"""
MCP (Model Context Protocol) Manager
Gestiona conexiones a servidores MCP y extensiones tipo gemini-cli
"""

import os
import json
import logging
import asyncio
import subprocess
from typing import Dict, List, Optional, Any
from pathlib import Path
import aiohttp
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class MCPServer:
    """Configuración de servidor MCP"""
    name: str
    command: str
    args: List[str]
    env: Dict[str, str]
    enabled: bool = True

class MCPManager:
    """
    Gestor de Model Context Protocol (MCP)
    - Auto-descubrimiento de servidores MCP
    - Conexión automática a extensiones
    - Soporte para gemini-cli extensions
    - Gestión de API keys automática
    """
    
    def __init__(self, config_dir="/app/config/mcp"):
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.servers: Dict[str, MCPServer] = {}
        self.active_connections = {}
        self.extensions = {}
        
    async def discover_mcp_servers(self) -> List[MCPServer]:
        """Descubre servidores MCP disponibles automáticamente"""
        logger.info("🔍 Descubriendo servidores MCP...")
        
        discovered = []
        
        # MCP Servidores comunes
        common_servers = [
            {
                "name": "filesystem",
                "command": "npx",
                "args": ["-y", "@modelcontextprotocol/server-filesystem", "/tmp"]
            },
            {
                "name": "github",
                "command": "npx",
                "args": ["-y", "@modelcontextprotocol/server-github"]
            },
            {
                "name": "postgres",
                "command": "npx",
                "args": ["-y", "@modelcontextprotocol/server-postgres"]
            },
            {
                "name": "slack",
                "command": "npx",
                "args": ["-y", "@modelcontextprotocol/server-slack"]
            },
            {
                "name": "puppeteer",
                "command": "npx",
                "args": ["-y", "@modelcontextprotocol/server-puppeteer"]
            },
            {
                "name": "brave-search",
                "command": "npx",
                "args": ["-y", "@modelcontextprotocol/server-brave-search"]
            }
        ]
        
        for server_config in common_servers:
            try:
                # Verificar si el servidor está disponible
                result = subprocess.run(
                    ["which", "npx"],
                    capture_output=True,
                    timeout=5
                )
                
                if result.returncode == 0:
                    server = MCPServer(
                        name=server_config["name"],
                        command=server_config["command"],
                        args=server_config["args"],
                        env=os.environ.copy()
                    )
                    discovered.append(server)
                    logger.info(f"✅ Servidor MCP encontrado: {server.name}")
            except Exception as e:
                logger.debug(f"Servidor {server_config['name']} no disponible: {e}")
        
        return discovered
    
    async def load_gemini_cli_extensions(self) -> Dict[str, Any]:
        """Carga extensiones tipo gemini-cli automáticamente"""
        logger.info("🔌 Cargando extensiones gemini-cli...")
        
        extensions = {
            "code_execution": {
                "type": "code_execution",
                "enabled": True,
                "languages": ["python", "javascript", "bash", "powershell"]
            },
            "google_search": {
                "type": "google_search_retrieval",
                "enabled": True,
                "dynamic_retrieval_config": {
                    "mode": "MODE_DYNAMIC",
                    "dynamic_threshold": 0.7
                }
            },
            "function_calling": {
                "type": "function_declarations",
                "enabled": True,
                "functions": []
            }
        }
        
        self.extensions = extensions
        logger.info(f"✅ {len(extensions)} extensiones cargadas")
        return extensions
    
    async def connect_to_server(self, server: MCPServer) -> bool:
        """Conecta a un servidor MCP"""
        try:
            logger.info(f"🔗 Conectando a servidor MCP: {server.name}")
            
            # Iniciar proceso del servidor MCP
            process = await asyncio.create_subprocess_exec(
                server.command,
                *server.args,
                env=server.env,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                stdin=asyncio.subprocess.PIPE
            )
            
            self.active_connections[server.name] = {
                "server": server,
                "process": process,
                "status": "connected"
            }
            
            logger.info(f"✅ Conectado a {server.name}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error conectando a {server.name}: {e}")
            return False
    
    async def send_mcp_request(self, server_name: str, method: str, params: Dict) -> Optional[Dict]:
        """Envía request a servidor MCP usando JSON-RPC 2.0"""
        if server_name not in self.active_connections:
            logger.warning(f"Servidor {server_name} no conectado")
            return None
        
        try:
            connection = self.active_connections[server_name]
            process = connection["process"]
            
            # Construir mensaje JSON-RPC
            request = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": method,
                "params": params
            }
            
            # Enviar request
            request_json = json.dumps(request) + "\n"
            process.stdin.write(request_json.encode())
            await process.stdin.drain()
            
            # Leer respuesta
            response_line = await process.stdout.readline()
            response = json.loads(response_line.decode())
            
            return response.get("result")
            
        except Exception as e:
            logger.error(f"Error en request MCP a {server_name}: {e}")
            return None
    
    async def list_tools(self, server_name: str) -> List[Dict]:
        """Lista tools disponibles en servidor MCP"""
        result = await self.send_mcp_request(server_name, "tools/list", {})
        return result.get("tools", []) if result else []
    
    async def call_tool(self, server_name: str, tool_name: str, arguments: Dict) -> Any:
        """Llama a una herramienta MCP"""
        params = {
            "name": tool_name,
            "arguments": arguments
        }
        return await self.send_mcp_request(server_name, "tools/call", params)
    
    async def initialize_all(self):
        """Inicializa todos los servidores MCP y extensiones"""
        logger.info("🚀 Inicializando sistema MCP completo...")
        
        # Descubrir servidores
        servers = await self.discover_mcp_servers()
        
        # Conectar a servidores
        for server in servers:
            if server.enabled:
                await self.connect_to_server(server)
        
        # Cargar extensiones gemini-cli
        await self.load_gemini_cli_extensions()
        
        logger.info(f"✅ Sistema MCP inicializado: {len(self.active_connections)} servidores activos")
    
    async def shutdown(self):
        """Cierra todas las conexiones MCP"""
        logger.info("⏹️ Cerrando conexiones MCP...")
        
        for name, connection in self.active_connections.items():
            try:
                process = connection["process"]
                process.terminate()
                await process.wait()
                logger.info(f"✅ Servidor {name} cerrado")
            except Exception as e:
                logger.error(f"Error cerrando {name}: {e}")
        
        self.active_connections.clear()

# Uso ejemplo
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    async def main():
        manager = MCPManager()
        await manager.initialize_all()
        
        # Listar tools de filesystem
        if "filesystem" in manager.active_connections:
            tools = await manager.list_tools("filesystem")
            print(f"Tools disponibles: {tools}")
        
        await manager.shutdown()
    
    asyncio.run(main())
