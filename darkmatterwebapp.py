import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
import numpy as np
altair==4.2.2
#-----------------------------------------------------------------------------------------------------------
#user defined functions
def createdata(file):
    df = pd.read_csv(file, delim_whitespace=True)
    # Check if the required columns exist in the DataFrame
    if 'radius' not in df.columns or 'velocity' not in df.columns:
        st.error("Required columns 'radius' or 'velocity' are missing in the dataset.")
        return

    # Extract the relevant data
    r = df['radius']
    v = df['velocity']
    
    error = None
    if 'error' in df.columns:
        error = df['error']
    
    return r,v,error

def plot_it(r,v,error,x_label,y_label,title,logscale=False):
    plt.figure(figsize=(10, 6))
    
    plt.xlabel(x_label)  # Set the x-axis label
    plt.ylabel(y_label)  # Set the y-axis label
    
    plt.plot(r, v, color='grey', alpha=0.5)  # Connect points with a line
    plt.errorbar(r, v, yerr=error, fmt='o', capsize=2, label='data', color='black')
    plt.title(title)
    if logscale==True:
        plt.xscale('log')
        plt.yscale('log')
    plt.grid(True)
    plt.legend()
    
    # Display the plot in Streamlit
    st.pyplot(plt)
    
#---------------------------------------------------------------------------------------------------------

# Streamlit app layout
st.title("Study of Dark Matter")
st.header("galaxy rotation curve")
st.write("Developed by Pranjal Sharma")
st.write("Under the guidance of Dr. C. Konar")
st.sidebar.write("Upload a text file with galaxy rotaton curve data")

st.sidebar.write("Units used in dataset")
col1, col2, col3, col4 = st.sidebar.columns([1,0.3, 0.3, 1])
with col1:
    st.write("radius :")
with col2:
    st.write("m")
with col3:          
    r_in_kpc = st.toggle("", value=True)  # Default to False (Off)
with col4:
    st.write("kPc ")

with col1:
    st.write("speed :")
with col2:
    st.write("m/s")
with col3:
    v_in_kms = st.toggle(" ", value=True)  # Default to False (Off)
with col4:
    st.write("km/s")

L= st.sidebar.number_input("Luminosity",value=1.5e11,format='%e')
mlratio =st.sidebar.number_input("Mass to light ratio",value=1.5,format='%e')

#---------------------------------------------------------------------------------------------------------
    # r_kpc = list of r in kpc
    # r_si = list of r in m
    # v_kms = list of v in km/s
    # v_si = list of v in m/s
    # slope = list of slopes for rotation curve in si unit
    # rho = list of density in kg/m^2 
    # rho_kpc2 = list of density solar mass/kpc^2
# File uploader

uploaded_file = st.sidebar.file_uploader("Choose a text file", type="txt")
st.sidebar.write("**columns should be named 'radius', 'velocity', and 'error'.")
#data collection and unit correction
if uploaded_file is None:
    st.sidebar.write("using sample milkyway dataset. upload file and provide asked values to process other dataset")
    r,v,error = createdata('mw.txt')
if uploaded_file is not None:
    r,v,error = createdata(uploaded_file)
if error is None or (isinstance(error, pd.Series) and error.empty):
    error = []
    for i in r:
        error.append(0)
if r_in_kpc==True:
    r_kpc=r
    r_si=[i*3.086e+19 for i in r]
else:
    r_kpc=[i*3.241e-20 for i in r]
    r_si=r
if v_in_kms==True:
    v_kms=v
    v_si=[i*1e3 for i in v]
    error_si=[i*1000 for i in error]
else:
    v_kms=[i*1e-3 for i in v]
    v_si=v
del r,v
    
plot_it(r_kpc,v_kms,error,'Radius (kPc)','Velocity (km/s)','Galaxy Rotation Curve')
#---------------------------------------------------------------------------------------------------------
#               calculating slope
slope=[]
slope.append(v_si[0]/r_si[0])
for i in range(len(r_si)-1):
    dy= v_si[i+1]-v_si[i]
    dx= r_si[i+1]-r_si[i]
    s=abs(dy/dx)
    slope.append(s)
    
#NOTE :slope for the radius at index 0 is taken relative to origin as starting point'''
#---------------------------------------------------------------------------------
#               calculating rho

br=[]
for i in range(len(slope)):
    b=1 + 2*(r_si[i]/v_si[i])*slope[i]
    br.append(b)
rho=[]
for i in range(len(br)):
    xx=r_si[i]
    yy=v_si[i]
    bb=float(br[i])
    r=(yy**2)/(4*3.14*6.67e-11*xx**2)*bb
    rho.append(r)
result={}
for i in range(len(rho)):
    result[r_si[i]]=rho[i]
    
error_density=[i*0 for i in rho]
rho_kpc2=[i*(2.938e58*5.028e-31) for i in rho]
#---------------------------------------------------------------------------------

st.header('density profile')
'Asuming spherically symmetry'
st.latex(r' \rho (r) = \frac{v(r)^2}{4 \pi G r^2} ( 1 + 2 \frac{dlogv(r)}{dlogr} ) ')
plot_it(r_kpc,rho_kpc2,error_density,'Radius (kPc)','density (solar masses/kpc^3)','Density Profile',logscale=True)   

#---------------------------------------------------------------------------------
#               calculating mass
dx=[]
for i in range(len(rho)-1):
    d=r_si[i+1]-r_si[i]
    dx.append(d)
    
yaxis=[]
for i in range(len(rho)):
    v=4*3.14*(r_si[i])**2
    yaxis.append(v)
dv=[]
for i in range(len(yaxis)-1):
    v=dx[i]*yaxis[i]
    dv.append(v)
mass=[]
for i in range(len(rho)-1):
    m=rho[i]*dv[i]
    mass.append(m)
totalmass=0
for i in range(len(mass)):
    totalmass+=mass[i]
massPU=totalmass*5.02785e-31

#---------------------------------------------------------------------------------

st.success(f'Total mass = {massPU:e} solar masses')

L_mass=mlratio*L
st.latex(r"Luminous \ matter = mass \ to \ light \ ratio \times luminosity")
st.success(f'Luminous matter = {L_mass:e} solar masses')

darkmatter=massPU - L_mass
st.latex(r"Dark \ Matter = Total \ matter - Luminous \ matter")
st.info(f"Dark matter = {darkmatter:e} solar masses" )
st.info(f'Ratio of dark matter to luminous matter is {darkmatter/L_mass}')
st.info(f'Percentage of dark matter in the galaxy= {darkmatter*100/massPU} %')

table=st.checkbox("see data table") #ask if they want to see the table

data={'radius in kPc':r_kpc,'velocity in km/s':v_kms,"density in solar mass per kPc^3":rho_kpc2}

dataset=pd.DataFrame(data)
for column in dataset.columns:
    dataset[column] = dataset[column].apply(lambda x: '{:.2e}'.format(x))


if table:
    st.dataframe(dataset, use_container_width=True)
#---------------------------------------------------------------------------------

st.markdown("""
<div style='text-align: right;'>
    <p><strong>By Pranjal Sharma</strong></p>
    <p><strong>under guidance of Dr. C. Konar</strong></p>
</div>
""", unsafe_allow_html=True)
#--------------------------------------------------------------------------------------------------------
st.markdown("---")
st.subheader("My Scientific Tools:")

apps = [
    {"name": "Cloudy Online", "url": "https://cloudyonline.streamlit.app/", "desc": "Online interface for Cloudy spectral synthesis."},
    {"name": "Cloudy Interpreter", "url": "https://cloudy-output-interpreter.streamlit.app/", "desc": "Analyze and visualize Cloudy output files."},
    {"name": "Accretion Disk Sim", "url": "https://accretion-disk-spectrum.streamlit.app/", "desc": "Standard accretion disk spectrum simulator."},
    {"name": "Dark Matter Estimator", "url": "https://darkmatter.streamlit.app/", "desc": "Rotation curves and dark matter halo estimation."},
    {"name": "GraphAway", "url": "https://graphaway.streamlit.app/", "desc": "Advanced plotting and graphing tool for researchers."}
]

cols = st.columns(3)
for i, app in enumerate(apps):
    with cols[i % 3]:
        st.markdown(f"#### [{app['name']}]({app['url']})")
        st.caption(app['desc'])
        st.markdown("---")
#--------------------------------------------------------------------------------------------------------
