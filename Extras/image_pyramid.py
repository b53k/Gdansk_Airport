import numpy as np
import matplotlib.pyplot as plt
import cv2

'''source: https://theailearner.com/tag/image-blending-with-pyramid-and-mask/'''

aircraft = cv2.imread('Data/08_11_2023/Frame_53.jpg')
#scene = cv2.imread('Data/08_11_2023/Frame_93.jpg')
scene = cv2.imread('Data/10_11_2023/Frame_9.jpg')
mask = np.load('mask.npy')

mask = cv2.resize(mask, (aircraft.shape[1], aircraft.shape[0]), interpolation = cv2.INTER_NEAREST)
mask = mask.astype(np.float32)
mask = np.repeat(mask[:,:,np.newaxis], 3, axis = 2)
print (f'Mask Shape: {mask.shape}')

# Find the Gaussian pyramid of the two images and the mask
def gaussian_pyramid(img, num_levels):
    lower = img.copy()
    gaussian_pyr = [lower]
    for i in range(num_levels):
        lower = cv2.pyrDown(lower)
        gaussian_pyr.append(np.float32(lower))
    return gaussian_pyr

# Calculate Laplacian Pyramid
def laplacian_pyramid(gaussian_pyr):
    laplacial_top = gaussian_pyr[-1]
    num_levels = len(gaussian_pyr) - 1

    laplacian_pyr = [laplacial_top]
    for i in range(num_levels, 0, -1):
        size = (gaussian_pyr[i - 1].shape[1], gaussian_pyr[i - 1].shape[0])
        gaussian_expanded = cv2.pyrUp(gaussian_pyr[i], dstsize=size)
        laplacian = np.subtract(gaussian_pyr[i-1], gaussian_expanded)
        laplacian_pyr.append(laplacian)
    return laplacian_pyr

# Blend the two images w.r.t the mask
def blend(laplacian_A, laplacian_B, mask_pyr):
    LS = []
    for la, lb, mask in zip(laplacian_A, laplacian_B, mask_pyr):
        ls = lb * mask + la * (1.0 - mask)
        LS.append(ls)
    return LS

# Reconstruct original image
def reconstruct(laplacian_pyr):
    laplacian_top = laplacian_pyr[0]
    laplacian_lst = [laplacian_top]
    num_levels = len(laplacian_pyr) - 1
    for i in range(num_levels):
        size = (laplacian_pyr[i + 1].shape[1], laplacian_pyr[i + 1].shape[0])
        laplacian_expanded = cv2.pyrUp(laplacian_top, dstsize=size)
        laplacian_top = cv2.add(laplacian_pyr[i+1], laplacian_expanded)
        laplacian_lst.append(laplacian_top)
    return laplacian_lst



original_size = aircraft.shape[:2]

num_levels = 5

# Calculate Gaussian and Laplacian for Scene
gaussian_pyr_1 = gaussian_pyramid(scene, num_levels)
laplacian_pyr_1 = laplacian_pyramid(gaussian_pyr_1)

# Calculate Gaussian and Laplacian for Object
gaussian_pyr_2 = gaussian_pyramid(aircraft, num_levels)
laplacian_pyr_2 = laplacian_pyramid(gaussian_pyr_2)

# Calculate the Gaussian pyramid for the mask image and reverse it.
mask_pyr_final = gaussian_pyramid(mask, num_levels)
mask_pyr_final.reverse()

# Blend the images
add_laplace = blend(laplacian_pyr_1,laplacian_pyr_2,mask_pyr_final)

# Reconstruct the images
final  = reconstruct(add_laplace)

#final = reconstruct(add_laplace, original_size)

cv2.imwrite('pyramid2.jpg',final[num_levels])

final_img = cv2.cvtColor(final[num_levels], cv2.COLOR_BGR2RGB)
final_img = final_img.astype(np.uint8)

print (f'Final Image Size: {final_img.shape}')