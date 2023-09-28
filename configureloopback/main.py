#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# =============================================================================
# Created By  : Priyaa Elumalai
# Created Date: 28/9/2023
# =============================================================================
"""The Module Has Been Build to configure loopback interface using netmiko module"""
# =============================================================================
# Imports
# =============================================================================
from flask import Flask, request, jsonify
from netmiko import ConnectHandler
import re

#Create a Flask application
app = Flask(__name__)


########  Supporting Functions for Routes #########
def connectionstring(data):
    hostname = data["hostname"]
    username = data["username"]
    password = data["password"]
    
    device_params = {
    'device_type': 'cisco_xr',
    'ip': hostname,
    'username': username,
    'password': password,
    }
    
    return device_params

def configure_loopback_interface(device_params, interface_number, ip_address):
    try:
        # Connect to the IOS XR device
        net_connect = ConnectHandler(**device_params)
        net_connect.enable()

        # Construct the CLI command
        command = [
            f'interface Loopback{interface_number}',
            f'ip address {ip_address}',
            'commit',
            'end',
        ]

        # Send the commands to the device
        output = net_connect.send_config_set(command)

        # Close the SSH connection
        net_connect.disconnect()
        return {'message': 'Interface configured successfully.', 'output': output}, 200

    except Exception as e:
        return {'message': str(e)}, 500

def show_loopback_interface(device_params,interface_number):
    try:
        # Connect to the IOS XR device
        net_connect = ConnectHandler(**device_params)
        net_connect.enable()

        # Construct the CLI command
        command = f'show running-config interface Loopback{interface_number}'

        # Send the command to the device
        output = net_connect.send_command(command)

        # Close the SSH connection
        net_connect.disconnect()

        return {'message': 'Interface configuration:', 'output': output}, 200

    except Exception as e:
        return {'message': str(e)}, 500
        
        
def delete_loopback_interface(device_params,interface_number):
    try:
        # Connect to the IOS XR device
        net_connect = ConnectHandler(**device_params)
        net_connect.enable()

        # Construct the CLI command to delete the loopback interface
        delete_command = [
            f'configure terminal',
            f'no interface Loopback{interface_number}',
            'commit',
            'end',
        ]

        # Send the delete command to the device
        output = net_connect.send_config_set(delete_command)

        # Close the SSH connection
        net_connect.disconnect()

        return {'message': 'Interface deleted successfully.', 'output': output}, 200

    except Exception as e:
        return {'message': str(e)}, 500        

 ##############################   Routes  #################################

 
@app.route('/configure_loopback', methods=['POST'])
def configure_loopback_route():
    data = request.json
    device_params=connectionstring(data)
    loopback_ip = data.get('loopback_ip')
    interface_number = data.get('interface_number')
    
    result = configure_loopback_interface(device_params, interface_number, loopback_ip)

    return jsonify({'result': result})


@app.route('/show_loopback', methods=['POST'])
def show_loopback():
    data = request.json
    device_params=connectionstring(data)
    interface_number = data.get('interface_number')
    
    if not interface_number:
        return {'message': 'interface_number is required as a query parameter.'}, 400
    
    result, status_code = show_loopback_interface(device_params,interface_number)
    return jsonify(result), status_code
    
    
@app.route('/delete_loopback', methods=['POST'])
def delete_loopback():
    data = request.get_json()
    device_params=connectionstring(data)
    interface_number = data.get('interface_number')
    
    if not interface_number:
        return {'message': 'interface_number is required.'}, 400
    
    result, status_code = delete_loopback_interface(device_params,interface_number)
    return jsonify(result), status_code    
    
if __name__ == '__main__':
    app.run(debug=True)

