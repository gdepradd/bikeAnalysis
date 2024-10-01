import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Load datasets
data_day = pd.read_csv("dashboard/day.csv")
data_hour = pd.read_csv("dashboard/hour.csv")  
# Preprocess day data
def preprocess_day_data(df):
    df['dteday'] = pd.to_datetime(df['dteday'])
    return df
# Preprocess hour data
def preprocess_hour_data(df):
    df['dteday'] = pd.to_datetime(df['dteday'])
    return df
data_day = preprocess_day_data(data_day)
data_hour = preprocess_hour_data(data_hour)

######################################################## HELPER FUNCTION ######################################

# Helper function for seasonal working analysis
def season_rental_workingday(data):
    season1 = data[data['season']==1]
    season1['workingday'] = season1['workingday'].map({0:'Weekend Spring ', 1:'Workingday Spring'})
    season2 = data[data['season']==2]
    season2['workingday'] = season2['workingday'].map({0:'Weekend Summer', 1:'Workingday Summer'})
    season3 = data[data['season']==3]
    season3['workingday'] = season3['workingday'].map({0:'Weekend Fall', 1:'Workingday Fall'})
    season4 = data[data['season']==4]
    season4['workingday'] = season4['workingday'].map({0:'Weekend Winter', 1:'Workingday Winter'})
    season1_sum = season1.groupby('workingday')['cnt'].sum().reset_index()
    season2_sum = season2.groupby('workingday')['cnt'].sum().reset_index()
    season3_sum = season3.groupby('workingday')['cnt'].sum().reset_index()
    season4_sum = season4.groupby('workingday')['cnt'].sum().reset_index()
    season_total = pd.concat([season1_sum,season2_sum,season3_sum,season4_sum], ignore_index=True)
    return season_total

def season_rental(data):
    season_rental = data_day.groupby('season').agg(
    cnt_sum=('cnt', 'sum'),  
    cnt_mean=('cnt', 'mean')  
    ).reset_index()
    season_rental = season_rental.rename(columns={'cnt_sum': 'Rental Total', 'cnt_mean': 'Rental Avg'})
    season_mapping = {1: 'Spring', 2: 'Summer', 3: 'Fall', 4: 'Winter'}
    season_rental['season'] = season_rental['season'].replace(season_mapping)
    return season_rental

# Helper function for rental type analysis
def year_rental_type(data):
    year_rental = data.groupby('yr').agg(
        cas_sum=('casual', 'sum'),  
        reg_sum=('registered', 'sum')  
    ).reset_index()
    year_rental = year_rental.rename(columns={'cas_sum': 'Total Casual', 'reg_sum': 'Total Registered'})
    year_mapping = {0: '2011', 1:'2012'}
    year_rental['yr'] = year_rental['yr'].replace(year_mapping)
    year_rental['Total'] = year_rental['Total Casual'] + year_rental['Total Registered']
    return year_rental

def month_rental_type(data):
    month_rentaler = data.groupby(['mnth', 'yr']).agg(
        cas_sum=('casual', 'sum'),  
        reg_sum=('registered', 'sum')  
    ).reset_index()
    month_rentaler = month_rentaler.rename(columns={'cas_sum': 'Total Casual', 'reg_sum': 'Total Registered'})
    month_mapping = {
        1: "Januari",
        2: "Februari",
        3: "Maret",
        4: "April",
        5: "Mei",
        6: "Juni",
        7: "Juli",
        8: "Agustus",
        9: "September",
        10: "Oktober",
        11: "November",
        12: "Desember"
    }
    month_rentaler['mnth'] = month_rentaler['mnth'].replace(month_mapping)
    month_rentaler['Total'] = month_rentaler['Total Casual'] + month_rentaler['Total Registered']
    year_mapping = {0: '2011', 1:'2012'}
    month_rental_2011 = month_rentaler[month_rentaler['yr'] == 0].reset_index(drop=True)
    month_rental_2012 = month_rentaler[month_rentaler['yr'] == 1].reset_index(drop=True)
    month_rental_2011['yr'] = month_rental_2011['yr'].replace(year_mapping)
    month_rental_2012['yr'] = month_rental_2012['yr'].replace(year_mapping)
    return month_rental_2011, month_rental_2012

def season_rental_type(data):
    season_rentaler = data_day.groupby(['season', 'yr']).agg(
    cas_sum=('casual', 'sum'),  
    reg_sum=('registered', 'sum')  
    ).reset_index()
    season_rentaler = season_rentaler.rename(columns={'cas_sum': 'Total Casual', 'reg_sum': 'Total Registered'})
    season_mapping = {1: 'Spring', 2: 'Summer', 3: 'Fall', 4: 'Winter'}
    season_rentaler['season'] = season_rentaler['season'].replace(season_mapping)
    year_mapping = {0: '2011', 1:'2012'}
    season_rentaler['yr'] = season_rentaler['yr'].replace(year_mapping)
    season_rentaler['Total'] = season_rentaler['Total Casual'] + season_rentaler['Total Registered']
    season_rental_2011 = season_rentaler[season_rentaler['yr'] == '2011'].reset_index(drop=True)
    season_rental_2012 = season_rentaler[season_rentaler['yr'] == '2012'].reset_index(drop=True)
    return season_rental_2011, season_rental_2012

# Helper function for per-hour rental data
def hourly_rental(data):
    hourly_data = data.groupby('hr')['cnt'].mean().reset_index()
    return hourly_data

# Helper function for month 
def month_analysis(data):
    month_rental = data.groupby('mnth').agg(
    cnt_sum=('cnt', 'sum'),  
    cnt_mean=('cnt', 'mean')  
    ).reset_index()
    month_rental = month_rental.rename(columns={'cnt_sum': 'Rental Total', 'cnt_mean': 'Rental Avg'})
    month_mapping = {
        1: "Januari",
        2: "Februari",
        3: "Maret",
        4: "April",
        5: "Mei",
        6: "Juni",
        7: "Juli",
        8: "Agustus",
        9: "September",
        10: "Oktober",
        11: "November",
        12: "Desember"
    }

    month_rental['mnth'] = month_rental['mnth'].replace(month_mapping)
    return month_rental

###################################### LAYOUT #####################################
# Streamlit layout
st.title("Bike Rental Analysis Dashboard")

# Sidebar options for major sections
option = st.sidebar.selectbox(
    "Choose Analysis Type",
    ("Seasonal Analysis", "Hourly Analysis", "Monthly Analysis", "Rentaler Type")
)

# Seasonal Analysis
if option == "Seasonal Analysis":
    st.subheader("Data Of total Rental for 4 seasons")
    season_data_working = season_rental_workingday(data_day)
    season_data_working
    sns.barplot(data=season_data_working, x='workingday', y='cnt')
    plt.title('Compare of total Rental between workingday and weekday')
    plt.xticks(rotation=90)
    st.pyplot(plt)
    st.subheader("Rentaler Type Comparison by Season")
    season_data = season_rental(data_day)
    season_data
    labels = season_data['season'] 
    sizes = season_data['Rental Total'] 
    fig, ax = plt.subplots()
    ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90, colors=['#ff9999','#66b3ff','#99ff99','#ffcc99'])
    ax.set_title('Compare OF total rental in 4 season')
    ax.axis('equal')  
    st.pyplot(fig)

# Hourly Analysis
elif option == "Hourly Analysis":
    st.subheader("Data per Jam")
    hourly_data = hourly_rental(data_hour)  
    hourly_data
    plt.figure(figsize=(15, 5))
    sns.lineplot(
        x=hourly_data["hr"],
        y=hourly_data["cnt"],
        marker='o'
    )
    plt.title("Average Rental for 1 Hour", loc="center", fontsize=20)
    plt.xticks(fontsize=10)
    plt.yticks(fontsize=10)
    
    st.pyplot(plt)

# Monthly Analysis
elif option == "Monthly Analysis":
    st.subheader("Data Of Rental for 2 years(2011 and 2012)")
    monthly_rentaler = month_analysis(data_day)
    monthly_rentaler
    sns.barplot(data=monthly_rentaler, x='mnth', y='Rental Total')
    plt.title('Compare Total Rental for 2 years (in Month)')
    plt.xticks(rotation=90)
    st.pyplot(plt)
    
    sns.barplot(data=monthly_rentaler, x='mnth', y='Rental Avg')
    plt.title('Compare Average Rental for 2 years (in Month)')
    plt.xticks(rotation=90)
    st.pyplot(plt)

# Rentaler Type Analysis
elif option == "Rentaler Type":
    option_rentaler = st.sidebar.selectbox(
    "Choose Analysis Rentaler Type",
    ("Casual Vs Registered", 'Rentaler Type Month', 'Rentaler Season Analysis'))
    if option_rentaler == 'Casual Vs Registered':
        st.subheader("Rentaler Type Data")
        rental_type_data = year_rental_type(data_day)
        rental_type_data
        plt.bar(rental_type_data['yr'], rental_type_data['Total Casual'], label='Casual')
        plt.bar(rental_type_data['yr'], rental_type_data['Total Registered'], 
                bottom=rental_type_data['Total Casual'], label='Registered')  
        plt.xlabel('Year')
        plt.ylabel('Count')
        plt.title('Compare Rentaler Type in 2011 and 2012')
        plt.legend()  
        st.pyplot(plt)

        
    elif option_rentaler == 'Rentaler Type Month':
        year_rental = st.sidebar.selectbox('Choose year',('2011','2012'))
        if year_rental == '2011':
            st.subheader('Rentaler Per Month Analysis in 2011')
            month_rental_2011 = month_rental_type(data_day)[0]
            month_rental_2011
            plt.bar(month_rental_2011['mnth'], month_rental_2011['Total Casual'], label='Casual')
            plt.bar(month_rental_2011['mnth'], month_rental_2011['Total Registered'], 
                    bottom=month_rental_2011['Total Casual'], label='Registered')

            plt.xlabel('Month')
            plt.ylabel('Count')
            plt.title('Compare User Type per Month in 2011')
            plt.xticks(rotation=90)
            plt.legend()

            st.pyplot(plt)
        elif year_rental == '2012':
            st.subheader('Rentaler per Month Analysis 2012')
            month_rental_2012 = month_rental_type(data_day)[1]
            month_rental_2012
            plt.bar(month_rental_2012['mnth'], month_rental_2012['Total Casual'], label='Casual')
            plt.bar(month_rental_2012['mnth'], month_rental_2012['Total Registered'], 
                    bottom=month_rental_2012['Total Casual'], label='Registered') 
            plt.xlabel('Month')
            plt.ylabel('Count')
            plt.title('Compare User Type per Month in 2012')
            plt.xticks(rotation=90)
            plt.legend()  
            st.pyplot(plt)
    
    elif option_rentaler == 'Rentaler Season Analysis':
        season_rental = st.sidebar.selectbox('Choose year',('2011','2012'))
        if season_rental == '2011':
            st.subheader('Rentaler Season Analysis in 2011')
            season_rental_2011 = season_rental_type(data_day)[0]
            season_rental_2011
            plt.bar(season_rental_2011['season'], season_rental_2011['Total Casual'], label='Casual')
            plt.bar(season_rental_2011['season'], season_rental_2011['Total Registered'], 
                    bottom=season_rental_2011['Total Casual'], label='Registered')  
            plt.xlabel('Season')
            plt.ylabel('Count')
            plt.title('Compare User Type per Season in 2012')
            plt.xticks(rotation=90)
            plt.legend()  
            plt.show()
            st.pyplot(plt)
        elif season_rental == '2012':
            st.subheader('Rentaler Season Analysis in 2012')
            season_rental_2012 = season_rental_type(data_day)[1]
            season_rental_2012
            plt.bar(season_rental_2012['season'], season_rental_2012['Total Casual'], label='Casual')
            plt.bar(season_rental_2012['season'], season_rental_2012['Total Registered'], 
                    bottom=season_rental_2012['Total Casual'], label='Registered')  
            plt.xlabel('Season')
            plt.ylabel('Count')
            plt.title('Compare User Type per Season in 2012')
            plt.xticks(rotation=90)
            plt.legend()  
            plt.show()
            st.pyplot(plt)

if __name__ == "__main__":
    pass

