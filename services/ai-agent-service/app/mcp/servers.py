"""MCP Server Implementation — standardized tool access for agents."""
import json
from typing import Any, Callable
from dataclasses import dataclass, field
from datetime import datetime

@dataclass
class ToolSchema:
    name: str
    description: str
    parameters: dict
    returns: dict

@dataclass
class MCPServer:
    name: str
    description: str
    version: str = "1.0.0"
    tools: dict[str, Callable] = field(default_factory=dict)
    schemas: dict[str, ToolSchema] = field(default_factory=dict)

    def register_tool(self, name, description, handler, parameters, returns):
        self.tools[name] = handler
        self.schemas[name] = ToolSchema(name=name, description=description, parameters=parameters, returns=returns)

    def list_tools(self):
        return [{"name": s.name, "description": s.description, "parameters": s.parameters, "returns": s.returns} for s in self.schemas.values()]

    async def invoke(self, tool_name, arguments):
        if tool_name not in self.tools:
            return {"error": f"Tool \'{tool_name}\' not found"}
        try:
            result = self.tools[tool_name](**arguments)
            return {"status": "success", "tool": tool_name, "result": result, "timestamp": datetime.utcnow().isoformat()}
        except Exception as e:
            return {"status": "error", "tool": tool_name, "error": str(e)}

    def to_manifest(self):
        return {"name": self.name, "description": self.description, "version": self.version, "tools": self.list_tools()}

def create_patient_data_server(url):
    import httpx
    server = MCPServer(name="patient-data", description="Patient demographics access")
    def get_demo(patient_id):
        r = httpx.get(f"{url}/api/v1/patients/{patient_id}", timeout=10)
        r.raise_for_status()
        return r.json()
    server.register_tool("get_demographics", "Fetch patient demographics", get_demo,
        {"type":"object","properties":{"patient_id":{"type":"string"}}}, {"type":"object"})
    return server

def create_lab_data_server(url):
    import httpx
    server = MCPServer(name="lab-data", description="Patient lab results")
    def get_labs(patient_id, limit=10):
        r = httpx.get(f"{url}/api/v1/labs/{patient_id}", params={"limit":limit}, timeout=10)
        r.raise_for_status()
        return r.json()
    server.register_tool("get_labs", "Fetch lab results", get_labs,
        {"type":"object","properties":{"patient_id":{"type":"string"},"limit":{"type":"integer"}}}, {"type":"array"})
    return server

def create_guidelines_server():
    from app.rag.retrieval import retrieve_guidelines
    server = MCPServer(name="clinical-guidelines", description="RAG clinical guideline search")
    def search(query, condition=None, top_k=5):
        results = retrieve_guidelines(query=query, condition_filter=condition, top_k=top_k)
        return [{"content": r.content, "score": r.score, "metadata": r.metadata} for r in results]
    server.register_tool("search_guidelines", "Semantic search of guidelines", search,
        {"type":"object","properties":{"query":{"type":"string"},"condition":{"type":"string"}}}, {"type":"array"})
    return server

class MCPRegistry:
    def __init__(self):
        self._servers = {}
    def register(self, server):
        self._servers[server.name] = server
    def list_servers(self):
        return [s.to_manifest() for s in self._servers.values()]
    def get_server(self, name):
        return self._servers.get(name)
    def list_all_tools(self):
        tools = []
        for s in self._servers.values():
            for t in s.list_tools():
                t["server"] = s.name
                tools.append(t)
        return tools

registry = MCPRegistry()

def initialize_mcp_servers():
    from app.config import get_settings
    s = get_settings()
    registry.register(create_patient_data_server(s.patient_service_url))
    registry.register(create_lab_data_server(s.lab_service_url))
    registry.register(create_guidelines_server())
    return registry
