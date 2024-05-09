import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import datetime
from pathlib import Path
import plotly.graph_objects as go
import streamlit as st
from streamlit_option_menu import option_menu
from streamlit_extras.add_vertical_space import add_vertical_space
from streamlit_extras.stylable_container import stylable_container  #
from streamlit_gsheets import GSheetsConnection
from sklearn import metrics

THIS_DIR = Path(__file__).parent
ASSETS = THIS_DIR / "assets"
LOGO = ASSETS / "savila_games_logo.png"
#print(LOGO)

st.set_page_config(
        page_title='MFI 0054 FINAL PROJECT', # agregamos el nombre de la pagina, este se ve en el browser
        page_icon='📈' # se agrega el favicon, tambien este se ve en el browser
    )

if 'user_name' not in st.session_state:
    st.session_state['user_name'] = ''

if 'password' not in st.session_state:
    st.session_state['password'] = ''

if 'group' not in st.session_state:
    st.session_state['group'] = ''

house_test_url = 'https://raw.githubusercontent.com/ceche1212/test_github/main/Houseprice_test_with_values.csv?token=GHSAT0AAAAAACSASG6VX2YRJSRUKP33R4FWZR3LDGQ'
credit_risk_test_url = 'https://raw.githubusercontent.com/ceche1212/test_github/main/test_credit_default_with_output.csv'
time_series_test_url = 'https://raw.githubusercontent.com/ceche1212/test_github/main/Test_Hourly_Energy_Consumption_MW.csv'

login = None
df_n_cols = 6

conn = st.connection("gsheets", type=GSheetsConnection)
users_existing_data =  conn.read(worksheet="users", usecols=list(range(5)), ttl=1)
users_existing_data = users_existing_data.dropna(how="all")
users_existing_data.index = users_existing_data['email']

gs_user_db = users_existing_data.T.to_dict()

# emojis are obtained from bootstrap icons https://icons.getbootstrap.com/
with st.sidebar:
    st.image("./savila_games_logo.png")
    selected = option_menu(
        menu_title='MFI 0054',
        options= ['Login','Rankings','My group Submissions','Submit PART I','Submit PART II','Submit PART III'],
        icons=['bi bi-person-fill-lock', '123','bi bi-database','bi bi-graph-up-arrow','bi bi-graph-up-arrow','bi bi-graph-up-arrow'], menu_icon="cast"
    )

    add_vertical_space(1)

    if selected == 'Login':

        user_name = st.text_input('User email', placeholder = 'username@ieseg.fr')
    #st.caption('Please enter your IESEG email address')
        password =  st.text_input('Password', placeholder = '12345678',type="password")
        login = st.button("Login", type="primary")
    add_vertical_space(1)

#---------------------------------------------------------------------------------------------------------------------------------
#                                              
#
#---------------------------------------------------------------------------------------------------------------------------------  

if selected == 'Login':
   
   st.header('Welcome to your Final group project Challenge')
   st.write('Please proceed to login using the left side panel')
   st.write('⚠️ Please note that access to subsequent sections is restricted to logged-in users.')
   st.divider()
   st.subheader('Rules:')
   with st.expander('Rules',expanded=True):
      st.markdown("- This app lets you submit your project calculations.")
      st.markdown("- Everyone on your team can submit as many times as they like.")
      st.markdown("- For each one of the parts whichever team comes up with the best result for a given part gets the top grade for that part.")
      st.markdown("- In case there is a tie. The team that submitted first the solution will get the higher grade.")  
           
                
   st.subheader('How to use the app:')
   with st.expander('How to use the app',expanded=True):
      st.markdown("- Check out the **Ranking** 🥇 tab to see where your team stands for each one of the parts.")   
      st.markdown("- Click on **My Group Submissions** 🗃️ to see the history of all the solutions that your team has submitted.")
      st.markdown("- Hit **Part I, Part II or Part III** 📊 to drop in a new solution.")
      st.markdown("- Every time you submit, the app checks if it's all good and pops out some feedback in case you had a bug.") 
      st.markdown("- Keep trying new things and submitting - there's no limit")          
   add_vertical_space(1)
   st.image('https://media1.tenor.com/m/YoFWnXe4V3kAAAAC/may-the-odds-be-ever-in-your-favor-may-the-odds-hunger-games.gif',
            use_column_width = 'always' )

if login:
    if user_name not in gs_user_db.keys():
        st.error('Username not registered')
    else:
        real_password = gs_user_db[user_name]['password']
        if password.lower() != real_password:
            st.error('Sorry wrong password')
        else:
            user_first_name = gs_user_db[user_name]['name']
            group = gs_user_db[user_name]['group']
            st.session_state['user_name'] = user_name
            st.session_state['password'] = real_password
            st.session_state['group'] =  group
            with st.sidebar:
                st.success(f'{user_first_name} from group ({group}) succesfully log-in', icon="✅")

with st.sidebar:
    if st.session_state['user_name'] != '':
        st.write(f"User: {st.session_state['user_name']} ")
        st.write(f"Group: {st.session_state['group']} ")
        logout = st.button('Logout')
        if logout:
            st.session_state['user_name'] = ''
            st.session_state['password'] = ''
            st.session_state['group'] = ''
            st.session_state['Schedule'] = ''
            st.session_state['valid'] = ''
            st.session_state['resource_schedule'] = ''
            st.rerun()
    else:
        st.write(f"User: Not logged in ")

#---------------------------------------------------------------------------------------------------------------------------------
#                                              
#
#---------------------------------------------------------------------------------------------------------------------------------  

if selected == "Rankings":
    st.header('Rankings')
    
    if st.session_state['user_name'] == '':
        st.warning('Please log in to be able to see The rankings')
    else:
        st.write('The tabs below shows the rankings for each one of the parts of the project')

        rank_df = conn.read(worksheet="log", usecols=list(range(df_n_cols)), ttl=1).dropna(how="all")
        GROUPS = list(rank_df['group'].unique())
        default_time = pd.to_datetime('01/01/1901, 00:00:00',format="%d/%m/%Y, %H:%M:%S")

        tab1, tab2, tab3 = st.tabs(["Part I", "Part II", "Part III"])

        with tab1:

            st.header("Part I")

            rank_part_1 = rank_df[rank_df['type'] == 'part 1']
            ranking_list_1 = []
            for gr in GROUPS:

                mini_df_1 = rank_part_1[rank_part_1['group'] == gr]
                if len(mini_df_1) == 0:
                    row = {'group':gr,'MAPE':1,'time':default_time}
                    ranking_list_1.append(row)
                    continue
                else:
                    best_idx_1 = np.argmin(mini_df_1['score'])
                    best_value_1 = mini_df_1.iat[best_idx_1,-1]
                    best_time_1 = pd.to_datetime(mini_df_1.iat[best_idx_1,2],format="%d/%m/%Y, %H:%M:%S")
                    row = {'group':gr,'MAPE':best_value_1,'time':best_time_1}
                    ranking_list_1.append(row)
            ranking_df_1 = pd.DataFrame(ranking_list_1).sort_values(by = ['MAPE','time'])
            ranking_df_1 = ranking_df_1.reset_index(drop=True)
            ranking_df_1.iat[0,0] = ranking_df_1.iat[0,0] + "   🥇"
            ranking_df_1.iat[1,0] = ranking_df_1.iat[1,0] + "   🥈"
            ranking_df_1.iat[2,0] = ranking_df_1.iat[2,0] + "   🥉"
            st.dataframe(ranking_df_1,use_container_width=True,hide_index=True)

        with tab2:

            st.header("Part II")

            rank_part_2 = rank_df[rank_df['type'] == 'part 2']
            ranking_list_2 = []
            for gr in GROUPS:

                mini_df_2 = rank_part_2[rank_part_2['group'] == gr]
                if len(mini_df_2) == 0:
                    row = {'group':gr,'Accuracy':0,'time':default_time}
                    ranking_list_2.append(row)
                    continue
                else:
                    best_idx_2 = np.argmax(mini_df_2['score'])
                    best_value_2 = mini_df_2.iat[best_idx_2,-1]
                    best_time_2 = pd.to_datetime(mini_df_2.iat[best_idx_2,2],format="%d/%m/%Y, %H:%M:%S")
                    row = {'group':gr,'Accuracy':best_value_2,'time':best_time_2}
                    ranking_list_2.append(row)
            ranking_df_2 = pd.DataFrame(ranking_list_2).sort_values(by = ['Accuracy','time'],ascending=[False, True])
            ranking_df_2 = ranking_df_2.reset_index(drop=True)
            ranking_df_2.iat[0,0] = ranking_df_2.iat[0,0] + "   🥇"
            ranking_df_2.iat[1,0] = ranking_df_2.iat[1,0] + "   🥈"
            ranking_df_2.iat[2,0] = ranking_df_2.iat[2,0] + "   🥉"
            st.dataframe(ranking_df_2,use_container_width=True,hide_index=True)

        with tab3:

            st.header("Part III")

            rank_part_3 = rank_df[rank_df['type'] == 'part 3']
            ranking_list_3 = []
            for gr in GROUPS:

                mini_df_3 = rank_part_3[rank_part_3['group'] == gr]
                if len(mini_df_3) == 0:
                    row = {'group':gr,'MAPE':1,'time':default_time}
                    ranking_list_3.append(row)
                    continue
                else:
                    best_idx_3 = np.argmin(mini_df_3['score'])
                    best_value_3 = mini_df_3.iat[best_idx_3,-1]
                    best_time_3 = pd.to_datetime(mini_df_3.iat[best_idx_3,2],format="%d/%m/%Y, %H:%M:%S")
                    row = {'group':gr,'MAPE':best_value_3,'time':best_time_3}
                    ranking_list_3.append(row)
            ranking_df_3 = pd.DataFrame(ranking_list_3).sort_values(by = ['MAPE','time'])
            ranking_df_3 = ranking_df_3.reset_index(drop=True)
            ranking_df_3.iat[0,0] = ranking_df_3.iat[0,0] + "   🥇"
            ranking_df_3.iat[1,0] = ranking_df_3.iat[1,0] + "   🥈"
            ranking_df_3.iat[2,0] = ranking_df_3.iat[2,0] + "   🥉"
            st.dataframe(ranking_df_3,use_container_width=True,hide_index=True)

#---------------------------------------------------------------------------------------------------------------------------------
#                                              
#
#---------------------------------------------------------------------------------------------------------------------------------            

if selected == 'My group Submissions':
    st.header('My Group Submissions')
    
    if st.session_state['user_name'] == '':
        st.warning('Please log in to be able to see your submission history')
    else:
        st.write(f'The table below shows you the submission history of your group: **{st.session_state["group"]}**')
        group_log_df = conn.read(worksheet="log", usecols=list(range(df_n_cols)), ttl=1).dropna(how="all")
        group_log_df = group_log_df[group_log_df['group'] == st.session_state['group']]
        group_log_df = group_log_df[['user','time','type','metric','score']]
        
       
        st.subheader('Submissions History:')
        st.dataframe(group_log_df,use_container_width=True,hide_index=True)

#---------------------------------------------------------------------------------------------------------------------------------
#                                              
#
#---------------------------------------------------------------------------------------------------------------------------------  

if selected == 'Submit PART I':

    st.markdown("""
        <style>
        div[data-testid="stMetric"] {
            background-color: #EEEEEE;
            border: 2px solid #CCCCCC;
            padding: 5% 5% 5% 10%;
            border-radius: 5px;
            overflow-wrap: break-word;
        }
        </style>
        """
        , unsafe_allow_html=True)

    st.header('Submit Predictions for Part I')

    if st.session_state['user_name'] == '':
        st.warning('Please log in to be able to submit your project solution')
    else:
        house_y = pd.read_csv(house_test_url,index_col=0)['Appraised Value']
        n_house = len(house_y)

        house_file = st.file_uploader("Upload your predictions file",type=['csv'])
        st.caption(f"Your file must have {n_house} rows and at least one column named \'predictions\' with your predictions")
        if house_file is not None:

            submit_house_pred = st.button('submit',type="primary",key="submit_house")

            if submit_house_pred:

                house_df = pd.read_csv(house_file)

                if 'predictions' not in house_df.columns.to_list():
                    st.error('Sorry there is no \"predictions\" column in your file', icon="🚨")
                elif len(house_df) != n_house:
                    st.error(f'Sorry the number of rows of your file ({len(house_df)}) does not match the expected lenght of {n_house}', icon="🚨")
                else:
                    with st.spinner('Uploading solution to database'):
                        house_predictions = house_df['predictions']

                        timestamp = datetime.datetime.now()
                        timestamp = timestamp.strftime("%d/%m/%Y, %H:%M:%S")
                        st.write(f'Submitted on: {timestamp}')

                        RMSE_house = np.sqrt(metrics.mean_squared_error(house_predictions,house_y))
                        MAPE_house = metrics.mean_absolute_percentage_error(house_predictions,house_y)

                        columns_part_1 = st.columns(2)

                        with  columns_part_1[0]:
                            st.metric("RMSE",f"{RMSE_house:.2f}")
                        
                        with columns_part_1[1]:
                            st.metric("MAPE",f"{MAPE_house:.3f}")

                        #st.write(f"RMSE = {RMSE_house:.2f}")
                        #st.write(f"MAPE = {MAPE_house:.3f}")

                        solution_part_1_dict = dict()
                        solution_part_1_dict['user'] = st.session_state['user_name']
                        solution_part_1_dict['group'] = st.session_state['group']
                        solution_part_1_dict['time'] = timestamp
                        solution_part_1_dict['type'] = 'part 1'
                        solution_part_1_dict['metric'] = 'MAPE'
                        solution_part_1_dict['score'] = MAPE_house

                        logs_df_1 = conn.read(worksheet="log", usecols=list(range(df_n_cols)), ttl=1).dropna(how="all")
                        solution_1 = pd.DataFrame([solution_part_1_dict])
                        updated_log_1 = pd.concat([logs_df_1,solution_1],ignore_index=True)
                        conn.update(worksheet="log",data = updated_log_1)
                        st.success(f'Your solution was uploaded on: {timestamp}',icon="✅")
                        st.balloons()


#---------------------------------------------------------------------------------------------------------------------------------
#                                              
#
#---------------------------------------------------------------------------------------------------------------------------------  

if selected == 'Submit PART II':

    st.markdown("""
        <style>
        div[data-testid="stMetric"] {
            background-color: #EEEEEE;
            border: 2px solid #CCCCCC;
            padding: 5% 5% 5% 10%;
            border-radius: 5px;
            overflow-wrap: break-word;
        }
        </style>
        """
        , unsafe_allow_html=True)

    st.header('Submit Predictions for Part II')

    if st.session_state['user_name'] == '':
        st.warning('Please log in to be able to submit your project solution')
    else:   
        credit_y = pd.read_csv(credit_risk_test_url,index_col=0)['default']
        n_credit = len(credit_y)

        credit_file = st.file_uploader("Upload your predictions file",type=['csv'])
        st.caption(f"Your file must have {n_credit} rows and at least one column named \'predictions\' with your predictions")
        if credit_file is not None:

            submit_credit_pred = st.button('submit',type="primary",key="submit_credit")

            if submit_credit_pred:

                credit_df = pd.read_csv(credit_file) 

                if 'predictions' not in credit_df.columns.to_list():
                    st.error('Sorry there is no \"predictions\" column in your file', icon="🚨")
                elif len(credit_df) != n_credit:
                    st.error(f'Sorry the number of rows of your file ({len(credit_df)}) does not match the expected lenght of {n_credit}', icon="🚨")
                else:
                    with st.spinner('Uploading solution to database'):
                        credit_predictions = credit_df['predictions']

                        timestamp = datetime.datetime.now()
                        timestamp = timestamp.strftime("%d/%m/%Y, %H:%M:%S")
                        st.write(f'Submitted on: {timestamp}')

                        ACC = metrics.accuracy_score(credit_y,credit_predictions)
                        st.metric("ACCURACY",f"{ACC:.3f}")

                        solution_part_2_dict = dict()
                        solution_part_2_dict['user'] = st.session_state['user_name']
                        solution_part_2_dict['group'] = st.session_state['group']
                        solution_part_2_dict['time'] = timestamp
                        solution_part_2_dict['type'] = 'part 2'
                        solution_part_2_dict['metric'] = 'Accuracy'
                        solution_part_2_dict['score'] = ACC

                        logs_df_2 = conn.read(worksheet="log", usecols=list(range(df_n_cols)), ttl=1).dropna(how="all")
                        solution_2 = pd.DataFrame([solution_part_2_dict])
                        updated_log_2 = pd.concat([logs_df_2,solution_2],ignore_index=True)
                        conn.update(worksheet="log",data = updated_log_2)
                        st.success(f'Your solution was uploaded on: {timestamp}',icon="✅")
                        st.balloons()

#---------------------------------------------------------------------------------------------------------------------------------
#                                              
#
#---------------------------------------------------------------------------------------------------------------------------------  

if selected == 'Submit PART III':

    # style of the the st.metric cards
    st.markdown("""
        <style>
        div[data-testid="stMetric"] {
            background-color: #EEEEEE;
            border: 2px solid #CCCCCC;
            padding: 5% 5% 5% 10%;
            border-radius: 5px;
            overflow-wrap: break-word;
        }
        </style>
        """
        , unsafe_allow_html=True)

    st.header('Submit Predictions for Part III')

    if st.session_state['user_name'] == '':
        st.warning('Please log in to be able to submit your project solution')
    else:
        energy_y = pd.read_csv(time_series_test_url,index_col=0)['Hourly_Energy_Consumption_MW']

        n_energy = len(energy_y)

        energy_file = st.file_uploader("Upload your predictions file",type=['csv'])
        st.caption(f"Your file must have {n_energy} rows and at least one column named \'predictions\' with your predictions")
        if energy_file is not None:

            submit_energy_pred = st.button('submit',type="primary",key="submit_energy")

            if submit_energy_pred:

                energy_df = pd.read_csv(energy_file)

                if 'predictions' not in energy_df.columns.to_list():
                    st.error('Sorry there is no \"predictions\" column in your file', icon="🚨")
                elif len(energy_df) != n_energy:
                    st.error(f'Sorry the number of rows of your file ({len(energy_df)}) does not match the expected lenght of {n_energy}', icon="🚨")
                else:
                    with st.spinner('Uploading solution to database'):
                        energy_predictions = energy_df['predictions']

                        timestamp = datetime.datetime.now()
                        timestamp = timestamp.strftime("%d/%m/%Y, %H:%M:%S")
                        st.write(f'Submitted on: {timestamp}')

                        RMSE_energy = np.sqrt(metrics.mean_squared_error(energy_predictions,energy_y))
                        MAPE_energy = metrics.mean_absolute_percentage_error(energy_predictions,energy_y)

                        columns_part_3 = st.columns(2)

                        with  columns_part_3[0]:
                            st.metric("RMSE",f"{RMSE_energy:.2f}")
                        
                        with columns_part_3[1]:
                            st.metric("MAPE",f"{MAPE_energy:.3f}")

                        solution_part_3_dict = dict()
                        solution_part_3_dict['user'] = st.session_state['user_name']
                        solution_part_3_dict['group'] = st.session_state['group']
                        solution_part_3_dict['time'] = timestamp
                        solution_part_3_dict['type'] = 'part 3'
                        solution_part_3_dict['metric'] = 'MAPE'
                        solution_part_3_dict['score'] = MAPE_energy

                        logs_df_3 = conn.read(worksheet="log", usecols=list(range(df_n_cols)), ttl=1).dropna(how="all")
                        solution_3 = pd.DataFrame([solution_part_3_dict])
                        updated_log_3 = pd.concat([logs_df_3,solution_3],ignore_index=True)
                        conn.update(worksheet="log",data = updated_log_3)
                        st.success(f'Your solution was uploaded on: {timestamp}',icon="✅")
                        st.balloons()

