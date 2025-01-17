import argparse
import os

import trainer as trainer

if __name__ == "__main__":
    # ----------------------------------------
    #        Initialize the parameters
    # ----------------------------------------
    parser = argparse.ArgumentParser()
    # Pre-train, saving, and loading parameters
    parser.add_argument('--pre_train', type = bool, default = True, help = 'pre-train or not')
    parser.add_argument('--singleFrame', type = bool, default = True, help = 'single frame training or video frames training')
    parser.add_argument('--save_mode', type = str, default = 'epoch', help = 'saving mode, and by_epoch saving is recommended')
    parser.add_argument('--save_by_epoch', type = int, default = 1, help = 'interval between model checkpoints (by epochs)')
    parser.add_argument('--save_by_iter', type = int, default = 100000, help = 'interval between model checkpoints (by iterations)')
    parser.add_argument('--save_name_mode', type = bool, default = True, help = 'True for concise name, and False for exhaustive name')
    parser.add_argument('--load_name', type = str, default = './models/bs1_sc32_gan_pre/Pre_colorization_epoch500_bs1_GAN0_os2_ol2', help = 'load the pre-trained model with certain epoch')
    # GPU parameters
    parser.add_argument('--multi_gpu', type = bool, default = True, help = 'True for more than 1 GPU')
    parser.add_argument('--gpu_ids', type = str, default = '0, 1', help = 'gpu_ids: e.g. 0  0,1  0,1,2  use -1 for CPU')
    parser.add_argument('--cudnn_benchmark', type = bool, default = True, help = 'True for unchanged input data type')
    # Training parameters
    parser.add_argument('--epochs', type = int, default = 10, help = 'number of epochs of training')
    parser.add_argument('--batch_size', type = int, default = 8, help = 'size of the batches')
    parser.add_argument('--lr_g', type = float, default = 0.0001, help = 'Adam: learning rate for G')
    parser.add_argument('--lr_d', type = float, default = 0.0001, help = 'Adam: learning rate for D')
    parser.add_argument('--b1', type = float, default = 0.5, help = 'Adam: decay of first order momentum of gradient')
    parser.add_argument('--b2', type = float, default = 0.999, help = 'Adam: decay of second order momentum of gradient')
    parser.add_argument('--weight_decay', type = float, default = 0, help = 'weight decay for optimizer')
    parser.add_argument('--lr_decrease_mode', type = str, default = 'epoch', help = 'lr decrease mode, by_epoch or by_iter')
    parser.add_argument('--lr_decrease_epoch', type = int, default = 200, help = 'lr decrease at certain epoch and its multiple')
    parser.add_argument('--lr_decrease_iter', type = int, default = 200000, help = 'lr decrease at certain epoch and its multiple')
    parser.add_argument('--lr_decrease_factor', type = float, default = 0.8, help = 'lr decrease factor')
    parser.add_argument('--num_workers', type = int, default = 4, help = 'number of cpu threads to use during batch generation')
    parser.add_argument('--mask_para', type=float, default=50.0, help='coefficient for computing visibility mask')
    parser.add_argument('--lambda_flow', type = int, default = 10, help = 'coefficient for Flow Loss')
    parser.add_argument('--lambda_flow_long', type = int, default = 10, help = 'coefficient for Flow Loss')
    parser.add_argument('--lambda_gan', type = float, default = 0, help = 'coefficient for GAN Loss')
    # Initialization parameters
    parser.add_argument('--pad', type = str, default = 'reflect', help = 'pad type of networks')
    parser.add_argument('--norm', type = str, default = 'in', help = 'normalization type of networks')
    parser.add_argument('--in_channels', type = int, default = 3, help = '1 for colorization, 3 for other tasks')
    parser.add_argument('--out_channels', type = int, default = 3, help = '2 for colorization, 3 for other tasks')
    parser.add_argument('--start_channels', type = int, default = 64, help = 'start channels for the main stream of generator')
    parser.add_argument('--init_type', type = str, default = 'kaiming', help = 'initialization type of networks')
    parser.add_argument('--init_gain', type = float, default = 0.02, help = 'initialization gain of networks')
    # GAN parameters
    parser.add_argument('--gan_mode', type = bool, default = False, help = 'add GAN or not')
    parser.add_argument('--additional_training_d', type = int, default = 1, help = 'number of training D more times than G')
    # Dataset parameters
    parser.add_argument('--task', type = str, default = 'colorization', help = 'the specific task of the system')
    parser.add_argument('--baseroot', type = str, default = '/home/alien/Documents/zyz/ILSVRC2012_train_256', help = 'color image baseroot')
    parser.add_argument('--iter_frames', type = int, default = 10, help = 'number of iter_frames')
    parser.add_argument('--resize_h', type = int, default = 256, help = 'resize height')
    parser.add_argument('--resize_w', type = int, default = 256, help = 'resize width')
    parser.add_argument('--pwcnet_path', type = str, default = './models/pwcNet-default.pytorch', help = 'the path that contains the PWCNet model')
    opt = parser.parse_args()


    # ----------------------------------------
    #        Choose CUDA visible devices
    # ----------------------------------------
    if opt.multi_gpu == True:
        os.environ["CUDA_VISIBLE_DEVICES"] = opt.gpu_ids
        print('Multi-GPU mode, %s GPUs are used' % (opt.gpu_ids))
    else:
        os.environ["CUDA_VISIBLE_DEVICES"] = "0"
        print('Single-GPU mode')
    
    # ----------------------------------------
    #       Choose pre / continue train
    # ----------------------------------------
    if opt.singleFrame:
        print('Pre-training single frame colorization settings: [Epochs: %d] [Batch size: %d] [Learning rate: %.4f] [Saving mode: %s]'
            % (opt.epochs, opt.batch_size, opt.lr_g, opt.save_mode))
        if opt.gan_mode:
            trainer.Train_single(opt)
        else:
            trainer.Pre_train_single(opt)
    else:
        print('Continue-training settings: [Epochs: %d] [Batch size: %d] [Learning rate: %.4f] [Saving mode: %s]'
            % (opt.epochs, opt.batch_size, opt.lr_g, opt.save_mode))
        if opt.gan_mode:
            print('With GAN: [mask_para: %.4f] [lambda_flow: %d] [lambda_flow_long: %.4f] [lambda_gan: %.4f]'
            % (opt.mask_para, opt.lambda_flow, opt.lambda_flow_long, opt.lambda_gan))
            trainer.Train_GAN(opt)
        else:
            print('Without GAN: [mask_para: %.4f] [lambda_flow: %d] [lambda_flow_long: %.4f]'
            % (opt.mask_para, opt.lambda_flow, opt.lambda_flow_long))
            trainer.Train_No_GAN(opt)