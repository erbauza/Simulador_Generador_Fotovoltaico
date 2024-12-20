import datetime
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
import streamlit.components.v1 as components

def plot_potencia(datos, fecha_inicio, fecha_fin, temporada, color):
    # Filtrar los datos entre las fechas proporcionadas
    subtabla = datos.loc[fecha_inicio:fecha_fin, :]
    
    # Mostrar el título y el gráfico de barras
    st.markdown(
        f"""
        <div style="text-align:center;">

        ### Potencia instantánea en función del tiempo 
        ##### {temporada}
        </div>
        """,
        unsafe_allow_html=True
    )
    st.bar_chart(data=subtabla, y='Potencia (kW)', x_label='Tiempo',
                 y_label='Potencia instantánea generada (kW)', color=color, use_container_width=True)

    
    lapsos_funcionamiento = (subtabla['Potencia (kW)'] > 0).sum() #Lapsos de funcionamiento 
    lapsos_no_funcionamiento = (subtabla['Potencia (kW)'] == 0).sum() #Lapsos de NO funcionamiento 

    subtabla = subtabla.resample('D').mean() #Calculo el promedio diario 

    st.markdown(
        f"""
        <div style="text-align:center;">

        ### Potencia media diaria 
        ##### {temporada}
        </div>
        """,
        unsafe_allow_html=True
    )
    st.bar_chart(data=subtabla, y='Potencia (kW)', x_label='Tiempo',
                 y_label='Potencia diaria promedio (kW)', color=color, use_container_width=True)

    #tiempo de funcionamiento, no funcionamiento en horas y total
    t_funcionamiento = (10/60) * lapsos_funcionamiento  # cada lapso es de 10 min
    t_no_funcionamiento = (10/60) * lapsos_no_funcionamiento
    t_total = t_funcionamiento + t_no_funcionamiento
    porcentajes = [t_funcionamiento/t_total, t_no_funcionamiento/t_total]
    etiqueta = ['Porcentaje de Horas de Funcionamiento', 'Porcentaje de Horas sin Funcionamiento']

    st.markdown(
        f"""
        <div style="text-align:center;">

        ### Tiempo de funcionamiento
        ##### {temporada}
        La temporada tiene {t_total: .0f} horas, de las cuales el generador produce energía durante {t_funcionamiento: .0f} horas.
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # Gráfico de torta
    fig, ax = plt.subplots()
    ax.pie(porcentajes, labels=etiqueta, autopct='%1.1f%%', startangle=90, colors=[color, '#84917c'])
    ax.axis('equal')
    st.pyplot(fig)
    st.write('---')








# st.set_page_config(layout="wide") 
st.set_page_config(layout="centered") #Ajusta el contenido al centro de la pantalla

# usamos al final tabs ya que la otra forma no dejaba guardar el archivo subido
informacion, calculos, resultados = st.tabs(["Información", "Cálculos", "Resultados"])

with informacion:

    # el container va separando contenidos, para que quede bien modular
    with st.container():
        
        # lo siguiente que está escrito, y lo mismo va para todos los demas markdowns, es una forma que encontramos
        # para poder ajustar texto, centrarlo, etc, con la función de que te acepte codificación html
        st.markdown (
            """
            <div style="text-align:center;">

            # Generador Fotovoltáico

            </div>

            <div style="text-align:justify;">
            
            ## Modelo básico para la estimación de la potencia erogada

            Un generador fotovoltaico (GFV) convierte parte de la energía proveniente de la radicación solar en
            la forma eléctrica. La instalación se ejecuta en forma modular; una cantidad N de paneles (o módulos)
            se vinculan a través de sus terminales de salida en una configuración mixta serie-paralelo.<br>

            La tensión eléctrica provista por un GFV es del tipo continua, es decir, que se mantiene constante
            siempre que lo hagan las condiciones de radiación solar y temperatura. No obstante, dado que esto
            último no es posible, se requiere de un equipo electrónico que funciona como controlador, que busca
            estabilizar las con diciones de operación siempre que sea posible.<br>

            Una variante muy difundida altera convenientemente dicha tensión para que la potencia erogada sea la
            máxima posible de acuerdo con las condiciones meteorológicas del momento1. Asimismo, en virtud de que
            las redes eléctricas no suelen operar con tensión continua, sino en forma alterna (con una variación
            sinusoidal en el tiempo), un circuito electrónico “inversor” es requerido para realizar la conversión.
            
            </div>
            """,
            unsafe_allow_html=True  
         )
        
        st.image("Esquema en bloques de un GFV.jpeg", caption="Esquema en bloques de un GFV")

       
    with st.container():

        st.divider()
        st.header('Modelo matemático del GFV')
        st.markdown(
            """
            <div style="text-align:justify;">

            Se implementa un modelo simplificado la siguiente expresión obtiene la potencia eléctrica P (en
            kW) obtenida por un GFV, siempre que todos los módulos sean idénticos y cuando se utiliza un
            controlador de potencia que altera la condición de tensión de trabajo para maximizar el rendimiento.

            </div>

            <div style="text-align:center;">

            $P= N \cdot \\frac{G}{G_{std}} \cdot P_{pico} \cdot [1+k_p \cdot(T - T_r)] \cdot \eta \cdot 10^{-3} \quad (1)$

            </div>
            """,
            unsafe_allow_html=True  
        )
        
        # para expandir y contraer las referencias de las variables de la fórmula de cálculo de potencia
        with st.expander('Referencias'):
            st.markdown(
            """
            <div style="text-align:justify;">

            * **$G$:** Irradiancia global incidente en forma normal a los módulos fotovoltaicos, en $W/m^2$. La
            irradiancia mide el flujo de energía proveniente de la radiación solar (sea de forma directa o indirecta)
            por unidad de superficie incidente.
            * **$G_{std}$:** Irradiancia estándar, en $W/m^2$. Es un valor de irradiancia que utilizan los fabricantes
            de los módulos para referenciar ciertas características técnicas. Normalmente $G_{std} = 1000[W/m^2]$.
            * **$T_r$:** Temperatura de referencia, en *Celsius*. Es una temperatura utilizada por los fabricantes de
            los módulos para referenciar ciertos parámetros que dependen de la temperatura. Normalmente $Tr = 25[^◦C]$.
            * **$T_c$:** Temperatura de la celda, en *Celsius*. Es la temperatura de los componentes semiconductores
            que conforman cada módulo fotovoltaico.
            * **$P_{pico}$:** Potencia pico de cada módulo, en *Watt*. Se interpreta como la potencia eléctrica que
            entrega un módulo cuando $G$ coincide con $G_{std}$ y cuando $T_c$ coincide con $T_r$, en ausencia de
            viento y sin que el panel se vincule a otros componentes eléctricos que afecten el desempeño de la
            instalación. Constituye la potencia nominal bajo la cual los módulos son comercializados.
            * **$k_p$:** Coeficiente de temperatura-potencia, en $^◦C^{-1}$. Es un parámetro negativo que refleja
            cómo incide la temperatura de la celda en el rendimiento del GFV. Se observa que incrementos (disminuciones)
            de $T_c$ producen, en consecuencia, disminuciones (incrementos) de *P*.
            * **$η$:** Rendimiento global de la instalación “por unidad” (valor ideal: 1). Se utiliza para considerar el
            efecto de sombras parciales sobre el GFV, suciedad sobre la superficie de los módulos y, fundamentalmente,
            el rendimiento del equipo controlador-inversor. Los inversores contemplados por el modelo de la Ec. (1)
            también incluyen el sistema de control para maximizar la potencia de salida.

            </div>
            """,
            unsafe_allow_html=True  
            )
                
    with st.container():

        st.divider()
        st.header('Límite de generación')
        
        st.markdown(
            """
            <div style="text-align:justify;">

            Los circuitos inversores funcionan adecuadamente siempre que la producción, en términos de potencia,
            supere un umbral mínimo $µ$, habitualmente expresado en forma porcentual, en relación a la potencia nominal
            $P_{inv}$ del equipo. Si este umbral no es superado, la instalación no entrega potencia eléctrica.
            
            $$
            P_r \, [\\text{kW}] =
            \\begin{cases} 
            0 & \\text{si } P \leq P_\\text{min}, \\\\
            P & \\text{si } P_\\text{min} < P \leq P_\\text{inv}, \\\\
            P_\\text{inv} & \\text{si } P > P_\\text{inv}.
            \end{cases}
            $$

            </div>
            """,
            unsafe_allow_html=True  
            )

    with st.container():
        st.divider()
        st.header('GFV de la UTN Facultad Regional Santa FE')
        [info_utn, animacion]= st.columns([0.7,0.3]) # se crearon 2 columnas, una con texto, y otra con un gif
        with info_utn:
            st. markdown(
                """
                <div style="text-align:justify;">

                La UTN Facultad Regional Santa Fe dispone de un GFV de $2,88[kW]$ de potencia nominal, en combinación con
                un equipo inversor para su acoplamiento con la red eléctrica de baja tensión. Utiliza un conexionado de
                $N = 12$ módulos de la marca HISSUMA, con $P_{pico} = 240[W]$ y $k_p = -0,0044[◦C^{-1}]$.<br>
                El equipo inversor (monofásico) es de la marca SMA, con $P_{inv} = 2,5[kW]$ de potencia nominal. El modelo
                específico es SB2.5-1VL-40. El rendimiento global de la instalación se considera de $η = 0,97$, determinado
                fundamentalmente por el inversor. 
            
                </div>
                """,
                unsafe_allow_html=True
            )
        with animacion:
            st.image('UTN.gif',use_container_width=True)

        st.markdown(
            """
            <div style="text-align:justify;">

            Sin embargo, se observa que, de acuerdo con la ficha técnica, este rendimiento no es 
            rigurosamente constante, ya que depende de la potencia entregada en relación con su 
            capacidad nominal. A menores niveles de carga, el inversor puede experimentar una ligera 
            disminución en su eficiencia, lo que destaca la importancia de dimensionar correctamente 
            el sistema para operar en un rango óptimo. Este aspecto técnico debe ser considerado 
            al evaluar el desempeño global de la instalación en escenarios reales, especialmente en 
            días con variabilidad en la irradiancia solar o durante horarios de menor producción
            energética.
            </div>
            """,
            unsafe_allow_html=True
            )
        
        # si se desea saber más, se dispone un recuadro con la página de la facultad que habla del tema
        components.iframe('https://www.frsf.utn.edu.ar/noticias/606-energia-limpia-y-ahorro-energetico-un-compromiso-para-la-utn-santa-fe',height=400 ,scrolling=True)


with calculos: 
    
    st.markdown(
        """
        <div style="text-align:center;">

        # Cálculos Generador Fotovoltáico
        </div>
        <div style="text-align:justify;">

        El simulador presentado permite el cálculo de la potencia producida por
        el generador, según la formula presentada a continuación. Además, todos los parámetros 
        pueden ser modificados, permitiendo así la simulación de distintos casos de interes.
        Asimismo, los valores asignados a los parámetros se utilizan en la sección Resultados 
        para el cálculo de los valores de potencia y energía con los que se trazan distintas curvas
        y gráficos.
        </div>
        """,
        unsafe_allow_html=True  
    )

    st.markdown(
        """
        <div style="text-align:center;">

        $P= N \cdot \\frac{G}{G_{std}} \cdot P_{pico} \cdot [1+k_p \cdot(T - T_r)]* \cdot \eta \cdot 10^{-3}$

        </div>
        """,
        unsafe_allow_html=True  
    )

    click_2 = st.checkbox('Modificar valores estándar', False)
    # si click_2 es true, uno puede modificar los valores, de otra forma se clavan los parámetros de la facu
    if click_2:
        st.write("Modifique los valores")
        Gstd = st.number_input('Irradiancia estándar $[W/m^2]$', min_value=0, max_value=1500, value=1000)
        Tr = st.number_input('Temperatura de Referencia $[°C]$', min_value=0.0, max_value=60.0, value=25.0, format='%.1f', step=0.1)
    else:
        Gstd = 1000
        Tr = 25
        st.write(f'**Irradiancia estándar: {Gstd:.0f} $[W/m^2]$**')
        st.write(f'**Temperatura estándar de Referencia : {Tr:.0f} $[°C]$**')
    
    
    DatosUTN = st.toggle("Activar para trabajar con los valores del generador de la FRSF-UTN")
    # lo mismo sucede aqui, nada más que con un toggle
    if DatosUTN:
        st.write('Activado FRSF-UTN')
        N = st.number_input('Cantidad de paneles', min_value=12, max_value=12, value=12)
        Ppico = st.number_input('Potencia Pico del panel [W]', min_value=240, max_value=240, value=240)
        G = st.number_input('Nivel de irradiancia $[W/m^2]$', min_value=1000, max_value=1000, value=1000)
        T = st.number_input('Temperatura [°C]', min_value=20.0, max_value=20.0, value=20.0, format='%.1f')
        kp = st.number_input('Coeficiente de pot-temp', min_value=-0.0044, max_value=-0.0044, value=-0.0044, format='%.4f')
        eta = st.number_input('Rendimiento global', min_value=0.97, max_value=0.97, value=0.97, format='%.2f')
    else:
        N = st.number_input('Cantidad de paneles', min_value=1, max_value=1000, value=12)
        Ppico = st.number_input('Potencia Pico del panel [W]', min_value=1, max_value=2000, value=240)
        G = st.number_input('Nivel de irradiancia $[W/m^2]$', min_value=0, max_value=1500, value=1000)
        T = st.number_input('Temperatura [°C]', min_value=-10.0, max_value=60.0, value=20.0, format='%.1f', step=0.5)
        kp = st.number_input('Coeficiente de pot-temp', min_value=-0.01, max_value=0.0, value=-0.0044, format='%.4f', step=0.001)
        eta = st.number_input('Rendimiento global', min_value=0.0, max_value=1.0, value=0.97, format='%.2f', step=0.01)
    
    # el siguiente session_state quedó de unas pruebas intentando
    st.session_state['inputs'] = {'Gstd': Gstd, 'Tr': Tr, 'N': N, 'Ppico': Ppico,
                                    'G': G, 'T': T, 'kp': kp,'eta': eta}

    P = N * Ppico * G / Gstd * (1 + kp * (T - Tr)) * eta * 1e-3
    
    st.success(f'**Potencia obtenida: {P:.2f} kW**')


with resultados:

    #titulo principal
    st.markdown(
        """
        <div style="text-align:center;">

        # Resultados

        </div>
        <div style="text-align:justify;">

        En este apartado usted podrá ingresar un archivo tipo .xlsx, cuyas columnas contengan
        valores de *Nivel de Irradiancia* y *Temperatura*, para luego recibir una serie de 
        gráficos obtenidos a raíz del análisis de los datos subidos y los parámetros
        configurados en la sección Cálculos.
        
        </div>
        """,
        unsafe_allow_html=True  
    )

    if 'tabla' not in st.session_state:
        st.session_state['tabla'] = None
    
    archivo = st.file_uploader("Cargar archivo", type='xlsx', accept_multiple_files=False)
    if archivo:
        st.session_state['archivo'] = archivo
        
        if st.button("Recibir Resultados"):
            if 'archivo' in st.session_state:
                archivo = st.session_state['archivo']
                tabla = pd.read_excel(archivo, index_col=0)
                nombre_G, nombre_T = tabla.columns

                inputs = st.session_state['inputs']
                tabla['Potencia (kW)'] = (
                    inputs['N'] * inputs['Ppico'] * tabla[nombre_G] / inputs['Gstd']
                    * (1 + inputs['kp'] * (tabla[nombre_T] - inputs['Tr'])) * inputs['eta'] * 1e-3
                )
                tabla['Energía (kWh)']= tabla['Potencia (kW)']*10/60
                st.session_state['tabla'] = tabla
       
        if st.session_state['tabla'] is not None:
            st.logo('UTN_FRSF_logo.jpg')
            st.write('¡Su tabla ha sido cargada con éxito!')
            st.dataframe(st.session_state['tabla'], use_container_width=True)
            st.write('---')

            # Selección de fecha
            with st.sidebar:
                st.write('Seleccione las caracteristicas de su interes.')
                diario= st.checkbox('Evolución Diaria')
            if diario is True:
                st.header('Evolución Diaria')
                fecha = st.date_input(
                    "Seleccionar día",
                    value=datetime.date(2019, 1, 1),
                    min_value=datetime.date(2019, 1, 1),
                    max_value=datetime.date(2019, 12, 31)
                )
                # Filtrar tabla por fecha
                st.markdown(
                        """
                        <div style="text-align:center;">

                        ### Evolución de la Potencia intantánea en el día 

                        </div>
                        """,
                        unsafe_allow_html=True  
                    )
                subtabla = st.session_state['tabla'].loc[f'{fecha.year}-{fecha.month}-{fecha.day}', :]
                st.line_chart(data=subtabla, y='Potencia (kW)', x_label='Tiempo', y_label='kW', use_container_width=True)
                st.write('---')
            with st.sidebar:
                anual= st.checkbox('Características Anuales de Funcionamiento')
            if anual is True:
                #Energía
                tabla_anual= st.session_state['tabla']
                energia_anual=(tabla_anual['Energía (kWh)']).sum()
                #Horas de funcionamiento
                lapsos_funcionamiento_anual=(tabla_anual['Potencia (kW)']>0).sum()
                lapsos_no_funcionamiento_anual=(tabla_anual['Potencia (kW)']==0).sum()
                t_funcionamiento_anual= (lapsos_funcionamiento_anual)*10/60
                t_no_funcionamiento_anual= (lapsos_no_funcionamiento_anual)*10/60
                porcentajes_anual= [t_funcionamiento_anual, t_no_funcionamiento_anual]
                etiqueta=['Porcentaje de Horas de Funcionamiento', 'Porcentaje de Horas sin Funcionamiento']
                st.markdown(
                        f"""
                        ##### Energía anual producida = {energia_anual: .1f} (kWh).
                        <div style="text-align:center;">

                        ### Tiempo de funcionamiento anual
                        De las 8760 horas del año, el generador produce energía 
                        durante {t_funcionamiento_anual: .0f} horas.
                        </div>
                        """,
                        unsafe_allow_html=True  
                    )
                fig, ax = plt.subplots()
                ax.pie(
                        porcentajes_anual, 
                        labels=etiqueta, 
                        autopct='%1.1f%%', 
                        startangle=90, 
                        colors=['#fff700', '#84917c']
                )
                ax.axis('equal')
                st.pyplot(fig)
                st.write('---')

            with st.sidebar:
                estacional= st.checkbox('Características Estacionales de Funcionamiento ')
            #st.sidebar( estacional= st.checkbox('Características Estacionales de Funcionamiento '))
            if estacional is True:
                
                with st.sidebar: 
                    st.write('---')
                    estaciones = st.popover("Marque las estaciones de interes")
                    prim = estaciones.checkbox("Primavera ", False)
                    ver = estaciones.checkbox("Verano", False)
                    oto = estaciones.checkbox("Otoño ", False)
                    invi = estaciones.checkbox("Invierno", False)
                    st.write('---')
                

                if prim is True:
                    inicio_prim='2019-09-21'
                    fin_prim= '2019-12-20'
                    a=plot_potencia(st.session_state['tabla'],inicio_prim,fin_prim, 'Primavera', color='#04d442')


                if ver is True:
                    subtabla_ver1 = st.session_state['tabla'].loc['2019-01-01':'2019-3-20', :]
                    subtabla_ver2= st.session_state['tabla'].loc['2019-12-21':'2019-12-31', :]
                    subtabla_ver= pd.concat([subtabla_ver1, subtabla_ver2])
                    st.markdown(
                        """
                        <div style="text-align:center;">

                        ### Potencia intantánea en función del tiempo
                        ##### Verano

                        </div>
                            """,
                        unsafe_allow_html=True  
                    )
                    st.bar_chart(data=subtabla_ver, y='Potencia (kW)', x_label='Tiempo', y_label='Potencia instantanea generada (kW)',color='#f04507'  ,use_container_width=True)
                    lapsos_funcionamiento_ver = (subtabla_ver['Potencia (kW)'] > 0).sum()
                    lapsos_no_funcionamiento_ver = (subtabla_ver['Potencia (kW)'] == 0).sum()
                    subtabla_ver= subtabla_ver.resample('D').mean() #Valores promedios diarios
                    #subtabla_ver
                    st.markdown(
                        """
                        <div style="text-align:center;">

                        ### Potencia media diaria
                        ##### Verano

                        </div>
                        """,
                        unsafe_allow_html=True  
                    )
                    st.bar_chart(data=subtabla_ver, y='Potencia (kW)', x_label='Tiempo', y_label='Potencia diaria promedio (kW)',color='#f04507', use_container_width=True)
                    t_funcionamiento_ver= (10/60)*lapsos_funcionamiento_ver #cada lapso es de 10 min. t_funcionamiento en horas
                    t_no_funcionamiento_ver= (10/60)*lapsos_no_funcionamiento_ver #cada lapso es de 10 min. t_funcionamiento en horas
                    t_total_ver=t_funcionamiento_ver+t_no_funcionamiento_ver
                    porcentajes_ver= [t_funcionamiento_ver/t_total_ver, t_no_funcionamiento_ver/t_total_ver]
                    etiqueta=['Porcentaje de Horas de Funcionamiento', 'Porcentaje de Horas sin Funcionamiento']
                    #Gráfico de tortas
                    st.markdown(
                        f"""
                        <div style="text-align:center;">

                        ### Tiempo de funcionamiento
                        ##### Verano
                        La primavera tiene 2184 horas, de las cuales el generador produce energía 
                        durante {t_funcionamiento_ver: .0f} horas.

                        </div>
                        """,
                        unsafe_allow_html=True  
                    )
                    fig, ax = plt.subplots()
                    ax.pie(
                        porcentajes_ver, 
                        labels=etiqueta, 
                        autopct='%1.1f%%', 
                        startangle=90, 
                        colors=['#f04507', '#84917c']
                    )
                    ax.axis('equal')
                    st.pyplot(fig)
                    st.write('---')
                

                if oto is True:
                    inicio_otoño='2019-03-21'
                    fin_otoño= '2019-06-20'
                    plot_potencia(st.session_state['tabla'],inicio_otoño,fin_otoño, 'Otoño', color='#b06e17')
                    
                

                if invi is True:
                    inicio_invierno='2019-06-21'
                    fin_invierno= '2019-09-20'
                    plot_potencia(st.session_state['tabla'],inicio_invierno,fin_invierno, 'Invierno', color='#09a9e3')

                    