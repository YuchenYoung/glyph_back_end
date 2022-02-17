import os
import torch
from .CLIP import clip
from PIL import Image
import numpy as np
import cv2
import matplotlib.pyplot as plt
from svglib.svglib import svg2rlg
from reportlab.graphics import renderPM


#@title Control context expansion (number of attention layers to consider)
num_layers =  10 #@param {type:"number"}

def interpret(image, texts, model, device):
    batch_size = texts.shape[0]
    images = image.repeat(batch_size, 1, 1, 1)
    logits_per_image, logits_per_text = model(images, texts)
    probs = logits_per_image.softmax(dim=-1).detach().cpu().numpy()
    index = [i for i in range(batch_size)]
    one_hot = np.zeros((logits_per_image.shape[0], logits_per_image.shape[1]), dtype=np.float32)
    one_hot[torch.arange(logits_per_image.shape[0]), index] = 1
    one_hot = torch.from_numpy(one_hot).requires_grad_(True)
    one_hot = torch.sum(one_hot * logits_per_image)
    model.zero_grad()

    image_attn_blocks = list(dict(model.visual.transformer.resblocks.named_children()).values())
    num_tokens = image_attn_blocks[0].attn_probs.shape[-1]
    R = torch.eye(num_tokens, num_tokens, dtype=image_attn_blocks[0].attn_probs.dtype).to(device)
    R = R.unsqueeze(0).expand(batch_size, num_tokens, num_tokens)
    for i, blk in enumerate(image_attn_blocks):
        if i <= num_layers:
          continue
        grad = torch.autograd.grad(one_hot, [blk.attn_probs], retain_graph=True)[0].detach()
        cam = blk.attn_probs.detach()
        cam = cam.reshape(-1, cam.shape[-1], cam.shape[-1])
        grad = grad.reshape(-1, grad.shape[-1], grad.shape[-1])
        cam = grad * cam
        cam = cam.reshape(batch_size, -1, cam.shape[-1], cam.shape[-1])
        cam = cam.clamp(min=0).mean(dim=1)
        R = R + torch.bmm(cam, R)
    image_relevance = R[:, 0, 1:]

    return image_relevance

clip.clip._MODELS = {
    "ViT-B/32": "https://openaipublic.azureedge.net/clip/models/40d365715913c9da98579312b702a82c18be219cc2a73407c4526f58eba950af/ViT-B-32.pt",
    "ViT-B/16": "https://openaipublic.azureedge.net/clip/models/5806e77cd80f8b59890b7e101eabd078d9fb84e6937f9e85e4ecb61988df416f/ViT-B-16.pt",
}

device = "cuda" if torch.cuda.is_available() else "cpu"
model, preprocess = clip.load("ViT-B/32", device=device, jit=False)

class color:
   PURPLE = '\033[95m'
   CYAN = '\033[96m'
   DARKCYAN = '\033[36m'
   BLUE = '\033[94m'
   GREEN = '\033[92m'
   YELLOW = '\033[93m'
   RED = '\033[91m'
   BOLD = '\033[1m'
   UNDERLINE = '\033[4m'
   END = '\033[0m'


def make_square(im, min_size=224, fill_color=(255,255,255, 0)):
    x, y = im.size
    size = max(min_size, x, y)
    new_im = Image.new('RGBA', (size, size), fill_color)
    new_im.paste(im, (int((size - x) / 2), int((size - y) / 2)))
    return new_im


def show_image_relevance(image_relevance, image, mask_img, ax):
    # create heatmap from mask on image
    def show_cam_on_image(img, mask):
        heatmap = cv2.applyColorMap(np.uint8(255 * mask), cv2.COLORMAP_JET)
        heatmap = np.float32(heatmap) / 255
        cam = heatmap + np.float32(img)
        cam = cam / np.max(cam)
        return cam

    def get_mask_relevance(mask_img):
      mask_relevance = image_relevance
      for i in range(mask_img.shape[0]):
        for j in range(mask_img.shape[1]):
          if mask_img[i,j,0] > 10:
            mask_relevance[i,j] = 0
      return mask_relevance

    def get_average_relevance(mask_relevance):
        return format(mask_relevance.sum()/(mask_relevance!=0).sum(), '.2f')

    # print(type(image))
    # print(type(mask_img))
    mask_img = cv2.resize(np.array(mask_img), (224, 224))
    image_relevance = image_relevance.reshape(1, 1, 7, 7)
    image_relevance = torch.nn.functional.interpolate(image_relevance, size=224, mode='bilinear')
    image_relevance = image_relevance.reshape(224, 224).data.cpu().numpy()
    image_relevance = (image_relevance - image_relevance.min()) / (image_relevance.max() - image_relevance.min())

    image = image[0].permute(1, 2, 0).data.cpu().numpy()
    image = (image - image.min()) / (image.max() - image.min())
    vis = show_cam_on_image(image, get_mask_relevance(mask_img))
    vis = np.uint8(255 * vis)
    vis = cv2.cvtColor(np.array(vis), cv2.COLOR_RGB2BGR)
    ax.imshow(vis)
    return(get_average_relevance(get_mask_relevance(mask_img)))
    

def save_imgs(svg_list):
    svg_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'CLIP/svg')
    svg_num = len(svg_list)
    print(f"svgnum is {svg_num}")
    for i in range(svg_num):
        cur_svg_dir = os.path.join(svg_dir, f'img_{i}.svg')
        cur_png_dir = os.path.join(svg_dir, f'img_{i}.png')
        with open(cur_svg_dir, 'w') as f:
            f.write(svg_list[i])
        drawing = svg2rlg(cur_svg_dir)
        renderPM.drawToFile(drawing, cur_png_dir, fmt='PNG')     


def map_data(header, img_num, rel_matrix):
    print(rel_matrix)
    header_mapped = np.zeros(len(header), dtype=np.int)
    svg_mapped = np.zeros(img_num, dtype=np.int)
    map_res = {}
    map_cnt = 0
    loop_cnt = 0
    while map_cnt < len(header) and loop_cnt < 50:
        loop_cnt += 1
        for j in range(len(header)):
            if header_mapped[j] > 0:
                continue
            max_pos = -1
            max_val = -1
            for i in range(img_num):
                if svg_mapped[i]:
                    continue
                if rel_matrix[i][j] > max_val:
                    max_val = rel_matrix[i][j]
                    max_pos = i
            # print(f"j {j} maxpos {max_pos} maxval {max_val}")
            max_available = True
            for k in range(len(header)):
                if not header_mapped[k] and rel_matrix[max_pos][k] >= max_val and k != j:
                    max_available = False
                    break
            # print("======")
            if max_available:
                map_res[header[j]] = max_pos
                header_mapped[j] = 1
                svg_mapped[max_pos] = 1
                map_cnt += 1
                # print(map_res)
                break
    print(map_res)
    return map_res

def clip_main(content, header, svg_list):
    texts = []
    for i in range(len(header)):
        texts.append(f"a {content} with {header[i]}")
    svg_part = len(svg_list) - 1
    save_imgs(svg_list)

    svg_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'CLIP/svg')
    
    img = preprocess(make_square(Image.open(os.path.join(svg_dir, 'img_0.png')))).unsqueeze(0).to(device)
    fig, axs=plt.subplots(svg_part+1, len(header), sharex='col', sharey='row', figsize=(2*len(header), 2.5*svg_part))

    rel_matrix = np.zeros((svg_part + 1, len(header)), dtype=np.float)

    for i in range(0, svg_part + 1):
        test_image = Image.open(os.path.join(svg_dir, f'img_{i}.png'))
        new_image = np.array(make_square(test_image))
        for j in range(len(header)):
            text = clip.tokenize(texts[j]).to(device)
            R_image = interpret(model=model, image=img, texts=text, device=device)
            img_rel = show_image_relevance(R_image, img, new_image, axs[i-1, j])
            rel_matrix[i][j] = img_rel
            axs[i-1,j].text(0.5, 0.1, img_rel, horizontalalignment='center', verticalalignment='center', transform=axs[i-1,j].transAxes)
            axs[i-1,j].set_title(header[j])
    
    return map_data(header, svg_part + 1, rel_matrix)
    