# -*- coding: utf-8 -*-
'''
@paper: GAN Prior Embedded Network for Blind Face Restoration in the Wild (CVPR2021)
@author: yangxy (yangtao9009@gmail.com)
'''
import cv2
import time, math
import numpy as np
import __init_paths
from face_detect.retinaface_detection import RetinaFaceDetection
from face_parse.face_parsing import FaceParse
from face_model.face_gan import FaceGAN
from sr_model.real_esrnet2 import RealESRNet #### yerang edit
from align_faces import warp_and_crop_face, get_reference_facial_points

class FaceEnhancement(object):
    def __init__(self, base_dir='./', in_size=512, out_size=None, model=None, use_sr=True, sr_model=None, sr_scale=2, tile_size=0, channel_multiplier=2, narrow=1, key=None, device='cuda'):
        self.facedetector = RetinaFaceDetection(base_dir, device)
        self.facegan = FaceGAN(base_dir, in_size, out_size, model, channel_multiplier, narrow, key, device=device)
        self.srmodel =  RealESRNet(base_dir, sr_model, sr_scale, tile_size, device=device)
        self.faceparser = FaceParse(base_dir, device=device)
        self.use_sr = use_sr
        self.in_size = in_size
        self.out_size = in_size if out_size is None else out_size
        self.threshold = 0.8

        # the mask for pasting restored faces back
        self.mask = np.zeros((512, 512), np.float32)
        cv2.rectangle(self.mask, (26, 26), (486, 486), (1, 1, 1), -1, cv2.LINE_AA)
        self.mask = cv2.GaussianBlur(self.mask, (101, 101), 11)
        self.mask = cv2.GaussianBlur(self.mask, (101, 101), 11)

        self.kernel = np.array((
                [0.0625, 0.125, 0.0625],
                [0.125, 0.25, 0.125],
                [0.0625, 0.125, 0.0625]), dtype="float32")

        # get the reference 5 landmarks position in the crop settings
        default_square = True
        inner_padding_factor = 0.25
        outer_padding = (0, 0)
        self.reference_5pts = get_reference_facial_points(
                (self.in_size, self.in_size), inner_padding_factor, outer_padding, default_square)

    def mask_postprocess(self, mask, thres=20):
        mask[:thres, :] = 0; mask[-thres:, :] = 0
        mask[:, :thres] = 0; mask[:, -thres:] = 0
        mask = cv2.GaussianBlur(mask, (101, 101), 11)
        mask = cv2.GaussianBlur(mask, (101, 101), 11)
        return mask.astype(np.float32)

#     def process(self, img, aligned=False):
#         orig_faces, enhanced_faces = [], []
#         if aligned:
#             ef = self.facegan.process(img)            
#             orig_faces.append(img)
#             enhanced_faces.append(ef)

#             if self.use_sr:
#                 ef = self.srmodel.process(ef)

#             return ef, orig_faces, enhanced_faces

#         if self.use_sr:

#             print('srmodel ==============')
#             start = time.time()
#             math.factorial(100000)


#             img_sr = self.srmodel.process(img)

#             end = time.time()
#             print('===========================================')
#             print(f"{end - start:.5f} sec")
#             print('===========================================')

#             if img_sr is not None:
#                 img = cv2.resize(img, img_sr.shape[:2][::-1])

#         print('facedetector ==============')
#         start = time.time()
#         math.factorial(100000)

#         facebs, landms = self.facedetector.detect(img)

#         end = time.time()
#         print('===========================================')
#         print(f"{end - start:.5f} sec")
#         print('===========================================')


#         height, width = img.shape[:2]
#         full_mask = np.zeros((height, width), dtype=np.float32)
#         full_img = np.zeros(img.shape, dtype=np.uint8)

#         for i, (faceb, facial5points) in enumerate(zip(facebs, landms)):
#             if faceb[4]<self.threshold: continue
#             fh, fw = (faceb[3]-faceb[1]), (faceb[2]-faceb[0])

#             facial5points = np.reshape(facial5points, (2, 5))

#             of, tfm_inv = warp_and_crop_face(img, facial5points, reference_pts=self.reference_5pts, crop_size=(self.in_size, self.in_size))

#             # enhance the face

#             print('facegan ==============')
#             start = time.time()
#             math.factorial(100000)


#             ef = self.facegan.process(of)

#             end = time.time()
#             print('===========================================')
#             print(f"{end - start:.5f} sec")
#             print('===========================================')

#             orig_faces.append(of)
#             enhanced_faces.append(ef)

#             #tmp_mask = self.mask
#             tmp_mask = self.mask_postprocess(self.faceparser.process(ef)[0]/255.)
#             tmp_mask = cv2.resize(tmp_mask, (self.in_size, self.in_size))
#             tmp_mask = cv2.warpAffine(tmp_mask, tfm_inv, (width, height), flags=3)

#             if min(fh, fw)<100: # gaussian filter for small faces
#                 ef = cv2.filter2D(ef, -1, self.kernel)

#             if self.in_size!=self.out_size:
#                 ef = cv2.resize(ef, (self.in_size, self.in_size))
#             tmp_img = cv2.warpAffine(ef, tfm_inv, (width, height), flags=3)

#             mask = tmp_mask - full_mask
#             full_mask[np.where(mask>0)] = tmp_mask[np.where(mask>0)]
#             full_img[np.where(mask>0)] = tmp_img[np.where(mask>0)]

#         full_mask = full_mask[:, :, np.newaxis]
#         if self.use_sr and img_sr is not None:
#             img = cv2.convertScaleAbs(img_sr*(1-full_mask) + full_img*full_mask)
#         else:
#             img = cv2.convertScaleAbs(img*(1-full_mask) + full_img*full_mask)

#         return img, orig_faces, enhanced_faces



    def process(self, imgs, aligned=False):
        orig_faces, enhanced_faces = [], []
        
        
        if aligned: ### 일단 무시
            ef = self.facegan.process(img)            
            orig_faces.append(img)
            enhanced_faces.append(ef)

            if self.use_sr:
                ef = self.srmodel.process(ef)

            return ef, orig_faces, enhanced_faces

        # =============================
        # bach inference 
        # =============================
        
        if self.use_sr:            
            print('imgs.shape===',imgs.shape)
            img_sr_arr = self.srmodel.process(imgs) # <<<<<<<<<<<<<<<<<<<<<<<< 여기에 이미지 여러개 넣고 싶음
            print('img_sr_arr.shape===',img_sr_arr.shape)
        # =============================
        # 이미지 한장한장 
        # =============================       
        
        bbox_arr = np.load('/data/GCP_Backup/yerang/bbox_arr.npy')
        kpss_arr = np.load('/data/GCP_Backup/yerang/kpss_arr.npy')
        
        result_imgs = []
        #for img, img_sr in zip(imgs, img_sr_arr):
        for idx, (img, img_sr) in enumerate(zip(imgs, img_sr_arr)):
            
            facebs = bbox_arr[idx] ##
            landms = kpss_arr[idx] ##
            new_ratio_x, new_ratio_y = 1, 1 ##
            
            if self.use_sr and img_sr is not None:
                new_ratio_x = img_sr.shape[0]/img.shape[0] ##
                new_ratio_y = img_sr.shape[1]/img.shape[1] ##
                
                img = cv2.resize(img, img_sr.shape[:2][::-1])


            #facebs, landms = self.facedetector.detect(img) ####################
   
            

            height, width = img.shape[:2]
            full_mask = np.zeros((height, width), dtype=np.float32)
            full_img = np.zeros(img.shape, dtype=np.uint8)

            for i, (faceb, facial5points) in enumerate(zip(facebs, landms)):
                print('faceb[4], self.threshold', faceb[4], self.threshold)
                if faceb[4]<self.threshold: continue
                fh, fw = (faceb[3]-faceb[1]), (faceb[2]-faceb[0])

                #facial5points = np.reshape(facial5points, (2, 5))
                faceb[0], faceb[2] = faceb[0]*new_ratio_x, faceb[2]*new_ratio_x
                faceb[1], faceb[3] = faceb[1]*new_ratio_y, faceb[3]*new_ratio_y
                
                facial5points = np.transpose(facial5points).flatten()
                facial5points = np.reshape(facial5points,(2,5))
                
                facial5points[0] = facial5points[0]*new_ratio_x
                facial5points[1] = facial5points[1]*new_ratio_y
                
                print('faceb', faceb)
                print('facial5points', facial5points)
                

                of, tfm_inv = warp_and_crop_face(img, facial5points, reference_pts=self.reference_5pts, crop_size=(self.in_size, self.in_size))

                # enhance the face 
                ef = self.facegan.process(of)             #############################
                orig_faces.append(of)
                enhanced_faces.append(ef)

                #tmp_mask = self.mask
                tmp_mask = self.mask_postprocess(self.faceparser.process(ef)[0]/255.)
                tmp_mask = cv2.resize(tmp_mask, (self.in_size, self.in_size))
                tmp_mask = cv2.warpAffine(tmp_mask, tfm_inv, (width, height), flags=3)

                if min(fh, fw)<100: # gaussian filter for small faces
                    ef = cv2.filter2D(ef, -1, self.kernel)

                if self.in_size!=self.out_size:
                    ef = cv2.resize(ef, (self.in_size, self.in_size))
                tmp_img = cv2.warpAffine(ef, tfm_inv, (width, height), flags=3)

                mask = tmp_mask - full_mask
                full_mask[np.where(mask>0)] = tmp_mask[np.where(mask>0)]
                full_img[np.where(mask>0)] = tmp_img[np.where(mask>0)]

            full_mask = full_mask[:, :, np.newaxis]
            if self.use_sr and img_sr is not None:
                img = cv2.convertScaleAbs(img_sr*(1-full_mask) + full_img*full_mask)
            else:
                img = cv2.convertScaleAbs(img*(1-full_mask) + full_img*full_mask)
                
            result_imgs.append(img)

        return result_imgs, orig_faces, enhanced_faces
