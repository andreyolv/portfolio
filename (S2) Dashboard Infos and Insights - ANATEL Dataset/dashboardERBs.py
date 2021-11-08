import streamlit as st
import pandas as pd
import simplekml
import base64
import io

# HEAD PAGE
st.write("""
# ERB Filter ANATEL Bashboard
This app ....!

Enter all info in left side bar to filter what you want
***
""")

# SIDE BAR INPUTS
st.sidebar.header("User Input Filters")

# Sidebar - ANATEL Service Selection
st.sidebar.subheader('ANATEL Service Selection')
services = ["SLP (Serviço Limitado Privado)",
            "SMP (Serviço Móvel Pessoal)"]
service_choice = st.sidebar.selectbox('Select your service filtering', services)

# Sidebar - CNPJ Input
st.sidebar.subheader('Company CNPJ')
cnpj_input = st.sidebar.number_input("CNPJ input", 1234567891009)

# Sidebar - City Input
st.sidebar.subheader('City')
city_input = st.sidebar.text_input("City input", "Curitiba")

# Sidebar - Coordinates Input
st.sidebar.subheader('Geographic Coordinates')
latitude_input = st.sidebar.number_input("Insert Latitude", 20.48411)
longitude_input = st.sidebar.number_input("Insert Longitude", 20.48411)
radius_input = st.sidebar.slider("Select radius in kilometers", min_value=0, max_value=120, step=1)

# Sidebar - Frequency Input
st.sidebar.subheader('Frequency Operation')
freq_init_input = st.sidebar.number_input("Insert Initial Frequency", 2000)
freq_end_input = st.sidebar.number_input("Insert End Frequency", 2050)














# MAIN CODE
# Loading Data
# @st.cache
# SLP Dataset load_data and cleaning:
df_slp = pd.read_csv("SLP (Serviço Limitado Privado).csv", sep=';', nrows=100, encoding='UTF-8')
df_slp = df_slp.drop(columns=['Bairro', 'Logradouro', 'Data Inclusão', 'Data Primeiro Licenciamento',
                    'Designação Emissão', 'Potência', 'Raio', 'Ganho', 'F/C', '1/2 Potência',
                    'Ângulo de Elevação', 'Azimute', 'Polarização', 'Data Último Licenciamento',
                    'Aplicação do Serviço', 'Tipo de Identificação'])

df_slp.rename(columns={"CNPJ/CPF": "CNPJ", "Nome/Razão Social": "Empresa", "Freq. Transmissão": "Frequência"})

df_slp.Latitude.dropna()
df_slp.Longitude.dropna()

# Converting Geographic Coordinates Format
def convert(coordenada):
    try:
        degree = coordenada[:2]
        minutes = coordenada[3:5]
        seconds = coordenada[5:]
        letra = coordenada[2]

        if letra == 'W' or letra == 'S':
            signal = -1

        if letra == 'O' or letra == 'N':
            signal = 1

        decimal_degrees = int(degree) + (int(minutes)/60) + (int(seconds)/360000)
        final = signal*decimal_degrees

        return final

    except IndexError:
        return 0

df_slp['Latitude'] = df_slp.Latitude.apply(convert)
df_slp['Longitude'] = df_slp.Longitude.apply(convert)

# SMP Dataset load_data and cleaning:
df_smp = pd.read_csv("SMP (Serviço Móvel Pessoal).csv", sep=';', nrows=100, encoding='ISO-8859-1')
df_smp = df_smp.drop(columns=['Tipo da Estação', 'UF', 'Código do Município', 'Logradouro', 'Azimute',
                    'Frequência Inicial (MHz)', 'Emissão', 'Código da UF'])
df_smp.rename(columns={"Prestadora": "Empresa", "Frequência Final (MHz)": "Frequência"})
df_smp['Nome do Serviço'] = "Serviço Móvel Pessoal"

df_smp.drop(df_smp[df_smp['Latitude'] == '*'].index, inplace=True)

# Concatenating the 2 dataframes into 1 dataframe
df_unique = pd.concat([df_slp, df_smp])

# Manipulating Unique Dataframe
df_unique["Número da Estação"].unique()
df_unique = df_unique.drop_duplicates(subset = "Número da Estação")

# Converting Geographic Coordinates Input into Search Range
lat_south = latitude_input - (radius_input/111)
lat_north = latitude_input + (radius_input/111)
long_west = longitude_input - (radius_input/111)
long_east = longitude_input + (radius_input/111)

# Filtering Dataframe based on user input values
con1 = df_unique['CNPJ/CPF'] == cnpj_input
con2 = df_unique['Município'] == city_input
con3 = df_unique['Latitude'] >> lat_south & df_unique['Latitude'] << lat_north
con4 = df_unique['Longitude'] >> long_west & df_unique['Longitude'] << long_east
con5 = df_unique['Frequencia'] >> freq_init_input & df_unique['Frequencia'] << freq_final_input

df_filtered = df[cond1 & cond2 & cond3 & cond4 & cond5]

# Exporting Dataframe to Kml file
lat_list = df_filtered['Latitude'].values.tolist()
long_list = df_filtered['Longitude'].values.tolist()
name_list = df_filtered['Número da Estação'].values.tolist()

kml = simplekml.Kml()

def export_kml():
    i = 0
    while i < len(lat_list):
        lat = lat_list[i]
        long = long_list[i]
        number = name_list[i]
        kml.newpoint(name=str(number), coords=[(long, lat)])  # lon, lat, optional height
        i = i + 1
    return kml.save("EstaçõesCNPJ.kml")














# MAINPAGE DASHBOARD
# Insights Output
st.header('Insights')
st.write("ERBs Quantity: ")

st.write("Graph Plots Here: ")

st.write("***")

# DataFrame Output
st.header('Spreadsheet')
st.dataframe(df)
st.write("Here you can download the spreadsheet dataframe filtered")

df_download = df_filtered.copy()

def filedownload(df):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()  # strings <-> bytes conversions
    linko = f'<a href="data:file/csv;base64,{b64}" download="playerstats.csv">Download CSV File</a>'
    return linko

st.markdown(filedownload(df_download), unsafe_allow_html=True)
st.write("***")

# Map Output
st.header('ERB Map')
# Show map here
st.write("Here you can download kmz file to see all ERB in GoogleEarth")
export_kml()