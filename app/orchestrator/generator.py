import os
import yaml
from typing import List
from datetime import datetime
from app.orchestrator.slots import ConversationSlots
from app.orchestrator.llm.factory import get_llm_client

class PRDGenerator:
    """Generates PRDs and updates API contracts based on conversation slots"""
    
    def __init__(self):
        self.llm_client = get_llm_client()
    
    async def generate_artifacts(self, conversation: ConversationSlots) -> List[str]:
        """Generate PRD and update contracts based on conversation slots"""
        artifacts = []
        
        prd_path = await self._generate_prd(conversation)
        artifacts.append(prd_path)
        
        contract_path = await self._update_contracts(conversation)
        artifacts.append(contract_path)
        
        return artifacts
    
    async def _generate_prd(self, conversation: ConversationSlots) -> str:
        """Generate a PRD markdown file"""
        template_path = "docs/templates/PRD_TEMPLATE.md"
        if os.path.exists(template_path):
            with open(template_path, 'r') as f:
                template = f.read()
        else:
            template = self._get_default_prd_template()
        
        prompt = f"""
        Generate a comprehensive Product Requirements Document (PRD) based on the following project information:
        
        Project Name: {conversation.project_name}
        Description: {conversation.project_description}
        Target Users: {conversation.target_users}
        Key Features: {', '.join(conversation.key_features or [])}
        Technical Requirements: {conversation.technical_requirements or 'None specified'}
        Success Metrics: {conversation.success_metrics or 'None specified'}
        Timeline: {conversation.timeline or 'Not specified'}
        Budget Constraints: {conversation.budget_constraints or 'None specified'}
        Integration Requirements: {', '.join(conversation.integration_requirements or [])}
        Data Entities: {', '.join(conversation.data_entities or [])}
        
        Use this template structure:
        {template}
        
        Return only the filled PRD content in markdown format.
        """
        
        prd_content = await self.llm_client.generate_json_response(
            prompt, 
            {"type": "object", "properties": {"prd_content": {"type": "string"}}}
        )
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        feature_id = f"FT-{timestamp}"
        prd_filename = f"{feature_id}.md"
        prd_path = f"docs/prds/{prd_filename}"
        
        os.makedirs("docs/prds", exist_ok=True)
        with open(prd_path, 'w') as f:
            f.write(prd_content.get("prd_content", ""))
        
        return prd_path
    
    async def _update_contracts(self, conversation: ConversationSlots) -> str:
        """Update API contracts based on data entities"""
        contract_path = "contracts/api.yaml"
        
        if os.path.exists(contract_path):
            with open(contract_path, 'r') as f:
                contract = yaml.safe_load(f)
        else:
            contract = self._get_base_contract()
        
        if conversation.data_entities:
            for entity in conversation.data_entities:
                entity_lower = entity.lower()
                entity_path = f"/v1/{entity_lower}s"
                
                if "paths" not in contract:
                    contract["paths"] = {}
                
                contract["paths"][entity_path] = {
                    "get": {
                        "summary": f"List {entity_lower}s",
                        "responses": {
                            "200": {
                                "description": f"List of {entity_lower}s",
                                "content": {
                                    "application/json": {
                                        "schema": {
                                            "type": "array",
                                            "items": {"$ref": f"#/components/schemas/{entity}"}
                                        }
                                    }
                                }
                            }
                        }
                    },
                    "post": {
                        "summary": f"Create {entity_lower}",
                        "requestBody": {
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": f"#/components/schemas/{entity}Create"}
                                }
                            }
                        },
                        "responses": {
                            "201": {
                                "description": f"{entity} created",
                                "content": {
                                    "application/json": {
                                        "schema": {"$ref": f"#/components/schemas/{entity}"}
                                    }
                                }
                            }
                        }
                    }
                }
                
                contract["paths"][f"{entity_path}/{{id}}"] = {
                    "get": {
                        "summary": f"Get {entity_lower} by ID",
                        "parameters": [
                            {
                                "name": "id",
                                "in": "path",
                                "required": True,
                                "schema": {"type": "string", "format": "uuid"}
                            }
                        ],
                        "responses": {
                            "200": {
                                "description": f"{entity} details",
                                "content": {
                                    "application/json": {
                                        "schema": {"$ref": f"#/components/schemas/{entity}"}
                                    }
                                }
                            }
                        }
                    },
                    "put": {
                        "summary": f"Update {entity_lower}",
                        "parameters": [
                            {
                                "name": "id",
                                "in": "path",
                                "required": True,
                                "schema": {"type": "string", "format": "uuid"}
                            }
                        ],
                        "requestBody": {
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": f"#/components/schemas/{entity}Update"}
                                }
                            }
                        },
                        "responses": {
                            "200": {
                                "description": f"{entity} updated",
                                "content": {
                                    "application/json": {
                                        "schema": {"$ref": f"#/components/schemas/{entity}"}
                                    }
                                }
                            }
                        }
                    },
                    "delete": {
                        "summary": f"Delete {entity_lower}",
                        "parameters": [
                            {
                                "name": "id",
                                "in": "path",
                                "required": True,
                                "schema": {"type": "string", "format": "uuid"}
                            }
                        ],
                        "responses": {
                            "204": {"description": f"{entity} deleted"}
                        }
                    }
                }
        
        os.makedirs("contracts", exist_ok=True)
        with open(contract_path, 'w') as f:
            yaml.dump(contract, f, default_flow_style=False, sort_keys=False)
        
        return contract_path
    
    def _get_default_prd_template(self) -> str:
        """Get default PRD template"""
        return """# Product Requirements Document: {project_name}

{project_description}

{target_users}

{key_features}

{technical_requirements}

{success_metrics}

{timeline}

{budget_constraints}

{integration_requirements}

{data_entities}
"""
    
    def _get_base_contract(self) -> dict:
        """Get base OpenAPI contract"""
        return {
            "openapi": "3.0.0",
            "info": {
                "title": "Agentic Dev Team API",
                "version": "1.0.0",
                "description": "Multi-agent web development system API"
            },
            "paths": {
                "/v1/drafts": {
                    "get": {
                        "summary": "List drafts",
                        "responses": {
                            "200": {
                                "description": "List of drafts",
                                "content": {
                                    "application/json": {
                                        "schema": {
                                            "type": "array",
                                            "items": {"$ref": "#/components/schemas/Draft"}
                                        }
                                    }
                                }
                            }
                        }
                    },
                    "post": {
                        "summary": "Create draft",
                        "requestBody": {
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/DraftCreate"}
                                }
                            }
                        },
                        "responses": {
                            "201": {
                                "description": "Draft created",
                                "content": {
                                    "application/json": {
                                        "schema": {"$ref": "#/components/schemas/Draft"}
                                    }
                                }
                            }
                        }
                    }
                },
                "/v1/drafts/{id}": {
                    "get": {
                        "summary": "Get draft by ID",
                        "parameters": [
                            {
                                "name": "id",
                                "in": "path",
                                "required": True,
                                "schema": {"type": "string", "format": "uuid"}
                            }
                        ],
                        "responses": {
                            "200": {
                                "description": "Draft details",
                                "content": {
                                    "application/json": {
                                        "schema": {"$ref": "#/components/schemas/Draft"}
                                    }
                                }
                            }
                        }
                    },
                    "put": {
                        "summary": "Update draft",
                        "parameters": [
                            {
                                "name": "id",
                                "in": "path",
                                "required": True,
                                "schema": {"type": "string", "format": "uuid"}
                            }
                        ],
                        "requestBody": {
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/DraftUpdate"}
                                }
                            }
                        },
                        "responses": {
                            "200": {
                                "description": "Draft updated",
                                "content": {
                                    "application/json": {
                                        "schema": {"$ref": "#/components/schemas/Draft"}
                                    }
                                }
                            }
                        }
                    },
                    "delete": {
                        "summary": "Delete draft",
                        "parameters": [
                            {
                                "name": "id",
                                "in": "path",
                                "required": True,
                                "schema": {"type": "string", "format": "uuid"}
                            }
                        ],
                        "responses": {
                            "204": {"description": "Draft deleted"}
                        }
                    }
                }
            },
            "components": {
                "schemas": {
                    "Draft": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "string", "format": "uuid"},
                            "owner": {"type": "string"},
                            "payload": {"type": "object"},
                            "updated_at": {"type": "string", "format": "date-time"}
                        }
                    },
                    "DraftCreate": {
                        "type": "object",
                        "properties": {
                            "owner": {"type": "string"},
                            "payload": {"type": "object"}
                        },
                        "required": ["owner", "payload"]
                    },
                    "DraftUpdate": {
                        "type": "object",
                        "properties": {
                            "owner": {"type": "string"},
                            "payload": {"type": "object"}
                        }
                    }
                }
            }
        }
