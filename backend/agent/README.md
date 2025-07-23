

1. Primero tomamos el input del usuario
2. Pasamos el input por una IA con conocimiento de varias herramientas -> generate_chain_of_thought - posiblemente cambiar nombre a > reason_appropiate_tool
3. Guardamos la respuesta en la base de datos, vectorizada
4. ejecutamos la herramienta que indico la IA
5. pasamos el resultado de la herramienta mas un contexto mas el input a otra segunda IA para que genere una respuesta


Primero se crea el agente, si no existe en la base de datos se guarda el agente de config.json en agent_profiles

Se va a modificar generate_chain_of_thought para hacer la primera pregunta 