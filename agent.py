import os
import json

class Agent:
    def __init__(self):
        self.setup_tools()
        self.messages = [
            {
                "role": "system",
                "content": "Eres un asistente útil que habla español y eres muy conciso con tus respuestas"
            }
        ]

    def setup_tools(self):
        # Formato estándar de chat.completions (compatible con todos los proveedores)
        self.tools = [
            {
                "type": "function",
                "function": {
                    "name": "list_files_in_dir",
                    "description": "Lista los archivos que existen en un directorio dado",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "directory": {
                                "type": "string",
                                "description": "Directorio a listar. Por defecto el directorio actual"
                            }
                        },
                        "required": []
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "read_file",
                    "description": "Lee el contenido de un archivo en la ruta especificada",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "path": {
                                "type": "string",
                                "description": "Ruta del archivo a leer"
                            }
                        },
                        "required": ["path"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "edit_file",
                    "description": "Edita o crea un archivo. Reemplaza prev_text por new_text, o crea uno nuevo.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "path": {
                                "type": "string",
                                "description": "Ruta del archivo"
                            },
                            "prev_text": {
                                "type": "string",
                                "description": "Texto a reemplazar (vacío si es archivo nuevo)"
                            },
                            "new_text": {
                                "type": "string",
                                "description": "Texto nuevo"
                            }
                        },
                        "required": ["path", "new_text"]
                    }
                }
            }
        ]

    """
    HERRAMIENTAS DEL AGENTE
    Son las herramientas que tiene el agente para realizar la tarea del usuario
    """    
    #Permite listar todos los archivos del directorio actual
    #Problema: Dar permiso de leer todo el sistema a Gemini = Google, puede ser demasiado
    def list_files_in_dir(self, directory="."):
        print("  ⚙️  Herramienta: list_files_in_dir")
        try:
            return {"files": os.listdir(directory)}
        except Exception as e:
            return {"error": str(e)}

    #Permite leer cualquier archivo en base a una dirección
    def read_file(self, path):
        print("  ⚙️  Herramienta: read_file")
        try:
            with open(path, encoding="utf-8") as f:
                return f.read()
        except Exception as e:
            return f"Error al leer {path}: {e}"

    #Permite editar un archivo
    def edit_file(self, path, new_text, prev_text=""):
        print("  ⚙️  Herramienta: edit_file")
        try:
            existed = os.path.exists(path)
            if existed and prev_text:
                with open(path, encoding="utf-8") as f:
                    content = f.read()
                if prev_text not in content:
                    return f"Texto '{prev_text}' no encontrado en {path}"
                content = content.replace(prev_text, new_text)
            else:
                dir_name = os.path.dirname(path)
                if dir_name:
                    os.makedirs(dir_name, exist_ok=True)
                content = new_text

            with open(path, "w", encoding="utf-8") as f:
                f.write(content)

            accion = "editado" if existed and prev_text else "creado"
            return f"Archivo {path} {accion} correctamente"
        except Exception as e:
            return f"Error al editar {path}: {e}"

    def process_response(self, response):
        message = response.choices[0].message

        # Guardar el turno del asistente en el historial
        self.messages.append(message)

        if message.tool_calls:
            for tool_call in message.tool_calls:
                fn_name = tool_call.function.name
                args = json.loads(tool_call.function.arguments)

                print(f"  → Llamando a '{fn_name}' con args: {args}")

                if fn_name == "list_files_in_dir":
                    result = self.list_files_in_dir(**args)
                elif fn_name == "read_file":
                    result = self.read_file(**args)
                elif fn_name == "edit_file":
                    result = self.edit_file(**args)
                else:
                    result = f"Herramienta '{fn_name}' no reconocida"

                # Añadir resultado al historial como mensaje de herramienta
                self.messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": json.dumps({"result": result}, ensure_ascii=False)
                })

            return True  # Hubo tool calls, continúa el bucle

        else:
            # Respuesta final de texto
            reply = message.content or ""
            print(f"\nAsistente: {reply}\n")
            return False  # No hay más tool calls

