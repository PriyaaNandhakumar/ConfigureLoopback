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

       
@app.route('/configure_loopback', methods=['POST'])
def configure_loopback_route():
    data = request.json
    hostname = data.get('hostname')
    username = data.get('username')
    password = data.get('password')
    loopback_ip = data.get('loopback_ip')
    interface_number = data.get('interface_number')
    
    device_params = {
    'device_type': 'cisco_xr',
    'ip': hostname,
    'username': username,
    'password': password,
    }

    result = configure_loopback_interface(device_params, interface_number, loopback_ip)

    return jsonify({'result': result})


    
if __name__ == '__main__':
    app.run(debug=True)

