# Check out the code in work at https://www.kaggle.com/hsankesara/prototypical-net/
# Check out the blog at <COMING SOON>

import torch
import numpy as np  # linear algebra
import pandas as pd  # data processing, CSV file I/O (e.g. pd.read_csv)
from matplotlib import pyplot as plt
import cv2
from tensorboardX import SummaryWriter
from torch import optim
from tqdm import tqdm
import multiprocessing as mp
from preprocessing import read_images
from prototypicalNet import PrototypicalNet, train_step, test_step, load_weights
tqdm.pandas(desc="my bar!")


def main():
    tb_writer = SummaryWriter()

    # Reading the data
    print("Reading background images")
    trainx, trainy = read_images(r'D:\_hackerreborn\Prototypical-Networks\input\omniglot\images_background')
    print(trainx.shape)
    print(trainy.shape)

    print("Reading background images")
    testx, testy = read_images(r'D:\_hackerreborn\Prototypical-Networks\input\omniglot\images_evaluation')
    print(testx.shape)
    print(testy.shape)

    # Checking if GPU is available
    use_gpu = torch.cuda.is_available()
    # Converting input to pytorch Tensor
    trainx = torch.from_numpy(trainx).float()
    testx = torch.from_numpy(testx).float()
    if use_gpu:
        trainx = trainx.cuda()
        testx = testx.cuda()
    # Priniting the data
    print(trainx.size(), testx.size())
    # Set training iterations and display period
    num_episode = 16000
    frame_size = 500
    trainx = trainx.permute(0, 3, 1, 2)
    testx = testx.permute(0, 3, 1, 2)

    # Initializing prototypical net
    protonet = PrototypicalNet(use_gpu)
    optimizer = optim.SGD(protonet.parameters(), lr=0.001, momentum=0.9)

    # Training loop
    frame_loss = 0
    frame_acc = 0

    for i in range(num_episode):
        print("Train Episode Number : {0}".format(i))
        # if i > 10:
        #     break

        loss, acc = train_step(protonet, trainx, trainy, 5, 60, 5, optimizer)
        frame_loss += loss.data
        frame_acc += acc.data
        if (i + 1) % frame_size == 0:
            print("Frame Number:", ((i+1) // frame_size),
                  'Frame Loss: ', frame_loss.data.cpu().numpy().tolist() / frame_size,
                  'Frame Accuracy:', (frame_acc.data.cpu().numpy().tolist() * 100) / frame_size)

            tb_writer.add_scalar('frame_loss', frame_loss.data.cpu().numpy().tolist() / frame_size, ((i+1) // frame_size))
            tb_writer.add_scalar('frame_accuracy', frame_acc.data.cpu().numpy().tolist() / frame_size, ((i + 1) // frame_size))

            frame_loss = 0
            frame_acc = 0

    # # Test loop
    # num_test_episode = 2000
    # avg_loss = 0
    # avg_acc = 0
    # for _ in range(num_test_episode):
    #     print("Test Episode Number : {0}".format(_))
    #     loss, acc = test_step(protonet, testx, testy, 5, 60, 15)
    #     avg_loss += loss.data
    #     avg_acc += acc.data
    #
    # print('Avg Loss: ', avg_loss.data.cpu().numpy().tolist() / num_test_episode,
    #       'Avg Accuracy:', (avg_acc.data.cpu().numpy().tolist() * 100) / num_test_episode)
    #
    # # Using Pretrained Model
    # protonet = load_weights('./protonet.pt', protonet, use_gpu)


if __name__ == "__main__":
    main()
