#!/usr/bin/env python
import pymongo
import time
import pika

# method to receive statements generated by RabbitMQ
def callback(ch, method, properties, body):
    print("%r:%r" % (method.routing_key, body))


# start instance of Mongo Client and RabbitMQ Channel
db = pymongo.MongoClient().test
connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
channel = connection.channel()

# event loop for sending commands
while 1:
    # First recieve input from keyboard
    message = input("Type message command:")
    print("[Checkpoint 01", time.time(), "] Message Captured:"
          , message)
    # construct msg ID for each message received
    MsgID = "team_19$" + str(time.time())

    # Parsing message to MongoDB format
    if message[0:2:] == 'p:':
        #produce
        action = 'p'
        place = message[message.find(':')+1:message.find('+'):]
        queue = message[message.find('+')+1:message.find('"')-1:]
        cmdMess = message[message.find('"')+1:message.rfind('""'):]
        #construct command in db format
        command = {
                    "Action": action,
                    "Place": place,
                    "MsgID": MsgID,
                    "Subject": queue,
                    "Message": cmdMess
                  }

        # Insert command into mongoDB
        print("[Checkpoint 02 ", time.time(), "] Store command in MongoDB instance:"
              , command)
        db.commands.insert(command)

        # send command to rabbit MQ and receive result/response
        print("[Checkpoint 03 ", time.time(), "] Accessing the RabbitMQ instance:")
        print("Produce in", place, "+", queue,":", cmdMess)
        # channel.exchange_declare(exchange=place, exchange_type='direct')
        channel.basic_publish(exchange=place, routing_key=queue, body=cmdMess)


    elif message[0:2:] == 'c:':
        #consume
        action = 'c'
        place = message[message.find(':')+1:message.find('+'):]
        subject = message[message.find('+')+1::]
        command = {
                    "Action": action,
                    "Place": place,
                    "MsgID": MsgID,
                    "Subject": subject,
                  }

        # insert command into mongoDB
        print("[Checkpoint 02 ", time.time(), "] Store command in MongoDB instance:"
              , command)
        db.commands.insert(command)

        # send command to rabbit MQ and receive result/response
        print("[Checkpoint 03 ", time.time(), "] Accessing the RabbitMQ instance:")
        channel.queue_bind(exchange=place, queue=subject, routing_key=subject)
        channel.basic_consume(on_message_callback=callback, queue=subject, auto_ack=True)
        try:
            channel.start_consuming()
        except KeyboardInterrupt:
            channel.stop_consuming()

    else:
        print("No command recieved")
        continue


connection.close()
