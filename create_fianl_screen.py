import zipfile
import os
from pathlib import Path
import PySimpleGUI as sg 
from collections import Counter
import mysql.connector
from mysql.connector import Error
from mysql.connector import errorcode
import logging
import inflect
import csv
from pathlib import Path
import os
from functools import reduce
import sqlparse
import tkinter as tk
import inflect
import os, stat
from jproperties import Properties

#########################################################################################################################
            #######logger code##############
def set_logger_object():
    formatter = logging.Formatter("%(levelname)s - %(message)s")
    handler = logging.FileHandler(filename='installer_logging.log')
    handler.setFormatter(formatter)
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    logger.addHandler(handler)
    return logger
logger=set_logger_object()
            #######main_varible###########################
user_selected_database_installer=False
user_selected_application_installer=False
#########################################################################################################################
#############################terms_and_condition_task######################################################
                    #########terms and condition code###########
def terms_and_condition_screen():
    terms_and_condition_screen_window=None
    terms_and_condition_content=read_terms_and_condition_file_content()
    if terms_and_condition_content is not None:
        logger.info("Successfully read content of terms and condition file")
        terms_and_condition_contain_layout = [[sg.Text(terms_and_condition_content,size=(90,15),font='Courier 12',text_color='white')],         
                        [sg.Submit("Accept"), sg.Cancel("Decline")]
                        ]
        terms_and_condition_screen_window= sg.Window('ModeFinServer Pvt Ltd',terms_and_condition_contain_layout,location=(380,200),margins=(10, 10),auto_size_text=True,auto_size_buttons=True,element_justification="center",element_padding=((20,20),(20,20)))
    return terms_and_condition_screen_window

def read_terms_and_condition_file_content():
    terms_and_condition_content=None
    terms_and_condition_file_obj= open(Path("../installer_folder/MFSDBPackage-4.7-DBZIP/MFS_DB_SETUP/demo_file.txt"),"r") 
    terms_and_condition_content=terms_and_condition_file_obj.read()
    return terms_and_condition_content

                    #######validation_of_terms_and_condition_screen###########
def validation_of_terms_and_condition_screen():
    terms_and_condition_event=None
    terms_and_condition_screen_window=terms_and_condition_screen()
    while True:    
        if terms_and_condition_screen_window is not None:
            terms_and_condition_event,terms_and_condition_values = terms_and_condition_screen_window.read() 
            if terms_and_condition_event is None:
                terms_and_condition_screen_window.close() 
                logger.error('user end the installer process while proccessing  the terms and condition screen')
                break 
            elif terms_and_condition_event=="Decline": 
                data=sg.PopupYesNo('Want to end the installation process',title="warning",text_color="red",location=(700,300))
                logger.warning('Want to end the installation process') 
                if (data is None) or (data=="Yes"):
                    logger.info('User Decline for installation')
                    terms_and_condition_screen_window.close() 
                    break                        
            else:
                logger.info('User accept terms and condition for installation')
                terms_and_condition_screen_window.close()
                terms_and_condition_event="Accept"
                break
    return terms_and_condition_event  
###########################################main_screen##################################################################
                ########################home_screen####################
def home_screen_layout():
    installer_type_layout=installer_type_screen()
    database_installer_layout,main_institute_wise_key_list=database_installer_screen()
    application_installer_layout=application_Server_installer_screen()
    master_installer_layout = [[sg.TabGroup([[
                    sg.Tab('Installer Type Screen',installer_type_layout,key='installer_type',element_justification="center"),
                    sg.Tab('Database Installer Screen ',database_installer_layout,key='main_database_installer',element_justification="center",disabled=False,visible=False),
                    sg.Tab('Application Installer Screen',application_installer_layout,key='main_application_installer',element_justification="center",disabled=False,visible=False),
                    ]],enable_events=False)]]    
    master_installer_window = sg.Window('ModeFinServer Pvt Ltd',master_installer_layout,location=(380,200),size=(800,400),auto_size_text=True,auto_size_buttons=True,element_justification="center",no_titlebar=False, resizable=True).Finalize()
    return master_installer_window,main_institute_wise_key_list 

                #########installer_type#####################
def installer_type_screen():
    installer_type_layout =[
                [sg.Text('  Installer  Type ',size=(18, 2),font='Courier 12',text_color='white')],
                [sg.Radio('Database Installer',size=(22, 2), group_id='mygroup', key='database_installer',font='Courier 12',text_color='white'),
                 sg.Radio('Application Installer',group_id='mygroup',size=(22, 2), key='application_installer',font='Courier 12',text_color='white')],
                [sg.Button('Next',key="installer_type_button")]]
    return installer_type_layout

                ##########database_installer################
def database_installer_screen():
    radio_choices_for_database_tools=["MYSQL","ORACLE","MSSQL","POSTGRESS"]
    database_tools_layout =[
                [sg.Text('Database Tool Type',size=(18, 2),font='Courier 12',text_color='white',justification="center")],
                [sg.Radio(text,1,size=(10, 2),key=text,font='Courier 12',text_color='white') for text in radio_choices_for_database_tools],
                [sg.Button("Next",key="database_tool_event")]]
    data_base_creditional_layout =[[sg.Text('Enter database creditional',size=(60,2),font='Courier 12',text_color='white',justification="center")],  
            [sg.Text('Enter Database Name', size=(40,2),font='Courier 12',text_color='white'), sg.InputText(key="db_name")],
            [sg.Text('Enter Host Name', size=(40,2),font='Courier 12',text_color='white'), sg.InputText(key="localhost")],
            [sg.Text('Enter Valid Username', size=(40,2),font='Courier 12',text_color='white'), sg.InputText(key="username")],
            [sg.Text('Enter Valid Password', size=(40,2),font='Courier 12',text_color='white'), sg.InputText(password_char='*',key="password")],      
            [sg.Button("Next",key="database_creditional_event")]]
    major_list=[]       
    no_of_institute_list=read_no_of_institute_file()
    main_institute_wise_key_list=[]
    for institute_id in no_of_institute_list: 
        sub_institute_wise_key_list=[]
        bank_name,location_name,folder_name,language_list_key,button_obj=prepare_key_words(institute_id)
        sub_institute_wise_key_list=[institute_id,bank_name,location_name,folder_name,language_list_key,button_obj]
        layout_name="%s_layout_experiment"%institute_id
        main_institute_wise_key_list.append(sub_institute_wise_key_list)
        layout_name=institution_screen(bank_name,location_name,folder_name,language_list_key,institute_id,button_obj)
        dyanemi_screen=sg.Tab(institute_id,layout_name,key=institute_id,element_justification="center",disabled=True)
        major_list.append(dyanemi_screen)
    database_installer_layout = [[sg.TabGroup([[
                sg.Tab('Database Tool',database_tools_layout,key='database_tool',element_justification="center"),
                sg.Tab('Database Creditional',data_base_creditional_layout,key='database_creditional',element_justification="center",disabled=True),
                *[data for data in major_list]]])]]    
    return database_installer_layout,main_institute_wise_key_list
def read_no_of_institute_file():
    no_of_institute_list=[]
    no_of_institute_obj= open(Path("../installer_folder/MFSDBPackage-4.7-DBZIP/MFS_DB_SETUP/number_of_institute.txt"),"r") 
    no_of_institute_data=(no_of_institute_obj.read())
    no_of_institute_data=no_of_institute_data.strip()
    for inst_data in no_of_institute_data.split("\n"):
        if inst_data.find("institute_id")!=-1:
            no_of_institute_list.append(inst_data.split("=")[1])
    return no_of_institute_list

def prepare_key_words(institute_id):
    bank_name="bank_name"+'_'+institute_id
    location_name="location_name"+'_'+institute_id
    folder_name="folder_name"+'_'+institute_id
    language_list_key="language_list_key"+"-"+institute_id
    button_obj="button"+"-"+institute_id
    return (bank_name,location_name,folder_name,language_list_key,button_obj)

def institution_screen(bank_name,location_name,folder_name,language_list_key,words,button_obj):
    language_list=read_language_file()
    langauge_str=','  
    langauge_str=langauge_str.join(language_list)
    language_text='Select language from %s'%(langauge_str)
    inst_message="institutional details for %s"%(words)
    each_institution_wise_layout =[[sg.Text(inst_message,size=(40,2),font='Courier 12',text_color='white',justification="center")],  
            [sg.Text('Enter the Bank Name',size=(40,2),font='Courier 12',text_color='white'), sg.InputText(key=bank_name)],
            [sg.Text('Enter Location of the Institute',size=(40,2),font='Courier 12',text_color='white'), sg.InputText(key=location_name)],
            [sg.Text('Enter Integration Folder Name',size=(40,2),font='Courier 12',text_color='white'), sg.InputText(key=folder_name)],
            [sg.Text("Select languages for Institute",size=(50,2),font='Courier 12',text_color='white',justification="left"),sg.Listbox(values=language_list, size=(28,3),select_mode='multiple', key=language_list_key)],
            [sg.Submit("Next",key=button_obj)]]
    return each_institution_wise_layout 

def read_language_file():
    language_list=[]
    language_file_obj= open(Path("../installer_folder/MFSDBPackage-4.7-DBZIP/MFS_DB_SETUP/language.txt"),"r") 
    language_data=language_file_obj.read()
    for lang_data in language_data.split("\n"):
        language_list.append(lang_data)
    return (language_list)
                ########################application_Server##############
def application_Server_installer_screen():
    application_Server_type_layout=application_Server_type_screen()
    home_directory_layout=process_home_directory()
    customise_application_input_screen_layout=customise_application_input_screen()
    application_installer_layout = [[sg.TabGroup([[
                sg.Tab('Server Selection',application_Server_type_layout,key='server_selection_screen',element_justification="center"),
                sg.Tab('Home Directory',home_directory_layout,key='directory_screen',element_justification="center",disabled=True),
                sg.Tab('Customize Input',customise_application_input_screen_layout,key='customise_input_screen_for_product',element_justification="center",disabled=True),
                ]])]]    
    return application_installer_layout

def application_Server_type_screen():
    application_Server_type_layout =[
                [sg.Text('Application Server',size=(18, 2),font='Courier 12',text_color='white',justification="center")],
                [sg.Radio('Apache Tomcat',size=(22, 2), group_id='mygroup', key='apache_tomcat',font='Courier 12',text_color='white'),
                 sg.Radio('Oracle WebLogic',group_id='mygroup',size=(22, 2), key='oracle_webLogic',font='Courier 12',text_color='white')],
                [sg.Submit("Next")]]
    return application_Server_type_layout

def process_home_directory():
    home_directory_layout =[[sg.Text("Provide  home directory in following format\n(D:/home/report)",size=(80,3),font='Courier 12',text_color='white',justification="center")],  
        [sg.Text('Enter Home Directory',size=(22,2),font='Courier 12',text_color='white'),sg.InputText(key="home_directory")],      
        [sg.Submit("Next")]]
    return home_directory_layout

def customise_application_input_screen():
    customise_application_input_screen_layout =[[sg.Text('Customise Input Screen',size=(80,3),font='Courier 12',text_color='white',justification="center")],  
        [sg.Text('Enter Database Tool Name', size=(40,2),font='Courier 12',text_color='white'), sg.InputText(key="Database_Tool_Name")],
        [sg.Text('Enter Database Name', size=(40,2),font='Courier 12',text_color='white'), sg.InputText(key="Database_Name")],
        [sg.Text('Enter Database UserName', size=(40,2),font='Courier 12',text_color='white'), sg.InputText(key="Database_User_Name")],
        [sg.Text('Enter Database PassWord', size=(40,2),font='Courier 12',text_color='white'), sg.InputText(key="Database_Pass_Word")],
        [sg.Submit("Submit")]]
    return customise_application_input_screen_layout
                    ######validation_of_installer_type###########                  
def validation_of_installer_type_screen(master_installer_window):
    installer_type_event=None
    installer_type_values=None
    while True:
        installer_type_event,installer_type_values = master_installer_window.read()
        if installer_type_event is None:
            master_installer_window.close() 
            logger.error('user end the installer process while proccessing  the installer type window screen')
            break 
        elif (installer_type_values.get('database_installer')==False) and  (installer_type_values.get('application_installer')==False): 
            sg.popup("Must Select either Database installer or Application installer",title="warning",text_color="red",location=(700,300))        
            logger.warning("Must Select either Database installer or Application installer")
        else:
            if installer_type_values.get('database_installer')==True:
                logger.info("Selected installer type is Database Installer ") 
                installer_type_values="Database Installer"
                user_selected_database_installer=True
            else: 
                logger.info("Selected installer type is Application Installer ")  
                installer_type_values="Application Installer"
                user_selected_application_installer=True
            break 
    return  installer_type_event,installer_type_values
            ######validation_of_db_tool###########
def validation_of_db_tool_screen(master_installer_window):
    db_tool_event=None
    db_tool_values=None
    while True:
        db_tool_event,db_tool_values=master_installer_window.read() 
        if db_tool_event is None:
            master_installer_window.close() 
            logger.error('user end the installer process while proccessing  the database tool window screen')
            break
        elif (db_tool_values.get('MYSQL')==False) and (db_tool_values.get('ORACLE')==False) and (db_tool_values.get('MSSQL')==False) and (db_tool_values.get('POSTGRESS')==False): 
            sg.popup("Must Select one database tool",title="Warning",text_color="red",location=(700,300))        
            logger.warning("Must Select one database tool")
        else:
            if db_tool_values.get('MYSQL')==True:
                db_tool_values='MYSQL'
                logger.info("selected database tool is:MYSQL")
            elif db_tool_values.get('ORACLE')==True:
                db_tool_values='ORACLE'
                logger.info("selected database tool is:ORACLE")
            elif db_tool_values.get('MSSQL')==True:
                db_tool_values='MSSQL'
                logger.info("selected database tool is:MSSQL")
            else:
                db_tool_values='POSTGRESS'
                logger.info("selected database tool is:POSTGRESS")            
            break
    return db_tool_event,db_tool_values
            #########database_creaditional########################
def validation_of_database_creaditional_screen(master_installer_window):
    database_creditional_message=None
    master_installer_window.FindElement('database_creditional').Update(disabled=False)
    master_installer_window.FindElement('database_creditional').select()
    while True:
        data_base_creditional_event,data_base_creditional_values =  master_installer_window.read()
        if data_base_creditional_event is None:
            logger.error('user end the installer process while proccessing  the database creditional screen')
            database_creditional_message="Fail"             
            master_installer_window.close()
            break
        else:
            other_errror_indicator,final_message_for_data_base_connection,data_base_conn_data=data_base_creditional_verification(data_base_creditional_values)
            if (final_message_for_data_base_connection==True) and (bool(data_base_conn_data)==True) and other_errror_indicator==None:
                message="Successfully created and connected to: {}".format(data_base_conn_data.get("db_name")) 
                sg.popup(message,title="Success",text_color="white",location=(600,400)) 
                logger.info(message)
                database_creditional_message="Success"
                break 
            if (other_errror_indicator is not None) and  (final_message_for_data_base_connection==False):
                database_creditional_message="Fail"
                logger.error(other_errror_indicator)
                break
    return database_creditional_message,data_base_conn_data

def data_base_creditional_verification(data_base_creditional_values):
    final_message_for_data_base_connection=False
    other_errror_indicator=None
    data_base_conn_data=None
    if data_base_creditional_values.get("db_name")=='':
        sg.popup("Database name  field cannot be empty",title="warning",text_color="red",location=(600,400))
        logger.warning("Database name cannot be empty")
    elif data_base_creditional_values.get("localhost")=='': 
        sg.popup("Host name field cannot be empty",title="warning",text_color="red",location=(600,400))
        logger.warning("Host name field cannot be empty")
    elif data_base_creditional_values.get("username")=='': 
        sg.popup("Username field cannot be empty",title="warning",text_color="red",location=(600,400))
        logger.warning("Username field cannot be empty")
    elif data_base_creditional_values.get("password")=='': 
        sg.popup("Password field cannot be empty",title="warning",text_color="red",location=(600,400))  
        logger.warning("Password field cannot be empty")
    else:
        data_base_conn_data={"db_name":data_base_creditional_values.get("db_name"),"host_name":data_base_creditional_values.get("localhost"),"user_name":data_base_creditional_values.get("username"),"pass_word":data_base_creditional_values.get("password")}
        access_error,connection_messages,table_existance_single,host_error_single=data_base_main_connection(data_base_conn_data)
        if connection_messages=="Success":
            final_message_for_data_base_connection=True
        elif access_error==True:
            sg.popup("wrong user_id or password Please provide Correct user_id and password",title="warning",text_color="red",location=(600,400)) 
            logger.warning("wrong user_id or password Please provide Correct user_id and password")
        elif table_existance_single==True:
            sg.popup("DataBase already exist Please change the database name",title="Warning",text_color="red",location=(600,400)) 
            logger.warning("DataBase already exist Please change the database name")
        elif host_error_single==True:
            sg.popup("Name or service unknown Please Correct host address",title="Warning",text_color="red",location=(600,400)) 
            logger.warning("Name or service not known Please Correct host address")
        else:
            sg.popup(connection_messages,title="Error",text_color="red",location=(600,400)) 
            other_errror_indicator=connection_messages
            logger.error(connection_messages)
    return other_errror_indicator,final_message_for_data_base_connection,data_base_conn_data

def data_base_main_connection(data_base_conn_data):
    access_error=False
    connection_messages=False
    table_existance="1007 (HY000): Can't create database '%s'; database exists"%data_base_conn_data.get("db_name")
    table_existance_single=False
    host_error="2003: Can't connect to MySQL server"
    host_error_single=False
    try:
        connection = mysql.connector.connect(user=data_base_conn_data.get("user_name"), password=data_base_conn_data.get("pass_word"),host=data_base_conn_data.get("host_name"),auth_plugin='mysql_native_password',autocommit=True)    
        cursor = connection.cursor(buffered=True)
        cursor.execute("CREATE DATABASE %s" %data_base_conn_data.get("db_name"))
        cursor.close()
        connection.close()
        connection = mysql.connector.connect(user=data_base_conn_data.get("user_name"),password=data_base_conn_data.get("pass_word"),host=data_base_conn_data.get("host_name"),database=data_base_conn_data.get("db_name"),auth_plugin='mysql_native_password')
        cursor = connection.cursor(buffered=True)
        connection.commit()
        cursor.close()
        connection.close()
        connection_messages="Success"
    except mysql.connector.Error as err:
        connection_messages=err
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:  
            access_error=True   
            connection_messages=err
        elif str(err)==str(table_existance):
            table_existance_single=True
            connection_messages=err
        elif str(err).find(str(host_error))!=-1: 
            host_error_single=True
            connection_messages=err    
        else: 
            connection_messages=err
    return (access_error,connection_messages,table_existance_single,host_error_single)
            #########validation_of_of_institute_screen########################
def handle_institute_screen_validation_task(master_installer_window,main_institute_wise_key_list):
    institute_screen_validation_message=None
    list_of_dict_for_each_inst=[]
    for individual_inst_data in main_institute_wise_key_list:
        individual_inst_dict=validation_of_institute_screen(master_installer_window,individual_inst_data)
        if bool(individual_inst_dict)==True:
            list_of_dict_for_each_inst.append(individual_inst_dict)
        else:
            logger.error("error raised while getting the institutional data")
            institute_screen_validation_message="Fail"
    if len(list_of_dict_for_each_inst)==len(main_institute_wise_key_list):
        institute_screen_validation_message="Success"
    else:    
        institute_screen_validation_message="Fail"
    return institute_screen_validation_message,list_of_dict_for_each_inst,main_institute_wise_key_list

def validation_of_institute_screen(master_installer_window,individual_inst_data):
    individual_inst_dict={}
    master_installer_window.FindElement(individual_inst_data[0]).Update(disabled=False)
    master_installer_window.FindElement(individual_inst_data[0]).select()
    while True:
        institute_event,institute_values= master_installer_window.read()
        if institute_event is None:
            logger.error('user end the installer process while proccessing  the institute screen')             
            master_installer_window.close()
            break
        elif institute_values.get(individual_inst_data[1])=='':
            sg.popup("Bank name can't be empty provide Bank name",title="warning",text_color="red",location=(600,400)) 
            logger.warning("Bank name can't be empty provide Bank name")
        
        elif institute_values.get(individual_inst_data[2])=='':
            sg.popup("Location name  can't be empty provide Location name",title="warning",text_color="red",location=(600,400)) 
            logger.warning("Location name  can't be empty provide Location name")

        elif institute_values.get(individual_inst_data[3])=='':
            sg.popup("Intergration Folder Name can't be empty\n provide name for Intergration Folder Name",title="warning",text_color="red",location=(600,400)) 
            logger.warning("Intergration Folder Name can't be empty provide name for Intergration Folder Name")    

        elif len(institute_values.get(individual_inst_data[4]))==0:
            sg.popup("must select atleast one language",title="warning",text_color="red",location=(600,400)) 
            logger.warning("must select atleast one language")    
        else:
            individual_inst_dict.update({individual_inst_data[0]:individual_inst_data[0]})
            individual_inst_dict.update({individual_inst_data[1]:institute_values.get(individual_inst_data[1])})
            individual_inst_dict.update({individual_inst_data[2]:institute_values.get(individual_inst_data[2])})
            individual_inst_dict.update({individual_inst_data[3]:institute_values.get(individual_inst_data[3])})
            individual_inst_dict.update({individual_inst_data[4]:institute_values.get(individual_inst_data[4])})
            break
    return individual_inst_dict
######################validation_of_application_realted_method#########################################################################
            ###################validation_of_application_type_screen################################
def validation_of_application_type_screen(master_installer_window):
    application_type_screen_message="Fail"
    selected_application_Server_type=None
    master_installer_window.FindElement('main_application_installer').Update(visible=True) 
    master_installer_window.FindElement('main_application_installer').Update(disabled=False)
    master_installer_window.FindElement('main_application_installer').select()
    while True:
        application_Server_type_event,application_Server_type_values = master_installer_window.read()
        if application_Server_type_event is None:
            logger.info("user close installer screen while selecting application type")
            master_installer_window.close() 
            break 
        elif (application_Server_type_values.get('apache_tomcat')==False) and  (application_Server_type_values.get('oracle_webLogic')==False): 
            sg.popup("Must Select either Apache Tomcat or Oracle WebLogic",title="warning",text_color="red",location=(600,300))        
            logger.warning("Must Select either Apache Tomcat or Oracle WebLogic")
        else:
            if application_Server_type_values.get('apache_tomcat')==True:
                selected_application_Server_type='apache_tomcat'
                logger.info("selected database tool is:Apache Tomcat")
            if application_Server_type_values.get('oracle_webLogic')==True:
                selected_application_Server_type='oracle_webLogic'
                logger.info("selected database tool is:ORACLE WebLogic")
            application_type_screen_message="Success"
            break    
    return  application_type_screen_message,selected_application_Server_type
            ###################validation_of_home_directory_screen################################
def validation_of_application_home_directory_screen(master_installer_window):
    home_directory_path=None
    home_directory_path_message="Fail"
    master_installer_window.FindElement('directory_screen').Update(disabled=False)
    master_installer_window.FindElement('directory_screen').select()
    while True:
        home_directory_event,home_directory_values=master_installer_window.read()
        if home_directory_event is None:
            home_directory_path_message="Fail"
            logger.error("user closing the screen while processing home directory Screen")
            master_installer_window.close() 
            break 
        elif home_directory_values.get("home_directory")=='':
            sg.popup("Home Directory field cannot be empty",title="warning",text_color="red",location=(600,300))
            logger.warning("Home Directory field cannot be empty")
        else:
            try:
                home_directory_path=home_directory_values.get("home_directory")
                # os.chmod(Path(home_directory_path),stat.S_IWRITE)
                home_directory_path_message="Success"
                break 
            except Exception as err:
                file_not_finding_message="The system cannot find the file specified"
                if str(err).find(file_not_finding_message)!=-1:
                    alert_message_for_changin_home_directory="{}'\n'{}".format("The system cannot find the specified Directory","Provide Correct Directory") 
                    logger.warning("alert_message_for_changin_home_directory")
                    logger.warning(alert_message_for_changin_home_directory)
                    sg.popup(alert_message_for_changin_home_directory,title="warning",text_color="red",location=(600,300))
                else:
                    sg.popup(err,title="warning",text_color="red",location=(600,300))
                    logger.error(err)
                    break 
    return  home_directory_path_message,home_directory_path 
            ##############validation_of_customise_application_input_screen##################################
def customise_application_input_screen_verification(master_installer_window):
    customise_input_message="Fail"
    master_installer_window.FindElement('customise_input_screen_for_product').Update(disabled=False)
    master_installer_window.FindElement('customise_input_screen_for_product').select()
    customise_input_dict={}
    while True:
        application_customise_input_event,application_customise_input_values = master_installer_window.read() 
        if application_customise_input_event is None:
            logger.warning("user close the screen while provide the customize data for Properties file")
            customise_input_message="Fail"
            master_installer_window.close() 
            break 
        elif application_customise_input_values.get("Database_Tool_Name")=='':
            sg.popup("Database tool name  field cannot be empty",title="warning",text_color="red",location=(600,350))
            logger.warning("Database tool name  field cannot be empty")
        elif application_customise_input_values.get("Database_Name")=='': 
            sg.popup("Database name  field cannot be empty",title="warning",text_color="red",location=(600,350))
            logger.warning("Database name  field cannot be empty")
        elif application_customise_input_values.get("Database_User_Name")=='': 
            sg.popup("Database user name  field cannot be empty",title="warning",text_color="red",location=(600,350))
            logger.warning("Database user name  field cannot be empty")
        elif application_customise_input_values.get("Database_Pass_Word")=='': 
            sg.popup("Database password field cannot be empty",title="warning",text_color="red",location=(600,350))  
            logger.warning("Database password field cannot be empty")
        else:
            customise_input_dict={"Database_Tool_Name":application_customise_input_values.get("Database_Tool_Name"),"Database_Name":application_customise_input_values.get("Database_Name"),"Database_User_Name":application_customise_input_values.get("Database_User_Name"),"Database_Pass_Word":application_customise_input_values.get("Database_Pass_Word")}
            logger.info(customise_input_dict)
            customise_input_message="Success"
            break
    return customise_input_message,customise_input_dict

#############################################################################################################################
            #################Application Installer task #############################
def process_product_zip_file(home_directory_path):
    zip_extracting_message=None
    try:
        # os.chmod(Path(home_directory_path),stat.S_IWRITE)
        zip_file_path="../installer_folder/mfmbs.zip"
        read_and_extracting_product_zip_file(zip_file_path,home_directory_path)
        message="Successfully Move mfmbs product folder  to following directory: {}".format(str(home_directory_path)) 
        sg.popup(message,title="Success",text_color="white",location=(600,300)) 
        logger.info(message)
        zip_extracting_message="Success"
    except Exception as err:  
        zip_extracting_message=err  
        logger.error("Error while extract the product installer zip file")
        logger.error(zip_extracting_message)
    return zip_extracting_message 

def read_and_extracting_product_zip_file(zip_file_name,home_directory_path):
    with zipfile.ZipFile(Path(zip_file_name), "r") as product_zip_file_obj:
        product_zip_file_obj.extractall(home_directory_path)
def performing_application_server_installation_task(master_installer_window):
    application_installer_message="Fail"
    application_type_screen_message,selected_application_Server_type=validation_of_application_type_screen(master_installer_window)
    if (application_type_screen_message=="Success") and (selected_application_Server_type is not None):
        if selected_application_Server_type=="apache_tomcat":
            apache_tomcat_task=performing_apache_tomcat_task(master_installer_window)
            if apache_tomcat_task=="Success":
                sg.popup("Successfully application installation is Done",title="Success",text_color="white",location=(700,300))
                logger.info("Successfully application installation is Done")
            application_installer_message=apache_tomcat_task
        else:
            performing_oracle_weblogic_task(master_installer_window)
            application_installer_message=application_type_screen_message
    return application_installer_message

def performing_apache_tomcat_task(master_installer_window):
    apache_tomcat_task="Fail"
    home_directory_path_message,home_directory_path=validation_of_application_home_directory_screen(master_installer_window)
    if (home_directory_path_message=="Success") and (home_directory_path is not None):
            zip_extracting_message=process_product_zip_file(home_directory_path)
            if zip_extracting_message=="Success":
                customise_input_message,customise_input_dict=customise_application_input_screen_verification(master_installer_window)
                if (customise_input_message=="Success") and (bool(customise_input_dict)==True):
                    proccessing_properties_file_message=process_propertise_file(customise_input_dict,home_directory_path)
                    if proccessing_properties_file_message=="Success":
                        apache_tomcat_task=proccessing_properties_file_message
            else:
                sg.popup(zip_extracting_message,title="warning",text_color="red",location=(700,300))
                apache_tomcat_task="Fail"    
    return apache_tomcat_task         
      
def performing_oracle_weblogic_task(master_installer_window):
    pass

def process_propertise_file(customise_input_dict,home_directory_path):
    proccessing_properties_file_message=None
    try:
        propertise_obj = Properties()    
        path_of_propertise_file=str(home_directory_path)+"/mfmbs/WEB-INF/classes/mfs.properties"
        propertise_file_data=read_propertise_file(path_of_propertise_file,propertise_obj,customise_input_dict)
        write_propertise_file(path_of_propertise_file,propertise_file_data)
        proccessing_properties_file_message="Success"
    except Exception as err: 
        proccessing_properties_file_message=err
        logger.error(err)
    return proccessing_properties_file_message

def read_propertise_file(path_of_propertise_file,propertise_obj,customise_input_dict):
    with open(path_of_propertise_file, "r") as propertise_file_obj:
        propertise_file_data=propertise_obj.load(propertise_file_obj)
        for key,value in propertise_file_data.items():
            pass
            if key=="Database_Tool_Name":
                propertise_file_data.update({key:customise_input_dict.get(key)})
            elif key=="Database_Name":
                propertise_file_data.update({key:customise_input_dict.get(key)})
            elif key=="Database_User_Name":
                propertise_file_data.update({key:customise_input_dict.get(key)})
            elif key=="Database_Pass_Word":
                propertise_file_data.update({key:customise_input_dict.get(key)})         
            else:
                pass
    propertise_file_obj.close()
    return propertise_file_data 

def write_propertise_file(path_of_propertise_file,propertise_file_data):
    with open(path_of_propertise_file,"w") as propertise_file_obj:
        propertise_file_obj.write(str(propertise_file_data))
    propertise_file_obj.close()
#############################################################################################################################
            #################Database Installer task #############################
def performing_database_installation_task(master_installer_window,main_institute_wise_key_list):
    message_for_processing_of_database_installation_task="Fail"
    master_installer_window.FindElement('main_database_installer').Update(visible=True)
    master_installer_window.FindElement('main_database_installer').Update(disabled=False)
    master_installer_window.FindElement('main_database_installer').select()
    db_tool_event,db_tool_values=validation_of_db_tool_screen(master_installer_window)
    if db_tool_event=="database_tool_event":
        if db_tool_values=="MYSQL":
            message_for_processing_of_mysql_task=performing_mysql_database_installer_task(master_installer_window,main_institute_wise_key_list)
            if message_for_processing_of_mysql_task=="Success":
                logger.info("Successfully database installation is Done")
                sg.popup("Successfully database installation is Done",title="Success",text_color="white",location=(700,300))
            message_for_processing_of_database_installation_task=message_for_processing_of_mysql_task
        elif db_tool_values=="ORACLE":
            sg.popup("ORACLE database is not yet not supported",title="warning",text_color="red",location=(700,300))        
        elif db_tool_values=="MSSQL": 
            sg.popup("MSSQL database is not yet not supported",title="warning",text_color="red",location=(700,300))        
        else: 
            sg.popup("POSTGRESS database is not yet not supported",title="warning",text_color="red",location=(700,300))                 
    return message_for_processing_of_database_installation_task
        ################Extract the Zip File For Database Installer###############
def read_and_extracting_zip_file_for_database_installer():
    db_installer_zip_file_extract_message=None
    try:
        with zipfile.ZipFile(Path("../installer_folder/MFSDBPackage-4.7-DBZIP.zip"), "r") as z:
            z.extractall(os.getcwd())
        logger.info("Successfully extracting the database installer  zip file")    
        db_installer_zip_file_extract_message="Success"    
    except Exception as err:
        logger.error("following error raised %s",err) 
        logger.error("Error while extract the database installer zip file")
        logger.error(db_installer_zip_file_extract_message)
        db_installer_zip_file_extract_message=err
    return db_installer_zip_file_extract_message    
#####################################################################################################################
########################main_method################
def installer_processing():
    try:
        db_installer_zip_file_extract_message=read_and_extracting_zip_file_for_database_installer()
        if db_installer_zip_file_extract_message=="Success":
            terms_and_condition_event=validation_of_terms_and_condition_screen()
            if terms_and_condition_event=="Accept":
                master_installer_window,main_institute_wise_key_list=home_screen_layout()
                installer_type_event,installer_type_values=validation_of_installer_type_screen(master_installer_window)
                if installer_type_event=="installer_type_button":
                    if installer_type_values=="Database Installer":
                        message_for_processing_of_database_installation_task=performing_database_installation_task(master_installer_window,main_institute_wise_key_list)
                        if message_for_processing_of_database_installation_task=="Success":
                            if user_selected_application_installer==False:
                                data=sg.PopupYesNo('Want to start Application installation process',location=(700,300))
                                if (data is None) or (data=="No"):
                                    master_installer_window.close()                   
                                else: 
                                    application_installer_message=application_installer_message=performing_application_server_installation_task(master_installer_window)   
                                    if application_installer_message=="Success":
                                        sg.Popup("Successfully application installation and database installation is done",title="Success",text_color="white",location=(700,300))
                                        master_installer_window.close()

                                    else:
                                        master_installer_window.close()   
                            else:
                                master_installer_window.close()
                        else:
                            if message_for_processing_of_database_installation_task=="Fail":
                                master_installer_window.close()      
                    else:
                        application_installer_message=performing_application_server_installation_task(master_installer_window)
                        if application_installer_message=="Success":
                            if user_selected_database_installer==False:
                                data=sg.PopupYesNo('Want to start database installation process',location=(700,300))
                                if (data is None) or (data=="No"):
                                    master_installer_window.close()                   
                                else:
                                    mysql_database_activty_message=performing_database_installation_task(master_installer_window,main_institute_wise_key_list) 
                                    if mysql_database_activty_message=="Success":
                                        sg.Popup("Successfully application installation and database installation is done",title="Success",text_color="white",location=(700,300))
                                        master_installer_window.close()
                                    else:
                                        master_installer_window.close()
                            else:
                                master_installer_window.close()
        else:
            sg.popup(db_installer_zip_file_extract_message,title="Error",text_color="red",location=(700,300))
            master_installer_window.close()
    except Exception as err:
            logger.error("following error raised %s",err) 
            print("last excution",err) 

    #################_mysql_database_installer_task#############################
def performing_mysql_database_installer_task(master_installer_window,main_institute_wise_key_list):
    message_for_processing_of_mysql_task="Fail"
    database_creditional_message,data_base_conn_data=validation_of_database_creaditional_screen(master_installer_window)
    if database_creditional_message=="Success":
        institute_screen_validation_message,list_of_dict_for_each_inst,main_institute_wise_key_list=handle_institute_screen_validation_task(master_installer_window,main_institute_wise_key_list)
        if institute_screen_validation_message=="Success":
            connected_message,connection,cursor=connect_to_database(data_base_conn_data)
            if (connected_message=="Success") and (connection is not None) and (cursor is not None):
                dbobjects_file_excution_message=dbobjects_file_excution(connection,cursor)
                connection.commit()
                cursor.close()
                connection.close()
                if dbobjects_file_excution_message=="Success":
                    connected_message,connection,cursor=connect_to_database(data_base_conn_data)
                    if (connected_message=="Success") and (connection is not None) and (cursor is not None):
                        sg.Popup("    Processing Global  Folder    ",title="Creation",text_color="white",location=(700,300))
                        excute_global_data_message=excute_global_data(Path("./MFSDBPackage-4.7-DBZIP/MFSDB/MYSQL/DBSeed/Global"),cursor)  
                        connection.commit()
                        cursor.close()
                        connection.close()
                        if excute_global_data_message=="Success":
                            connected_message,connection,cursor=connect_to_database(data_base_conn_data)
                            if (connected_message=="Success") and (connection is not None) and (cursor is not None):
                                sg.Popup("Excuting institutional Data",title="Creation",text_color="green",location=(700,300))
                                institution_handler_message=institution_handler(connection,cursor,main_institute_wise_key_list,list_of_dict_for_each_inst)
                                if institution_handler_message=="Success":
                                    message_for_processing_of_mysql_task=institution_handler_message
                                    connection.commit()
                                    cursor.close()
                                    connection.close()
    return message_for_processing_of_mysql_task

def institution_handler(connection,cursor,main_institute_wise_key_list,list_of_dict_for_each_inst):
    institution_handler_message=None
    try:
        mfs_temp_institutional_folder="%s/%s" %("./MFSDBPackage-4.7-DBZIP/MFSDB/MYSQL/DBSeed","mfs_temp_institutional_folder")
        os.mkdir(Path(mfs_temp_institutional_folder))
        logger.info("%s folder is created",mfs_temp_institutional_folder)
        for list_index in range(len(main_institute_wise_key_list)):
            pop_up_message="     Insert Data for Institution  %s  "%((main_institute_wise_key_list[list_index])[0])
            sg.Popup(pop_up_message,title="Creation",text_color="white",location=(700,300))
            institue_name="%s_%s" %("institution",((main_institute_wise_key_list[list_index])[0]))
            sub_folder_name="%s/%s" %(mfs_temp_institutional_folder,institue_name)
            os.mkdir(Path(sub_folder_name))
            logger.info("%s  sub folder is created",sub_folder_name)
            place_holder_replacer(sub_folder_name,main_institute_wise_key_list[list_index],list_of_dict_for_each_inst[list_index],cursor)
            institution_handler_message="Success"
    except Exception as err:
        sg.Popup(err,title="Error",text_color="red",location=(700,300))
        institution_handler_message="Fail"
        logger.error(err)
    return institution_handler_message
def place_holder_replacer(sub_folder_name,sub_list,institute_values,cursor):
    replace_obj=prepare_place_holder_tuple(sub_list,institute_values)
    institutional_folder_path="./MFSDBPackage-4.7-DBZIP/MFSDB/MYSQL/DBSeed/Institution"
    status_data="Insert Data"
    progress_bar,output,output_window_screen=output_screen_screen(status_data)
    max_len_for_processing_window=len(os.listdir(Path(institutional_folder_path)))
    temp_data=1
    event,values = output_window_screen.read(timeout=1000)
    for institutional_file in (os.listdir(Path(institutional_folder_path))):
        institutional_file_path=institutional_folder_path+"/"+institutional_file
        sql_statement,excuted_file_name=read_sql_file(institutional_file_path)
        updated_sql_stmt=reduce(lambda a, kv: a.replace(*kv),replace_obj,sql_statement)
        updated_file=sub_folder_name+'/'+institutional_file
        with open(Path(updated_file), "w") as out_put_file_obj:
            out_put_file_obj.write(updated_sql_stmt)
            log_event_message=sql_excution(updated_sql_stmt,cursor,excuted_file_name,status_data)
            processing_windows_screen_message="excuting %s \n %s "%(excuted_file_name,log_event_message)
            some_data="out of %s %s is excuting"%(str(max_len_for_processing_window),str(temp_data))
            output_window_screen['output_text'].update(some_data)
            progress_bar.update_bar(temp_data,(max_len_for_processing_window))
            print(processing_windows_screen_message)
            temp_data=temp_data+1
    write_csv_for_user_input(sub_folder_name,sub_list,institute_values)   
    output_window_screen.close()

def prepare_place_holder_tuple(sub_list,institute_values):
    bank_tuple=('&2',institute_values.get(sub_list[1]))
    location_tuple=('&4',institute_values.get(sub_list[2]))
    folder_tuple=('&3',institute_values.get(sub_list[3]))
    institute_id_tuple=('&1',str(sub_list[0]))
    langauge_list=institute_values.get(sub_list[4])
    langauge_str=prepare_lang_obj(langauge_list)
    langauge_tuple=('&6',langauge_str)
    replace_obj =(bank_tuple,location_tuple,folder_tuple,institute_id_tuple,langauge_tuple)
    return replace_obj

def write_csv_for_user_input(sub_folder_name,sub_list,institute_values):
    updated_file=sub_folder_name+'/'+"user_insert_data"+".csv"
    user_input_list=prepare_csv_data(sub_list,institute_values)
    with open(updated_file, mode='w') as csv_file:
        fieldnames = ["FindString","ReplaceString","comment"]
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        for user_input_dict in user_input_list:
            writer.writerow(user_input_dict)

def prepare_csv_data(sub_list,institute_values):
    langauge_list=institute_values.get(sub_list[4])
    langauge_str=prepare_lang_obj(langauge_list)
    user_input_list=[]
    user_input_list.append({"FindString":"&1","ReplaceString":str(sub_list[0]),"comment":"Institution id"})
    user_input_list.append({"FindString":"&2","ReplaceString":institute_values.get(sub_list[1]),"comment":"Bank Name"})
    user_input_list.append({"FindString":"&3","ReplaceString":institute_values.get(sub_list[3]),"comment":"folder name used in integration"})
    user_input_list.append({"FindString":"&4","ReplaceString":institute_values.get(sub_list[2]),"comment":"Location of the institute"})
    user_input_list.append({"FindString":"&5","ReplaceString":"MYSQL","comment":"DBTYPE#MYSQL#MSSQL#ORACLE#"})
    user_input_list.append({"FindString":"&6","ReplaceString":langauge_str,"comment":"Langauges to be enabled for the institute"})
    return user_input_list

def prepare_lang_obj(langauge_list):
    langauge_str=','  
    langauge_str=langauge_str.join(langauge_list)
    return langauge_str      
#################
def connect_to_database(data_base_conn_data):
    connected_message=None
    connection=None
    cursor=None
    try:
        connection = mysql.connector.connect(user=data_base_conn_data.get("user_name"),password=data_base_conn_data.get("pass_word"),host=data_base_conn_data.get("host_name"),database=data_base_conn_data.get("db_name"),auth_plugin='mysql_native_password')
        cursor = connection.cursor(buffered=True)
        connected_message="Success"
        logger.info("success fully connected to %s database",data_base_conn_data.get("db_name"))
    except mysql.connector.Error as err:
        connected_message=err
        logger.info("following error is raised while connecting to  %s database",data_base_conn_data.get("db_name"))
    return (connected_message,connection,cursor)


def dbobjects_file_excution(connection,cursor):
    dbobjects_file_excution_message=None
    try:
        list_of_file=set_file_excution_level(os.listdir(Path("./MFSDBPackage-4.7-DBZIP/MFSDB/MYSQL/DBObjects/master")))
        status_data=["Tables Creation","Producer Creation","View Creation","Sequences Creation"]
        for master_file_index in range(len(list_of_file)):
            file_path='%s/%s'%("./MFSDBPackage-4.7-DBZIP/MFSDB/MYSQL/DBObjects/master",list_of_file[master_file_index])
            sql_statement,excuted_file_name=read_sql_file(file_path)
            if sql_statement:
                event="%s  is  about  to  start    "%status_data[master_file_index]
                logger.info(event)
                sg.Popup(event,title="Creation",text_color="white",location=(700,300))
                logger.info("currently Excuting the %s file",file_path)
                object_creation(sql_statement,cursor,excuted_file_name,status_data[master_file_index]) 
        dbobjects_file_excution_message="Success"  
    except Exception as err:
        sg.Popup(err,title="Error",text_color="red",location=(700,300))
        logger.info(err)
        dbobjects_file_excution_message=err
    return dbobjects_file_excution_message

def set_file_excution_level(list_of_directory):
    list_of_sequence_file=["table","procedure","view","sequences"]
    for x in range(len(list_of_directory)):
        if (list_of_directory[x].lower()).find(("Tables".lower()))!=-1:
            list_of_sequence_file[0]='m_CreateTablesMaster.sql'
        elif (list_of_directory[x].lower()).find(('m_CreateProcMaster.sql'.lower()))!=-1:
            list_of_sequence_file[1]='m_CreateProcMaster.sql'
        elif (list_of_directory[x].lower()).find(('m_CreateViewsMaster.sql'.lower()))!=-1:
            list_of_sequence_file[2]='m_CreateViewsMaster.sql'
        else:
            list_of_sequence_file[3]='m_CreateSequencesMaster.sql' 
    return list_of_sequence_file

def read_sql_file(file_path):
    sql_file = open(Path(file_path),"r")
    excuted_file_name=(file_path.split('/'))[-1]
    sql_statement = sql_file.read()
    return sql_statement,excuted_file_name

def object_creation(sql_statement,cursor,excuted_file_name,status_data):
    replace_obj = ("SOURCE ..",str("./MFSDBPackage-4.7-DBZIP/MFSDB/MYSQL/DBObjects")), ('\\','/')
    progress_bar,output,output_window_screen=output_screen_screen(status_data)
    max_len_for_processing_window=(len(sql_statement.split("\n")))
    temp_data=1
    event,values = output_window_screen.read(timeout=1000)
    for data in sql_statement.split("\n"): 
        create_file_path=reduce(lambda a, kv: a.replace(*kv),replace_obj,data)
        if create_file_path:
            create_sql_statement,excuted_file_name=read_sql_file(create_file_path)
            log_event_message=sub_object_creation(create_sql_statement,excuted_file_name,cursor,status_data)
            processing_windows_screen_message="excuting %s \n %s "%(excuted_file_name,log_event_message)
            some_data="out of %s %s is excuting"%(str(max_len_for_processing_window),str(temp_data))
            output_window_screen['output_text'].update(some_data)
            progress_bar.update_bar(temp_data,(max_len_for_processing_window))
            print(processing_windows_screen_message)
            temp_data=temp_data+1
    output_window_screen.close()

def output_screen_screen(status_data):
    output_screen = [[sg.Text(status_data,size=(40,1),font='Courier 12',key='progress_bar_text',text_color='white',justification="center")],
                    [sg.ProgressBar(max_value=10, orientation='h', size=(47,30),key='progress')],
                    [sg.Text("Output_Screen",size=(40,1),font='Courier 12',key='output_text',text_color='white',justification="center")],
                    [sg.Output(size=(70,5),key='output')]]
    frame_layout = [[sg.Frame("Excution_Status",output_screen, font='Courier 12', title_color='white', element_justification="center",relief="groove",title_location="n")]]
    output_window_screen= sg.Window('ModeFinServer Pvt Ltd',frame_layout,location=(500,200),margins=(10, 10),auto_size_text=True,auto_size_buttons=True,element_justification="center",element_padding=((20,20),(20,20)))
    progress_bar = output_window_screen['progress']
    output = output_window_screen['output']
    return  progress_bar,output,output_window_screen

def sub_object_creation(create_sql_statement,excuted_file_name,cursor,status_data):
    log_message= "%s is created"%((status_data.split(" "))[0])
    if create_sql_statement.find("DELIMITER")!=-1:
        create_sql_statement=handle_procedure_case(create_sql_statement)
        log_event_message=sql_excution(create_sql_statement,cursor,excuted_file_name,status_data)
    else:    
        log_event_message=sql_excution(create_sql_statement,cursor,excuted_file_name,status_data)
    return log_event_message

def handle_procedure_case(sql_statement):
    bad_chars = ['DELIMITER $$','$$','DELIMITER ;']
    for data in bad_chars:
        sql_statement=sql_statement.replace(data, '')
    return sql_statement

def sql_excution(sql_statement,cursor,excuted_file_name,status_data):
    log_event_message=None
    logger.info("currently executing sql file is %s ",excuted_file_name)
    try:
        for result in cursor.execute(sql_statement,multi=True):
            try:
                table_name=get_table_name(result)
                if table_name:
                    log_event_message=create_log_message_for_event_excution(status_data,table_name)
                    logger.info("Number of rows affected by statement %s"%(result.rowcount))
            except Exception as error:
                print(error)
                logger.warning(error)
                pass
    except Exception as e:
       logger.error(e) 
    return log_event_message    


def get_table_name(result):
    if result:
        if (((str(result).lower()).find("CREATE TABLE".lower())!=-1) or ((str(result).lower()).find("CREATE VIEW".lower())!=-1) or ((str(result).lower()).find("CREATE PROCEDURE".lower())!=-1)) and (str(result).find("/*")==-1):
            data_demo=(sqlparse.format(str(result),strip_comments=True))
            table_name=str(data_demo).split(" ")[3]
        elif ((str(result).lower()).find("INSERT".lower())!=-1) and (str(result).find("/*")==-1):
            data_demo=(sqlparse.format(str(result),strip_comments=True))
            table_name=str(data_demo).split(" ")[3]
        elif ((str(result).lower()).find("call")!=-1) and (str(result).find("/*")==-1):
            data_demo=(sqlparse.format(str(result),strip_comments=True))
            table_name=str(data_demo).split(" ")[2]
        else:
            table_name=None   
    else:
        table_name=None     
    return table_name   

def create_log_message_for_event_excution(status_data,table_name):
    if status_data=="Tables Creation":
        log_event_message="%s table is created"%(table_name)
    elif status_data=="Producer Creation":
        log_event_message="%s producer is created"%(table_name)
    elif status_data=="View Creation":
        log_event_message="%s View is created"%(table_name)
    elif  status_data=="Insert Data":
        log_event_message="data is insert in %s"%(table_name) 
    else:
        log_event_message=None
    if log_event_message:  
        logger.info(log_event_message)  
    return log_event_message  

def excute_global_data(global_directory,cursor):
    excute_global_data_message=None
    try:
        status_data="Insert Data"
        logger.info("excuing the gobal data") 
        progress_bar,output,output_window_screen=output_screen_screen(status_data)
        max_len_for_processing_window=len(os.listdir(global_directory))
        temp_data=1
        for global_file_path in (os.listdir(global_directory)):
            required_file=str(global_directory)+"/"+global_file_path
            global_sql_statement,excuted_file_name=read_sql_file(required_file)
            log_event_message=sql_excution(global_sql_statement,cursor,excuted_file_name,status_data) 
            event,values = output_window_screen.read(timeout=1000)
            processing_windows_screen_message="excuting %s \n %s "%(excuted_file_name,log_event_message)
            logger.info(processing_windows_screen_message)   
            some_data="out of %s %s is excuting"%(str(max_len_for_processing_window),str(temp_data))
            output_window_screen['output_text'].update(some_data)
            progress_bar.update_bar(temp_data,(max_len_for_processing_window))
            print(processing_windows_screen_message)
            temp_data=temp_data+1
        output_window_screen.close()
        excute_global_data_message="Success"
    except Exception as err:
        sg.Popup(err,title="Error",text_color="red",location=(700,300))
        excute_global_data_message=err
        logger.info(err)
    return  excute_global_data_message   

installer_processing()