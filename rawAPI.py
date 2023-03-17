import requests, os, time
from PIL import Image
import base64, io
from pprint import pprint

_cn_image_folder   = "set dir for input control net image"
_out_image_folder  = "set dir for output img"
# _base_image        = "set dir for base image img2img"

# _prompt            = "1 girls, blue hair, long blue jean , white shirt, empty, black background, short hair"
# _negative_prompt   = "worst quality, low quality:1.2, t-shirt, black shirt, short pant, hat, wide pant, jacket, skirt, long hair"
# _seed              = 3298147038

_prompt            = "a cute girl, white shirt, red shoes, blue hair, yellow eyes, blue long jean pant"
_negative_prompt   = "(low quality, worst quality:1.4), nsfw"
_seed              = 3298147038

def b64_img(image: Image):
    buffered = io.BytesIO()
    image.save(buffered, format="PNG")
    img_base64 = 'data:image/png;base64,' + str(base64.b64encode(buffered.getvalue()), 'utf-8')
    return img_base64

def raw_b64_img(image: Image):
    buffered = io.BytesIO()
    image.save(buffered, format="PNG")
    img_base64 = str(base64.b64encode(buffered.getvalue()), 'utf-8')
    return img_base64

def getAllFilesInFolder(folder):
    """
    utils funtion to get all the file in a folder
    folder: Str
        folder to get file in
    """
    res_files = []
    for f in os.listdir(folder):
        res_files.append(os.path.join(folder,f))
    return res_files

def run_sd(files, base_img = None):
    # process image
    start = 0
    end   = len(files)
    # end   = 10

    url = "http://localhost:7860/sdapi/v1/txt2img"

    # if base_img:
    #     base_img = Image.open(_base_image)
    #     base_img = base_img.resize((512,512))

    for i in range(start, end):
        print(files[i])
        cn_img   = raw_b64_img(Image.open(files[i]))
        # cn_mask_img   = b64_img(Image.open(files[i].replace("/in","/in_mask").replace(".png",".jpg")))
        body = {
            # "init_images": [b64_img(base_img)],
            "prompt": _prompt,
            "negative_prompt": _negative_prompt,
            "seed": _seed,
            "subseed": -1,
            "subseed_strength": 0,
            "denoising_strength": 0.75,
            "batch_size": 1,
            "n_iter": 1,
            "steps": 20,
            "cfg_scale": 7,
            "width": 512,
            "height": 512,
            "restore_faces": False,
            "eta": 0,
            "sampler_index": "DPM++ 2M Karras",
            "alwayson_scripts":
            {
                "ControlNet":
                {
                    "args":
                    [
                        {
                            "input_image": cn_img,
                            "module": "none",
                            "model": "control_openpose-fp16 [9ca67cc5]",
                            "weight": 1,
                            "resize_mode": "Scale to Fit (Inner Fit)",
                            "lowvram": False,
                            "processor_res": 512,
                            "threshold_a": 64,
                            "threshold_b": 64,
                            "guidance": 1.0,
                            "guidance_start": 0.0,
                            "guidance_end": 1.0,
                            "guessmode": False,
                        }
                    ]
                }
            }
        }
        res = requests.post(url, json=body).json()
        img = Image.open(io.BytesIO(base64.b64decode(res["images"][0])))
        img.save("%s/%s"%(_out_image_folder,os.path.basename(files[i])))

from bpy.app.handlers import persistent
import bpy

class BUtils:
    def __init__(self):
        pass

    def saveBlenderRender(scene):
        try:
            timestamp       = int(time.time())
            output_filename = f"Thuy_{timestamp}"
            temp_file       = "%s/%s.png"%(_cn_image_folder,output_filename)
        except:
            return print("Couldn't create temp file for image")

        try:
            orig_render_file_format = scene.render.image_settings.file_format
            orig_render_color_mode  = scene.render.image_settings.color_mode
            orig_render_color_depth = scene.render.image_settings.color_depth

            scene.render.image_settings.file_format = 'PNG'
            scene.render.image_settings.color_mode  = 'RGBA'
            scene.render.image_settings.color_depth = '8'

            bpy.data.images['Render Result'].save_render(temp_file)

            scene.render.image_settings.file_format = orig_render_file_format
            scene.render.image_settings.color_mode  = orig_render_color_mode
            scene.render.image_settings.color_depth = orig_render_color_depth
        except:
            return print("Couldn't save rendered image")

        return temp_file

    @staticmethod
    @persistent
    def render_complete_handler(scene):
        is_img_ready = bpy.data.images['Render Result'].has_data

        if is_img_ready:
            cn_img = BUtils.saveBlenderRender(scene)
            run_sd([cn_img])

            # load the image into image editor
            try:
                img = bpy.data.images.load("%s/%s"%(_out_image_folder,os.path.basename(cn_img)), check_existing=False)
                for window in bpy.data.window_managers['WinMan'].windows:
                    for area in window.screen.areas:
                        if area.type == 'IMAGE_EDITOR':
                            area.spaces.active.image = img
            except:
                return print("Couldn't load the image.")
        else:
            print("Rendered image is not ready.")



    def doit(self, isanim = False):
        """
        Function to connet blender wit SD
        isanim: bool
            set it true when you want to render seq
        """

        if not isanim:
            bpy.app.handlers.render_complete.clear()
            bpy.app.handlers.render_complete.append(self.render_complete_handler)
            # bpy.app.handlers.frame_change_post.clear()
            # bpy.app.handlers.frame_change_post.append(self.render_complete_handler)

        else:
            cn_img = []
            s=bpy.context.scene
            for i in range(s.frame_start,s.frame_end):
                s.frame_current = i

                timestamp       = int(time.time())
                # output_filename = f"Thuy_{timestamp}"
                output_filename = f"Thuy_###.png"
                temp_file       = "%s/%s"%(_cn_image_folder,output_filename)

                s.render.filepath = (
                                    temp_file
                                    )
                bpy.ops.render.render( #{'dict': "override"},
                                        #'INVOKE_DEFAULT',
                                        False,            # undo support
                                        animation=isanim,
                                        write_still=True
                                        )

                # Do whatever you want here
                cn_img.append(s.render.frame_path(frame=i))
                run_sd([s.render.frame_path(frame=i)])

butils = BUtils()
butils.doit()
# butils.doit(True)

# CN_img = getAllFilesInFolder(_cn_image_folder)
# run_sd(CN_img)