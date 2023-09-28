#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# =============================================================================
# Created By  : Priyaa Elumalai
# Created Date: 28/9/2023
# =============================================================================
"""The Module Has Been Build to configure loopback interface using netmiko module via CLI"""
# =============================================================================
# Imports
# =============================================================================
from flask import Flask, request, jsonify
from netmiko import ConnectHandler
from tabulate import tabulate
from ncclient import manager

#Create a Flask application
app = Flask(__name__)


########  Supporting Functions for Routes #########
# NETCONF XML template for configuring a loopback interface
loopback_config_template = """
<config>
    <interfaces xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces">
        <interface>
            <name>Loopback{interface_number}</name>
            <description>{description}</description>
            <type xmlns:ianaift="urn:ietf:params:xml:ns:yang:iana-if-type">
                ianaift:softwareLoopback
            </type>
            <enabled>true</enabled>
            <ipv4 xmlns="urn:ietf:params:xml:ns:yang:ietf-ip">
                <address>
                    <ip>{ip_address}</ip>
                    <netmask>{subnet_mask}</netmask>
                </address>
            </ipv4>
        </interface>
    </interfaces>
</config>
"""


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

def connectionstring_netconf(data):
    hostname = data["hostname"]
    username = data["username"]
    password = data["password"]
    
    netconf_params = {
    'host': hostname,
    'port': 22,
    'username': username,
    'password': password,
    'device_params': {'name': 'iosxr'},
    }
    
    return netconf_params

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

def list_loopback_interface(device_params):
    try:
        # Connect to the IOS XR device
        net_connect = ConnectHandler(**device_params)
        net_connect.enable()

        # Construct the CLI command
        command = f'show interfaces description'

        # Send the command to the device
        output = net_connect.send_command(command)
        # Close the SSH connection
        net_connect.disconnect()

        # Split the output into lines and remove leading/trailing spaces
        output_lines = [line.strip() for line in output.splitlines()]

        # Remove header and empty lines
        output_lines = [line for line in output_lines if line and not line.startswith('Interface')]

        # Split each line into columns using whitespace as a delimiter
        table_data = [line.split() for line in output_lines]

        # Print the table using tabulate
        print(tabulate(table_data, headers=['Interface', 'Description'], tablefmt='grid'))

        # Close the SSH connection
        net_connect.disconnect()

        return {'message': 'Interface configuration:', 'output': output}, 200

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

@app.route('/list_loopback', methods=['POST'])
def list_loopback():
    data = request.get_json()
    device_params=connectionstring(data)
    
    
    result, status_code = list_loopback_interface(device_params)
    return jsonify(result), status_code  


############ Via Netconf ########################
@app.route('/configure_loopback_netconf', methods=['POST'])
def configure_loopback_netconf():
    data = request.get_json()
    netconf_params=connectionstring_netconf(data)
    interface_number = data.get('interface_number')
    description = data.get('description')
    ip_address = data.get('ip_address')
    subnet_mask = data.get('subnet_mask')

    if not interface_number or not description or not ip_address or not subnet_mask:
        return {'message': 'All fields are required.'}, 400

    try:
        with manager.connect(**netconf_params) as m:
            loopback_config = loopback_config_template.format(
                interface_number=interface_number,
                description=description,
                ip_address=ip_address,
                subnet_mask=subnet_mask
            )
            m.edit_config(target='running', config=loopback_config)

        return {'message': 'Loopback interface configured successfully.'}, 200

    except Exception as e:
        return {'message': f'Error configuring loopback interface: {str(e)}'}, 500

if __name__ == '__main__':
    app.run(debug=True)

