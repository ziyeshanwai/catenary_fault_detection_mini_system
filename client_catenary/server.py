# -*- coding: utf-8 -*-

"""
Author:  Liyou Wang
Date: 2018.11.3
description:接触网小目标检测系统的服务器端，测试功能为展示客户端上传来的图片
"""
import grpc
import cv2
import detec_image_pb2 # message class
import detec_image_pb2_grpc # grpc server and client class
from concurrent import futures
import time
import struct
import numpy as np


# create a class to define the server functions, derived from
# calculator_pb2_grpc.CalculatorServicer
class DetectionServicer(detec_image_pb2_grpc.GetdetectionresultServicer):

    def Getdetres(self, request, context):
        print('the width is {}'.format(request.width))
        # print('the height is {}'.format(request.height))
        # print('the channel is {}'.format(request.channel))
        img_bytes = request.image
        img = np.array(struct.unpack('B'*request.width*request.height*request.channel, img_bytes), dtype=np.uint8).reshape([request.height, request.width, request.channel])
        np.save('./img.npy', img)
        response = detec_image_pb2.detecresult()
        """这里插入深度学习检测代码"""
        response.strofresult = "test is ok"
        return response


if __name__ == '__main__':
    # create a gRPC server
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    sess = 23

    # use the generated function `add_CalculatorServicer_to_server`
    # to add the defined class to the server
    detec_image_pb2_grpc.add_GetdetectionresultServicer_to_server(
            DetectionServicer(), server)

    # listen on port 50051
    print('Starting server. Listening on port 50051.')
    server.add_insecure_port('127.0.0.1:50051')
    server.start()
    

    # since server.start() will not block,
    # a sleep-loop is added to keep alive
    try:
        while True:
            time.sleep(86400)
    except KeyboardInterrupt:
        server.stop(0)
