# Import different libraries

import json, os
from minio import Minio
from minio.error import (ResponseError, BucketAlreadyOwnedByYou,
                            BucketAlreadyExists)

# smtplib module included in python by default for email purpose

from string import Template
import smtplib, json

# import more necessary packages for sending email
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# Initialize the client server with an endpoint, access and secret keys.

minioClient = Minio(os.environ['SERVER_NAME'],
                    access_key=os.environ['ACCESS_KEY'],
                    secret_key=os.environ['SECRET_KEY'],
                    secure=False)

class mockTest:    

    # Save the outputs of user as in json file
    # function for doing the make_bucket API call and taking the inputs

    def input(self):
        try:
            username = 'user-id'
            bucket_name = username+"-bucket"
            minioClient.make_bucket(bucket_name)
        except BucketAlreadyOwnedByYou as err:
            pass
        except BucketAlreadyExists as err:
            pass
        except ResponseError as err:
            print(err)

        inp = {}    # to store the outputs produced by the user as in dictionary
        count = 1   # counter for various different keys in dictionary

        while True:
            print("Enter answer:")
            x=os.popen(input()).read().split('\n')[0]
            if x=='end':
                break
            inp['Q ' + str(count)] = x
            count+=1

        # convert all the output data into json file
        with open('course-title.json', 'w') as json_file:
            json.dump(inp, json_file)

        # Verification of the format in console and display it
        y = json.dumps(inp)
        print(y)

        return;

    # Saving concept goes here like json to Minio interaction

    def save(self):
        try:
            bucket_name = "user-id-bucket"
            object_name = "course-title.json"
            file_path = "course-title.json"
            minioClient.fput_object(bucket_name, object_name, file_path)

        except ResponseError as err:
            print(err)

        return;

    # Process the data which is retrieved from the minio server to evaluate the result
    # Retrieving concept goes here like Minio to json interaction

    def process(self):
        try:
            username = "user-id"                    # fetch user id from db
            bucket_name = username+"-bucket"        # refer to the current user bucket by her id
            object_name = "course-title.json"       # all the submissions with same name in different bucket names
            file_path = "course-title-fetch.json"
            minioClient.fget_object(bucket_name, object_name, file_path)

        except ResponseError as err:
            print(err)

        data = open("course-title-fetch.json", 'r')
        data = json.load(data)
        sol = open('course-title-key.json', 'r')
        sol = json.load(sol)

        count=1
        total_score=0

        for i in range(0,len(data)):
            if(sol["Q "+str(count)] == data["Q "+str(count)]):
               data["Q " +str(count)]="correct"
               total_score+=1
            else:
                data["Q " +str(count)]="incorrect"
            count+=1

        # to store the final score of candidate
        data["total_score"]=total_score

        # convert into json
        with open('course-title-result.json', 'w') as json_file:
            json.dump(data, json_file)

        # Saving concept goes here like json to Minio interaction
        try:
            bucket_name = "user-id-bucket"
            object_name = "course-title-result.json"
            file_path = "course-title-result.json"
            minioClient.fput_object(bucket_name, object_name, file_path)

        except ResponseError as err:
            print(err)
    
        return;

    # Program to read contacts from a file and return a list of name and emails
    # Followed by emailing the results back to the user

    # 3 email functions whose definition starts here

    def get_contacts(self, filename):
        names=[]    # this will contain all the names of users
        emails=[]   # it will contain the corresponding emails of users
        with open(filename, mode='r', encoding='utf-8') as contacts_file:
            for contact in contacts_file:
                names.append(contact.split()[0])
                emails.append(contact.split()[1])
            return names, emails

    def read_template(self, filename):
        with open(filename, mode='r', encoding='utf-8') as template_file:
            template_file_content = template_file.read()
        return Template(template_file_content)  

    def email(self, names, emails, message_template ):

        # set up the SMTP server
        s = smtplib.SMTP(host='smtp.gmail.com', port=587)   # email service provider info goes here
        s.starttls()
        MY_ADDRESS = 'adarsh@cloudyuga.guru'
        PASSWORD = '*********'                              
        s.login(MY_ADDRESS, PASSWORD)                       # email and password of the senders account

        # Sending emails logic starts here

        # For each contact, send the email:
        for name, email1 in zip(names, emails):
            msg = MIMEMultipart()       # create a message
            
            res = open('course-title-result.json', 'r')
            res = json.load(res)
            res1 = ''

            for x in res:
                res1  = res1 + ("%s - %s" %(x, res[x])) + "\n"

            # add in the actual person name to the message template
            message = message_template.substitute(PERSON_NAME=name.title(),RESULT=res1)

            print("email sent")  # to check the format of message being sent

            # setup the parameters of the message
            msg['From']=MY_ADDRESS
            msg['To']=email1
            msg['Subject']="Mock Test Result - "

            # add in the message body
            msg.attach(MIMEText(message, 'plain'))

            # send the message via the server set up earlier.
            s.send_message(msg)
    
            del msg

        # terminate the SMTP connection and close the connection
        s.quit()

    def __init__(self, name):
        print("hello world from "+name)

obj = mockTest('ash')
obj.input()
obj.save()
obj.process()
names, emails = obj.get_contacts('contacts.txt')        # read contacts
message_template = obj.read_template('message.txt')     # define a template for body
obj.email(names, emails, message_template)


