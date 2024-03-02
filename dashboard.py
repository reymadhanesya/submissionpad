import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency
sns.set(style='dark')

# menyiapkan DataFrame
# create_daily_sharing_df()
def create_daily_sharing_df(df):
    daily_sharing_df = df.resample(rule='D', on='dteday').agg({
        "cnt": "sum",
        "casual": "sum",
        "registered": "sum"
    })
    daily_sharing_df = daily_sharing_df.reset_index()
    daily_sharing_df.rename(columns={
        "cnt": "sharing_total",
        "casual": "casual_total",
        "registered": "registered_total"
    }, inplace=True)
    
    return daily_sharing_df

# create_byworkingday_df()
def create_byworkingday_df(df):
    byworkingday_df = df.groupby(by="workingday").cnt.nunique().reset_index()
    byworkingday_df.rename(columns={
        "cnt": "workingday_count"
    }, inplace=True)
    
    return byworkingday_df

# create_byweather_df()
def create_byweather_df(df):
    byweather_df = df.groupby(by="weathersit").cnt.nunique().reset_index()
    byweather_df.rename(columns={
        "cnt": "weather_count"
    }, inplace=True)
    
    return byweather_df

# create_rfm_df()
def create_rfm_df(df):
    rfm_df = df.groupby(by="instant", as_index=False).agg({
        "dteday": "max", #mengambil tanggal sewa terakhir
        "casual": "nunique",
        "cnt": "sum"
    })
    rfm_df.columns = ["instant", "max_order_timestamp", "frequency", "monetary"]
    
    rfm_df["max_order_timestamp"] = rfm_df["max_order_timestamp"].dt.date
    recent_date = df["dteday"].dt.date.max()
    rfm_df["recency"] = rfm_df["max_order_timestamp"].apply(lambda x: (recent_date - x).days)
    rfm_df.drop("max_order_timestamp", axis=1, inplace=True)
    
    return rfm_df

# load berkas day_data.csv sebagao sebuah DataFrame
day_df = pd.read_csv("day_data.csv")

# data day_data memiliki satu kolom bertipe datetime, yaitu dteday
# mengurutkan DataFrame berdasarkan dteday
datetime_columns = ["dteday"]
day_df.sort_values(by="dteday", inplace=True)
day_df.reset_index(inplace=True)
 
for column in datetime_columns:
    day_df[column] = pd.to_datetime(day_df[column])

# membuat komponen filter
# filter dengan widget date input serta menambahkan logo perusahaan
min_date = day_df["dteday"].min()
max_date = day_df["dteday"].max()
 
with st.sidebar:
    # Menambahkan logo perusahaan
    st.image("https://raw.githubusercontent.com/reymadhanesya/logo/main/bike/BikeSharingDashboard.png")
    
    # Mengambil start_date & end_date dari date_input
    start_date, end_date = st.date_input(
        label='Rentang Waktu',min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

# start_date dan end_date di atas digunakan untuk memfilter day_data
# data yang telah difilter akan disimpan dalam main_df
main_df = day_df[(day_df["dteday"] >= str(start_date)) & 
                (day_df["dteday"] <= str(end_date))]

# DataFrame yang telah difilter (main_df) digunakan untuk menghasilkan
# berbagai DataFrame yang dibutuhkan untuk membuat visualisasi data
daily_sharing_df = create_daily_sharing_df(main_df)
byworkingday_df = create_byworkingday_df(main_df)
byweather_df = create_byweather_df(main_df)
rfm_df = create_rfm_df(main_df)

# melengkapi dashboard dengan berbagai visualisasi data
st.header('Bike Sharing Dashboard :sparkles:')

st.subheader('Daily Sharing')

# menampilkan informasi casual users, registered users, dan total keduanya
col1, col2, col3 = st.columns(3)
 
with col1:
    total_sharing = daily_sharing_df.sharing_total.sum()
    st.metric("Total Sharing Bike", value=total_sharing)

with col2:
    total_registered = daily_sharing_df.registered_total.sum()
    st.metric("Total Registered", value=total_registered)

with col3:
    total_casual = daily_sharing_df.casual_total.sum()
    st.metric("Total Casual", value=total_casual)

fig, ax = plt.subplots(figsize=(16, 8))
ax.plot(
    daily_sharing_df["dteday"],
    daily_sharing_df["sharing_total"],
    marker='o', 
    linewidth=2,
    color="#90CAF9"
)
ax.tick_params(axis='y', labelsize=20)
ax.tick_params(axis='x', labelsize=15)
 
st.pyplot(fig)

# informasi antara hubungan hari kerja dengan jumlah sewa sepeda harian
st.subheader("Bagaimana hubungan antara hari kerja dengan jumlah sewa sepeda harian?")
 
fig, ax = plt.subplots(figsize=(20, 10))
colors = ["#90CAF9", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]
sns.barplot(
    x="workingday", 
    y="workingday_count",
    data=byworkingday_df.sort_values(by="workingday_count", ascending=False),
    palette=colors,
    ax=ax
)
ax.set_title("Jumlah Sewa Sepeda pada Hari Kerja", loc="center", fontsize=30)
ax.set_ylabel(None)
ax.set_xlabel(None)
ax.tick_params(axis='y', labelsize=20)
ax.tick_params(axis='x', labelsize=15)
st.pyplot(fig)

# informasi pengaruh cuaca terhadap jumlah sewa sepeda harian
st.subheader("Bagaimana pengaruh cuaca terhadap jumlah sewa sepeda harian?")

fig, ax = plt.subplots(figsize=(20, 10))
colors = ["#90CAF9", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]
sns.barplot(
    x="weathersit", 
    y="weather_count",
    data=byweather_df.sort_values(by="weather_count", ascending=False),
    palette=colors,
    ax=ax
)
ax.set_title("Jumlah Sewa Sepeda Berdasarkan Cuaca", loc="center", fontsize=30)
ax.set_ylabel(None)
ax.set_xlabel(None)
ax.tick_params(axis='y', labelsize=20)
ax.tick_params(axis='x', labelsize=15)
st.pyplot(fig)

# parameter RFM (Recency, Frequency, & Monetary)
# akan ditampilkan rata-rata dari ketiga parameter tersebut
st.subheader("Best Users Based on RFM Parameters")
 
col1, col2, col3 = st.columns(3)
 
with col1:
    avg_recency = round(rfm_df.recency.mean(), 1)
    st.metric("Average Recency (days)", value=avg_recency)
 
with col2:
    avg_frequency = round(rfm_df.frequency.mean(), 2)
    st.metric("Average Frequency", value=avg_frequency)
 
with col3:
    avg_frequency = format_currency(rfm_df.monetary.mean(), "AUD", locale='es_CO') 
    st.metric("Average Monetary", value=avg_frequency)
 
fig, ax = plt.subplots(nrows=1, ncols=3, figsize=(35, 15))
colors = ["#90CAF9", "#90CAF9", "#90CAF9", "#90CAF9", "#90CAF9"]
 
sns.barplot(y="recency", x="instant", data=rfm_df.sort_values(by="recency", ascending=True).head(5), palette=colors, ax=ax[0])
ax[0].set_ylabel(None)
ax[0].set_xlabel("instant", fontsize=30)
ax[0].set_title("By Recency (days)", loc="center", fontsize=50)
ax[0].tick_params(axis='y', labelsize=30)
ax[0].tick_params(axis='x', labelsize=35)
 
sns.barplot(y="frequency", x="instant", data=rfm_df.sort_values(by="frequency", ascending=False).head(5), palette=colors, ax=ax[1])
ax[1].set_ylabel(None)
ax[1].set_xlabel("instant", fontsize=30)
ax[1].set_title("By Frequency", loc="center", fontsize=50)
ax[1].tick_params(axis='y', labelsize=30)
ax[1].tick_params(axis='x', labelsize=35)
 
sns.barplot(y="monetary", x="instant", data=rfm_df.sort_values(by="monetary", ascending=False).head(5), palette=colors, ax=ax[2])
ax[2].set_ylabel(None)
ax[2].set_xlabel("instant", fontsize=30)
ax[2].set_title("By Monetary", loc="center", fontsize=50)
ax[2].tick_params(axis='y', labelsize=30)
ax[2].tick_params(axis='x', labelsize=35)
 
st.pyplot(fig)
 
st.caption('Copyright (c) Bike Sharing Dashboard 2024')