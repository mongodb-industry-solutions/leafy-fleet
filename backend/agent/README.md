

1. Primero tomamos el input del usuario
2. Pasamos el input por una IA con conocimiento de varias herramientas -> generate_chain_of_thought - posiblemente cambiar nombre a > reason_appropiate_tool
3. Guardamos la respuesta en la base de datos, vectorizada
4. ejecutamos la herramienta que indico la IA
5. pasamos el resultado de la herramienta mas un contexto mas el input a otra segunda IA para que genere una respuesta


Primero se crea el agente, si no existe en la base de datos se guarda el agente de config.json en agent_profiles

Se va a modificar generate_chain_of_thought para hacer la primera pregunta 


en que trabajar manana.

En agent_profiles.py, actualmente se precarga el perfil del agente que se va a usar, haz que se pueda mandar desde afuera para poder tener IAS con diferentes personalidades


Ahorita estoy en fuel_consumption_tool, antes de ir a la tool se debe de guardar historical recommendarions y embeddear eso para futura referencia, despues ir a la tool seleccionada



1. Get embedding
2. Vector search
de vector search se puede ir a la 
3. tool 
o
3. generate_chain_of_thought
de generate_chain_of_thought se va a 
4. save_embedding
5. tool



Se tiene que enviar la cantiad de coches seleccionada y de que flotilla es para saber de que coches se esta hablando
