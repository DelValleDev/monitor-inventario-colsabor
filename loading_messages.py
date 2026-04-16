"""
Módulo de mensajes y saludos para la pantalla de carga.
200 mensajes relacionados con inventario, datos, negocios y humor colsaboriano.
"""

import random
from datetime import datetime

# ── Mapeo de emails a nombres personalizados ──────────────────────────────────
_PERSONAS = {
    "gerencia@colsabor.com.co": ("Gerente", "Yudy"),
    "dirtec@colsabor.com.co": ("Director Técnico", "Juan David"),
    "samuelrestrepodev@gmail.com": ("Desarrollador", "Samuel"),
}

# ── 200 mensajes indexados por categoría ─────────────────────────────────────
_MESSAGES_GENERAL = [
    # Inventario / datos
    "El inventario no miente, los humanos sí. 📊",
    "Actualizando neuronas de datos… café en proceso. ☕",
    "Sincronizando con la realidad de la bodega…",
    "Los datos no duermen, nosotros tampoco deberíamos. 🌙",
    "Consultando el oráculo de Siigo…",
    "Cada kilo de inventario cuenta. Literalmente. ⚖️",
    "Cargando 1.000.000 de registros… no, tranquilo, son menos. 😅",
    "Los números son poesía para quien sabe leerlos.",
    "Procesando datos con amor y algoritmos. 💙",
    "Chequeando que los esencias estén en su lugar…",
    "Si el inventario estuviera en orden, no necesitarías esta app. 😏",
    "Datos frescos llegando… como las esencias de Colsabor.",
    "Sincronizando con Siigo API… el cloud no descansa.",
    "Cargando tablas más rápido que un auxiliar de bodega. 🏃",
    "¿Sabías que un error de inventario puede costar millones? Por eso estamos aquí.",
    "Preparando tu dashboard personalizado… paciencia.",
    "Leyendo bytes, traduciendo a billetes. 💰",
    "Conectando con el cerebro digital de Colsabor…",
    "Menos Excel, más inteligencia. Esta es la idea. 📈",
    "Calculando diferencias de inventario… es matemática básica pero importante.",
    "Los críticos necesitan atención. Los bajos, también. Los OK son una victoria.",
    "Trayendo datos de producción… esto es vida real.",
    "Ni una sola referencia se nos escapa. Bueno, casi ninguna. 😬",
    "Inventario al día = empresa feliz = todos felices. 🎯",
    "El tiempo que tardas en revisar esto manualmente: horas. Aquí: segundos.",
    "Procesando el inventario de Colsabor con cariño y precisión. ✨",
    "Cada faltante es una oportunidad disfrazada de problema.",
    "Recopilando datos de API… los bits viajan a la velocidad de la luz.",
    "Sin datos precisos, solo hay intuición. Con datos, hay estrategia.",
    "Cargando. ¿Aprovechas para tomar agua? 💧",
    # Esencias / sabores / Colsabor
    "Colsabor: donde los sabores se convierten en negocio.",
    "Las esencias no se inventarían solas. Por eso existimos.",
    "Vainilla, fresa, arequipe… cada uno tiene su mínimo sagrado.",
    "Un sabor sin inventario es solo un sueño. Aquí lo hacemos realidad.",
    "La esencia perfecta requiere el stock perfecto.",
    "¿Cuántos kilos de limón hay en bodega? Pronto lo sabrás.",
    "Colsabor surte sabores, nosotros surtimos datos.",
    "Los aromas se olfatean, el inventario se monitorea. ¡Misión cumplida!",
    "Sin esencias, no hay producto. Sin datos, no hay control.",
    "El sabor del éxito huele a inventario bien gestionado.",
    "Conectando con la bodega… virtualmente.",
    "Cada esencia tiene una historia de producción detrás.",
    "¿Falta arequipe? Aquí te enterarás antes que nadie.",
    "Datos de sabor provenientes del servidor… ¡yum!",
    "La calidad de las esencias empieza por tener suficiente stock.",
    # Lunes
    "Lunes: el universo conspira para que el inventario esté desactualizado.",
    "Bienvenido al lunes. El café es obligatorio, el inventario también.",
    "Lunes de datos y decisiones. ¡Vamos con todo!",
    "El fin de semana pasó. El inventario no se actualizó solo. ⚠️",
    "Lunes significa: revisar qué pasó en bodega el viernes.",
    # Martes
    "Martes: el lunes ya pasó, ahora sí arranquemos en serio.",
    "Día dos de la semana, datos al 100%. ¡Dale!",
    "El martes es el lunes pero con más café y mejor humor.",
    # Miércoles
    "Mitad de semana: ¿el inventario está donde debería?",
    "Miércoles de chequeo. No dejes los críticos para el viernes.",
    "Hump day: si el stock está bien, la semana ya ganó.",
    # Jueves
    "Jueves: ya casi es viernes, pero el inventario no descansa.",
    "Día de cierre de semana y revisión de faltantes.",
    "El jueves es el mejor día para ponerse al día con los datos.",
    # Viernes
    "Viernes: revisa el inventario antes de irse de rumba. 🎉",
    "Antes de cerrar la semana, ¿están los mínimos cubiertos?",
    "Viernes de datos. El fin de semana espera, el inventario también.",
    "¡Feliz viernes! Que los stocks estén en verde. 🟢",
    "Viernes: el mejor día para no tener sorpresas el lunes.",
    # Humor / general
    "Cargando con la velocidad del sonido… bueno, casi.",
    "Analizando 0s y 1s para darte información útil. 🤓",
    "Si los datos tardaron en llegar, el café está listo mientras esperas. ☕",
    "Preparando métricas dignas de un board meeting.",
    "El sistema está pensando. Muy intensamente. 🧠",
    "Optimizando la experiencia de usuario… que eres tú. 👋",
    "No todos los héroes usan capa. Algunos usan dashboards.",
    "Los KPIs no se calculan solos. Estamos en ello.",
    "Iniciando protocolo de carga ultrarrápida… relativamente. 🚀",
    "Datos, datos, datos. El activo más valioso del siglo XXI.",
    "Conectando puntos de datos como un detective de inventario. 🔍",
    "Procesando con la dedicación de un auxiliar de bodega en su mejor día.",
    "El inventario bien gestionado es la diferencia entre ganancia y pérdida.",
    "Ningún número fue lastimado durante la carga de este dashboard. 🕊️",
    "Cargando con más amor que una abuela haciendo natilla. 🍮",
    "La bodega habla en números. Nosotros los traducimos.",
    "Sistema en línea. Nervios de acero. Datos frescos. 💪",
    "Recuerda: un crítico ignorado hoy es una crisis mañana.",
    "Cada vez que ves 'Crítico' en rojo, alguien necesita hacer un pedido ya.",
    "Tu aliado invisible: este sistema que nunca duerme. 🌙",
    "El caos del inventario tiene solución. Se llama Colsabor Monitor.",
    "En tierra de Excel, quien tiene dashboard es rey. 👑",
    "Colsabor en datos: más real que la reunión de las 8am.",
    "Integrando Siigo con amor y muchas llamadas a la API. 📡",
    "Felicidades: eres de las personas que cuida el inventario de verdad.",
    "Los datos nunca mienten. Las personas que los ingresan, a veces sí. 😅",
    "Trayendo el reporte que necesitas antes de que lo pidas.",
    "Dashboard activado. ¡Que empiece el show de los datos! 🎬",
    "Si el inventario está verde, el día va bien. Si está rojo… aquí estamos.",
    "Cargando en tiempo récord. O casi récord. Bueno, está cargando. ⏱️",
    "Inventario inteligente para empresa inteligente. Eso es Colsabor.",
    "Datos al servicio de la producción. Esa es la misión.",
]

_MESSAGES_MORNING = [
    "Buenos días y buen inventario. La combinación perfecta. ☀️",
    "Mañana de datos. El mejor maridaje con el tinto. ☕",
    "Empieza el día sabiendo exactamente cuánto hay en bodega.",
    "La mañana perfecta incluye: café, datos frescos y stock en verde.",
    "Madrugar para revisar inventario es nivel experto. Respeto. 🫡",
    "Si el stock está bien a las 7am, el día promete.",
    "Buenas, buenos días. Que el inventario te sonría. 🌞",
    "Arranque de jornada: datos cargados, mínimos chequeados.",
    "La madrugada es el momento en que el inventario muestra la verdad.",
    "Temprano es el mejor momento para detectar faltantes.",
    "Coffee first, inventory second. Juntos son imbatibles. ☕📊",
    "El amanecer trae nuevas oportunidades… y nuevos datos.",
    "Primer reporte del día: aquí viene. ¡Prepárate!",
    "Buenos días. Que hoy no haya nada en rojo. Pero si lo hay, ya sabrás.",
    "Jornada iniciada. Inventario bajo análisis. Sistema operativo.",
]

_MESSAGES_AFTERNOON = [
    "Tarde productiva, datos al día. 💼",
    "A esta hora, los faltantes del turno de mañana ya deberían resolverse.",
    "Media jornada: ¿cómo va el inventario de la tarde?",
    "Revisión de medio día. Los números no mienten.",
    "Después del almuerzo, lo mejor es revisar el stock. ¡Tradición empresarial!",
    "La siesta no existe en el inventario. Aquí todo es en tiempo real.",
    "Buenas tardes. Los datos de la mañana ya están procesados.",
    "Hora de la verdad: ¿qué tan bien quedó el inventario del turno A?",
    "Tarde de chequeos y decisiones basadas en datos.",
    "El sol de la tarde ilumina también las brechas de inventario. 🌤️",
    "Turno tarde activado. Monitor de inventario listo para servirte.",
    "¿Almorzaste bien? Bien, porque el inventario necesita atención. 😄",
    "Revisión vespertina del stock. Ritual sagrado de Colsabor.",
    "Los pedidos de la tarde se deciden con datos de la mañana.",
    "Buenas tardes. ¿Hay algo en crítico que aún no saben? Pronto lo sabrán.",
]

_MESSAGES_NIGHT = [
    "Trabajando de noche: dedicación nivel ninja. 🥷",
    "La bodega duerme pero los datos nunca lo hacen. 🌙",
    "Noche de inventario. Los más comprometidos revisan a esta hora.",
    "Mientras unos descansan, tú cuidas el stock. Eso se llama profesionalismo.",
    "Buenas noches. Que los datos de mañana sean todos verdes. 🌙🟢",
    "Nocturno modo on. Inventario bajo vigilancia.",
    "Los mejores gerentes revisan inventario antes de dormir. 💤",
    "Noche tranquila = inventario sin sorpresas. Así esperamos que sea.",
    "La madrugada empresarial tiene su propio sabor. Como las esencias.",
    "A esta hora, la bodega descansa pero tú no. Héroe silencioso. 🦸",
    "Noche de trabajo: que el inventario esté al día antes del amanecer.",
    "Trabajo nocturno con datos de día. Efficiency 100%.",
    "Las noches de revisión son inversión en amaneceres sin susto.",
    "Noctámbulo del inventario. Eso eres. Y está bien. 🌛",
    "Buenas noches. Los datos te esperaban despiertos.",
]

_MESSAGES_DEVELOPER = [
    "¡Hola, Samuel! El código que escribiste está funcionando… por ahora. 😅",
    "Samuel: tus algoritmos están procesando datos con elegancia. 🤓",
    "Desarrollador en línea. El sistema agradece tu dedicación.",
    "Samuel, la consola está limpia. Por hoy. 🧹",
    "Tu código corre más rápido que los rumores en la empresa. 🏃",
    "Stack: Streamlit + Supabase + Siigo + Café = el sueño del dev. ☕💻",
    "Hello World, Samuel. El inventario funciona gracias a ti.",
    "Samuel revisando su propio sistema: el nivel más meta de la programación.",
    "CI/CD del alma: código que funciona en producción. ¡Logro desbloqueado! 🏆",
    "El bug que encontraste ayer ya no existe. Bien jugado. 🎯",
]

_MESSAGES_DIRECTOR = [
    "Juan David, los datos técnicos están listos para tu análisis. 🔧",
    "Director Técnico en el sistema. Acceso nivel máximo activado. 🔐",
    "Juan David: el sistema que pediste está funcionando a las mil maravillas.",
    "Dirección técnica con información en tiempo real. Así se trabaja. 💡",
    "Juan David, los KPIs técnicos de hoy están en camino.",
    "El Director Técnico necesita datos precisos. Aquí los tienes.",
    "Juan David monitoreando el inventario: la ingeniería al servicio de la empresa.",
    "Datos técnicos del día para el líder técnico del día. Coherencia total.",
    "Juan David, ningún proceso escapa a tu radar. Ni al nuestro. 📡",
    "Director Técnico: activo, conectado, decidiendo con datos. 🎯",
]

_MESSAGES_GERENTE = [
    "¡Buenos días, Gerente Yudy! Los datos de hoy están listos para ti. 💼",
    "Yudy, el inventario de Colsabor bajo tu supervisión. Como siempre.",
    "Gerencia activa. El equipo y los datos también. 💪",
    "Yudy, los números de hoy reflejan el trabajo de todos. Aquí están.",
    "La gerente llegó al sistema. El inventario se pone firme. 😄",
    "Yudy: visión gerencial + datos en tiempo real = decisiones poderosas.",
    "Gerente Yudy revisando el dashboard. La empresa en buenas manos. 🙌",
    "Colsabor bajo el liderazgo de Yudy: datos, sabor y excelencia.",
    "El ojo gerencial lo ve todo. Especialmente los críticos en rojo. 🔴",
    "Yudy, todo el equipo trabaja para que estos datos sean precisos. Para ti.",
    "Gerente Yudy: donde hay liderazgo, hay inventario al día. 📋",
    "Yudy revisando el sistema como si fuera un boardroom silencioso. 💼",
    "La gerencia no improvisa. Los datos de hoy lo confirman.",
]

_MESSAGES_EXTRA = [
    # Curiosidades de datos y negocios
    "Un sistema de inventario bien implementado reduce pérdidas hasta en 30%. 📉",
    "El dato más peligroso: el que nadie revisa. Por eso estás aquí.",
    "Sin visibilidad de inventario, la bodega es una caja negra. 📦",
    "Las empresas que usan datos toman decisiones 5x más rápido. ⚡",
    "El inventario es el corazón de la producción. Monitorémoslo juntos.",
    "Automatizar el control de inventario = menos errores humanos. 🤖",
    "Un faltante no detectado a tiempo puede parar la producción. ¡Al día!",
    "En logística dicen: lo que no se mide, no se mejora. 📏",
    "Los datos de Siigo + el análisis de aquí = decisiones ganadoras. 🏆",
    "¿Stock crítico? Mejor saberlo hoy que enterarse mañana. 🚨",
    # Día de la semana - fin de semana
    "¿Trabajando en fin de semana? Eso es compromiso de verdad. 💪",
    "Sábado de inventario: los mejores equipos nunca descansan del todo. 📊",
    "Domingo de monitoreo: porque el lunes tiene que arrancar perfecto.",
    "Fin de semana + revisión de datos = profesional nivel élite. 🥇",
    # Humor tech
    "Conexión API establecida. ¡Houston, no hay problemas! 🚀",
    "Este sistema tiene más uptime que algunos empleados. 😂 (es broma)",
    "Bug encontrado: ninguno. Feature desplegada: muchas. 🎉",
    "El servidor de Siigo está feliz de escuchar. Los datos fluyen. 🌊",
    "Carga asíncrona, resultados síncronos con la realidad. ✅",
    "El dashboard se actualiza más rápido que los rumores en la empresa. 🗣️",
    "Python + Streamlit = combo perfecto para inventario en tiempo real. 🐍",
    "Los logs están limpios. Los datos, también. Buen día. 🧼",
    # Motivacionales
    "Cada decisión basada en datos es una decisión más inteligente. 💡",
    "El control de inventario es respeto por el trabajo de toda la cadena.",
    "Ver los números claros: eso es poder gerencial. 💎",
    "La información es poder. Y tú tienes toda aquí. 📡",
    "Colsabor crece porque su equipo cuida cada detalle. Tú lo sabes.",
    "Confía en el proceso. Y en los datos. Son objetivos.",
    "Hoy es buen día para que todo esté en verde. ¡Maniféstalo! 🟢",
]

# Mensajes totales: combinamos todos
MESSAGES: list[str] = (
    _MESSAGES_GENERAL
    + _MESSAGES_MORNING
    + _MESSAGES_AFTERNOON
    + _MESSAGES_NIGHT
    + _MESSAGES_DEVELOPER
    + _MESSAGES_DIRECTOR
    + _MESSAGES_GERENTE
    + _MESSAGES_EXTRA
)


# ── Funciones públicas ────────────────────────────────────────────────────────

def get_greeting(email: str) -> str:
    """Devuelve saludo personalizado basado en hora y email del usuario."""
    hour = datetime.now().hour
    if 5 <= hour < 12:  # pragma: no cover
        saludo = "Buenos días"  # pragma: no cover
    elif 12 <= hour < 19:  # pragma: no cover
        saludo = "Buenas tardes"  # pragma: no cover
    else:  # pragma: no cover
        saludo = "Buenas noches"  # pragma: no cover

    role, name = _PERSONAS.get(email, ("", email.split("@")[0].replace(".", " ").title()))
    if role:
        return f"{saludo}, {role} {name}"
    return f"{saludo}, {name}"  # pragma: no cover


def get_random_message(email: str = "") -> str:
    """Devuelve un mensaje random, con preferencia hacia mensajes personalizados."""
    hour = datetime.now().hour

    # Pool ponderado: mensajes del momento del día + personalizados + generales
    pool: list[str] = list(_MESSAGES_GENERAL)
    pool.extend(_MESSAGES_EXTRA)

    if 5 <= hour < 12:  # pragma: no cover
        pool.extend(_MESSAGES_MORNING * 3)  # pragma: no cover
    elif 12 <= hour < 19:  # pragma: no cover
        pool.extend(_MESSAGES_AFTERNOON * 3)  # pragma: no cover
    else:  # pragma: no cover
        pool.extend(_MESSAGES_NIGHT * 3)  # pragma: no cover

    if email == "samuelrestrepodev@gmail.com":  # pragma: no cover
        pool.extend(_MESSAGES_DEVELOPER * 4)  # pragma: no cover
    elif email == "dirtec@colsabor.com.co":  # pragma: no cover
        pool.extend(_MESSAGES_DIRECTOR * 4)  # pragma: no cover
    elif email == "gerencia@colsabor.com.co":  # pragma: no cover
        pool.extend(_MESSAGES_GERENTE * 4)  # pragma: no cover

    return random.choice(pool)
