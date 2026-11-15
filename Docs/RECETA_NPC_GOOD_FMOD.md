# Receta aprobada de NPC Good

La muestra aprobada es `work/NPC_Reacciones/NPC_Good_FMOD.wav`, de 2,125 s. Su evento editable es `event:/NPC_Video_Project_Good_Cadencia` en `Audio_FMOD/BogotaVoxel/BogotaVoxel.fspro`. La variante RetroClaro es otro evento.

- Fuente de la voz: `Video Project.m4a`. Se extrae un ciclo de voz para obtener sus armónicos y se generan vocales nuevas, sin incluir la frase original.
- Cadencia: envolvente de `Male good.wav`, suavizada con una gaussiana de 9 ms. La voz sintetizada usa 171 Hz de base y 36 Hz de variación. Los centros de las dos resonancias vocales son 620 y 1730 Hz y se desplazan durante la reacción.
- Ajustes del evento en FMOD Studio 2.03.15: filtro pasaaltos de 74 Hz, distorsión de 0,30, flanger con mezcla de 17 % y frecuencia de 1,45 Hz, filtro pasabajos de 5300 Hz y limitador a −2 dB.
- Fuente importada: `VideoNPC_Good_Cadencia.wav`. El evento reproduce la toma durante 2,125 s y pertenece al banco Desktop Master. La muestra renderizada llegó a −6,4 dBFS.
- Para reproducir el flujo: `work/prepare_npc_reaction_cadence.py` genera la fuente. `work/author_fmod_npc_reactions.js` documenta la creación y los ajustes. Con el banco ya compilado, `python work/render_npc_reactions_fmod.py Good` renderiza el evento.
