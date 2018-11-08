#!/usr/bin/env python3
import time
import boto3
import subprocess
import sys
import os


#Creating Instance
ec2 = boto3.resource('ec2')
instance = ec2.create_instances(
	ImageId='ami-0c21ae4a3bd190229',
	KeyName='DevOps2018',
	MinCount=1,
	MaxCount=1,
	SecurityGroupIds=['sg-0c475047ceddb1029'],    # my HTTP/SSH sec group
	UserData='''#!/bin/bash 
		yum -y update          
		yum install python3 -y
		amazon-linux-extras install nginx1.12 -y
		sudo service nginx start -y
		chkconfig nginx on
		touch /home/ec2-user/testfile''',
	InstanceType='t2.micro')
    
print ("\n")
print ( "Creating instance...")
time.sleep(2)    
print ("An instance with ID", instance[0].id, "has been created. \n")
time.sleep(5)
instance[0].reload()
#Short piece of code gotten from stackoverflow for cpu usage
CPU_Pct=str(round(float(os.popen('''grep 'cpu ' /proc/stat | awk '{usage=($2+$4)*100/($2+$4+$5)} END {print usage }' ''').readline()),2))

#print results
print("CPU Usage = " + CPU_Pct)


#Getting Ip address for instance
print ("Fetching ip address...")
time.sleep(3)
print ("Public IP address:", instance[0].public_ip_address)
print ("\n")
time.sleep(80)

#Copying check_webserver.py to the instance
try:
	cmd1 = "scp -o StrictHostKeyChecking=no -i DevOps2018.pem check_webserver.py ec2-user@" + instance[0].public_ip_address + ":."
	subprocess.call(cmd1, shell=True)
	print("\n")
	print ("1. Copying check_webserver.py to intance...")
	time.sleep(3)
	print ("File copied... \n")
	time.sleep(3)
except subprocess.CalledProcessError:
	print ("Sorry, There was an error with copying the file(cmd1)!!")
	time.sleep(3)

#Giving permissions to check_webserver.py
try:
	print ("2. Giving permissions to check_webserver.py ...")
	time.sleep(1)
	cmd2 = "ssh -o StrictHostKeyChecking=no -i DevOps2018.pem ec2-user@" + instance[0].public_ip_address + " 'chmod +x ./check_webserver.py'"
	subprocess.call(cmd2, shell=True)
	print ("Permissions granted \n")
	time.sleep(1)
except subprocess.CalledProcessError:
	print ("Sorry, There was an error with granting permissions (cmd2) \n")
	time.sleep(1)

#Remotely executing check_webserver.py
try:
	print ("3. Romotely executing check_webserver.py")
	time.sleep(1)
	cmd3 = "ssh -i DevOps2018.pem ec2-user@" + instance[0].public_ip_address + " './check_webserver.py'"
	subprocess.call(cmd3, shell=True)
	print ("File successfuly executed... \n")
	time.sleep(1)
except subprocess.CalledProcessError:
	print ("Sorry, There was an error executing the file (cmd3)!! \n")
	time.sleep(1)

#Listing Instnaces
try:
	print("Listing Instances... \n")
	time.sleep(1)
	ec2 = boto3.resource('ec2')
	for instance in ec2.instances.all():
		print(instance.id, instance.state)
		print("\n Instances Listed... \n")
except subprocess.CalledProcessError:
	print("Sorry, There was an error listing the instances! \n")

#Creating a Bucket
try:
	print("Creating a bucket...")
	time.sleep(1)
	bucket_name = input("Please Input a bucket name:")
	subprocess.Popen("./create_bucket.py " + bucket_name, shell=True)
except subprocess.CalledProcessError:
	print("Error Creating Bucket!! \n")
	time.sleep(1)
	
#List Buckets
s3 = boto3.resource('s3')
for bucket in s3.buckets.all():
	print (bucket.name)
	print ("______________________________________________________ ")
	time.sleep(1)
	print("\n")

#Putting an Image into a bucket
try:
	print("Please Follow the steps to put your image into the bucket...")
	bucket_name=input("\n Pleases enter the bucket name: \n")
	object_name=input("\n Enter the name of the image: \n")

	subprocess.Popen("./put_bucket.py " + bucket_name + " " + object_name, shell=True)
	print("\n Image inserted into bucket... \n")
	time.sleep(2)
except subprocess.CalledProcessError:
	print("Error inserting file into bucket \n")
	time.sleep(2)

#Inserting an image onto a webserver
try:
	print("Please follow the steps to insert your image onto the webserver.. \n")
	FileName=input("\n Please Enter The File Name(eg=Carlton.jpg) :")
	bucket_name=input("\n Please Enter The Bucket Name :")
	IPaddress=input("\n Please Enter an IP address :")
	try:
		f= open("index.html","w+")		
		html='''
		<html>
			<body>
				<img src="https://s3-eu-west-1.amazonaws.com/''' + bucket_name + '''/''' + FileName +'''">
			</body>
		</html>'''
		f.write(html)
		f.close()
	except subprocess.CalledProcessError:
		print("Error with html File...\n")

	#Command For Copying 
	try:
		print("\n")
		print("Copying index.html to instance...")
		cmd4 = "scp -i DevOps2018.pem index.html ec2-user@" + IPaddress + ":."
		subprocess.call(cmd4, shell=True)
		print("File Successfully Copied.. \n")
		time.sleep(2)
	except subprocess.CalledProcessError:
		print("Error Copying File \n")
	
	#Command For moving file to webserver
	try:
		print("Moving index.html to webserver location... \n")
		time.sleep(2)
		cmd5 = "ssh -i DevOps2018.pem ec2-user@" + IPaddress + " 'sudo mv index.html /usr/share/nginx/html/index.html'"
		subprocess.call(cmd5, shell=True)
		print("Image successfully moved")
	except subprocess.CalledProcessError:
		print("Sorry, There was an error moving the image...")
	
except subprocess.CalledProcessError:
	print("Error moving an image to nginx webserver")
	
	



















