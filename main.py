import numpy as np
from MyDataLoader import MyDataLoader
from Trainer import Trainer
import os
import json
import torch.utils.data as Data

class Parameters(object):
    def __init__(self, batchSize=512, imageSize=(24, 21), nz=512, ngf=64, ndf=64, 
                       nepochs=1500, lr=0.0001, beta1=0.8, gpu=1, adv_weight=0.1,
                       lrd=0.0001, alpha=0.3, outf='results', f_emb=8) -> None:
        self.batchSize=batchSize
        self.imageSize=imageSize
        self.nz=nz      # size of the latent z vector
        self.ngf=ngf    # Number of filters to use in the generator network
        self.ndf=ndf    # Number of filters to use in the discriminator network
        self.nepochs=nepochs
        self.lr=lr
        self.beta1=beta1    # beta1 for adam. default=0.5
        self.gpu=gpu        # GPU to use, -1 for CPU training
        self.adv_weight=adv_weight  # weight for adv loss
        self.lrd=lrd    # learning rate decay, default=0.0001
        self.alpha=alpha    # multiplicative factor for target adv. loss
        self.outf=outf


if __name__ == '__main__':
    opt = Parameters(batchSize=512, imageSize=(24, 21), nz=512, ngf=64, ndf=64, 
                       nepochs=5000, lr=0.00008, beta1=0.8, gpu=1, adv_weight=1.5,
                       lrd=0.0001, alpha=0.1, outf='results')
    mean = np.array([0.44, 0.44, 0.44])
    std = np.array([0.19, 0.19, 0.19])
    # target_names = {'../Data/HV_O_data.csv': 'Hardness (HV)', '../Data/UTS_O_data.csv': 'UTS (MPa)', '../Data/UTS_2_O_data.csv': 'UTS', '../Data/UTS_all_O_data.csv': 'UTS (MPa)', '../Data/UTS_HT_O_data.csv': 'UTS'}
    # img_files = {'../Data/HV_O_data.csv': '../Data/Schedule_HV.csv', '../Data/UTS_O_data.csv': '../Data/Schedule_UTS.csv', '../Data/UTS_2_O_data.csv':  '../Data/Schedule_UTS_2.csv', '../Data/UTS_all_O_data.csv': '../Data/Schedule_UTS_all.csv', '../Data/UTS_HT_O_data.csv': '../Data/Schedule_UTS_HT.csv'}
    # checkpoint_names = {'../Data/UTS_O_data.csv': 'HV-UTS-1', '../Data/UTS_2_O_data.csv': 'HV-UTS-2', '../Data/UTS_all_O_data.csv': 'HV-UTS-all', '../Data/UTS_HT_O_data.csv': 'HV-UTS-HT'}
    target_names = {'../Data/HV_O_data.csv': 'Hardness (HV)', '../Data/New Data/UTS_HT_ALL.csv': 'UTS'}
    img_files =  {'../Data/HV_O_data.csv': '../Data/Schedule_HV.csv', '../Data/New Data/UTS_HT_ALL.csv': '../Data/New Data/Schedule_HT_ALL.csv'}
    checkpoint_names = {'../Data/New Data/UTS_HT_ALL.csv': 'UTS_HT_ALL'}
    file_s = '../Data/HV_O_data.csv'
    model_path='./CheckPoint_NEW_HT_ALL_RVS'
    log_path = './Logs_NEW_HT_ALL_RVS'

    for name in checkpoint_names.values():
        if not os.path.isdir(f'{model_path}/{name}'):
            os.makedirs(f'{model_path}/{name}')
        if not os.path.isdir(f'{log_path}/{name}'):
            os.makedirs(f'{log_path}/{name}')
    result = {}
    for file_t in ['../Data/New Data/UTS_HT_ALL.csv']:
        print(f'######################{checkpoint_names[file_t]} Traininig########################')
        dataloader = MyDataLoader(source_img=img_files[file_s], orginal_data=file_s, targets=target_names[file_s],
                                    target_img=img_files[file_t], target_data=file_t, t_target=target_names[file_t])
        source_domain_x, source_domain_y, source_domain_class, target_domain_x, target_domain_y, target_domain_class, original_data_src, n_classes = dataloader.get_dataset(if_norm=True)
        model_saving_path = f'{model_path}/{checkpoint_names[file_t]}'
        if not os.path.isdir(model_saving_path):
            os.makedirs(model_saving_path)
        trainer = Trainer(Data.TensorDataset(source_domain_x, source_domain_y, source_domain_class),
                            [target_domain_x, target_domain_y, target_domain_class],
                            opt=opt, nclasses=n_classes, mean=mean, std=std, earlystop_patience=200, model_saving_path=model_saving_path,
                            if_init=True)
        evnet_path = f'./{log_path}/{checkpoint_names[file_t]}'
        if not os.path.isdir(f'./{log_path}/{checkpoint_names[file_t]}'):
            os.makedirs(f'./{log_path}/{checkpoint_names[file_t]}')
        best_src_score, best_src_report, best_tgt_score, best_tgt_report = trainer.train(batch_size=opt.batchSize, n_epochs=opt.nepochs, Log_path=f'./{log_path}/{checkpoint_names[file_t]}')
        result[checkpoint_names[file_t]] = {checkpoint_names[file_t]: {'source_acc': best_src_score, 'source_report': best_src_report, 'target_acc': best_tgt_score, 'target_report': best_tgt_report}}
    json.dump(result, open('./results/C_HT_ALL_New_RVS.json','w'), ensure_ascii = False)


    
