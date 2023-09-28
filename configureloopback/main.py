#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# =============================================================================
# Created By  : Priyaa Elumalai
# Created Date: 28/9/2023
# =============================================================================
"""The Module Has Been Build to configure loopback interface"""
# =============================================================================
# Imports
# =============================================================================
from flask import Flask, request, jsonify
import paramiko
import re

#Create a Flask application
app = Flask(__name__)



def configure_loopback(hostname, username, password, loopback_ip, subnet_mask):
    try:
        # Create an SSH client
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        # Connect to the device
        client.connect(hostname, username=username, password=password, timeout=10)
        
        # Create an SSH session
        ssh_session = client.invoke_shell()
        
        # Send commands to configure the loopback interface
        ssh_session.send("configure terminal\n")
        ssh_session.send(f"interface Loopback0\n")
        ssh_session.send(f"ip address {loopback_ip} {subnet_mask}\n")
        ssh_session.send("end\n")
        
        # Wait for the command to complete
        while True:
            output = ssh_session.recv(65535).decode("utf-8")
            if re.search(r"#", output):
                break
        
        # Close the SSH session and connection
        ssh_session.close()
        client.close()
        
        return "Loopback interface configured successfully."

    except Exception as e:
        return str(e)

def check_loopback_configuration(hostname, username, password):
    try:
        # Create an SSH client
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        # Connect to the device
        client.connect(hostname, username=username, password=password, timeout=10)

        # Create an SSH session
        ssh_session = client.invoke_shell()

        # Send a command to display interface information
        ssh_session.send("show interfaces brief | include Loopback0\n")
        

        # Wait for the command to complete and collect output
        output = ""
        while True:
            recv_data = ssh_session.recv(65535).decode("utf-8")
            output += recv_data
            if re.search(r"#", recv_data):
                break

        # Close the SSH session and connection
        ssh_session.close()
        client.close()
        # Check if the output contains information about Loopback0
        if re.search(r"Loopback0", output):
            return "Loopback interface is configured."
        else:
            return "Loopback interface is not configured."

    except Exception as e:
        return str(e)

def delete_loopback_config(hostname, username, password, interface_number):
    try:
        # Establish SSH connection to the router
        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh_client.connect(hostname, username=username, password=password)

        # Construct and execute the command to delete the loopback interface
        command = f"no interface Loopback{interface_number}"
        stdin, stdout, stderr = ssh_client.exec_command(command)

        # Check for errors
        error_message = stderr.read().decode()
        if error_message:
            return jsonify({'message': f'Error: {error_message}'}), 500

        ssh_client.close()
    except Exception as e:
        return jsonify({'message': f'Error: {str(e)}'}), 500
        
@app.route('/configure_loopback', methods=['POST'])
def configure_loopback_route():
    data = request.json
    hostname = data.get('hostname')
    username = data.get('username')
    password = data.get('password')
    loopback_ip = data.get('loopback_ip')
    subnet_mask = data.get('subnet_mask')

    result = configure_loopback(hostname, username, password, loopback_ip, subnet_mask)

    return jsonify({'result': result})

@app.route('/check_loopback_configured', methods=['POST'])
def check_loopback_configured():
    data = request.json
    hostname = data.get('hostname')
    username = data.get('username')
    password = data.get('password')
    
    result = check_loopback_configuration(hostname, username, password)

    return jsonify({'result': result})


@app.route('/delete_loopback', methods=['POST'])
def delete_loopback():
    data = request.json
    hostname = data.get('hostname')
    username = data.get('username')
    password = data.get('password')
    interfacenumber = data.get('interfacenumber')
    
    result = delete_loopback_config(hostname, username, password, interfacenumber)

    return jsonify({'result': result})
    
if __name__ == '__main__':
    app.run(debug=True)

