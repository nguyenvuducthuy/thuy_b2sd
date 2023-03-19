import bpy
from bpy.types import ( Panel,
                        Operator,
                        PropertyGroup
                        )
from bpy.props import (StringProperty,
                       BoolProperty,
                       IntProperty,
                       FloatProperty,
                       FloatVectorProperty,
                       EnumProperty,
                       PointerProperty,
                       )
from bpy.app.handlers import persistent
import requests, os, time, math
from PIL import Image
import base64, io
from pprint import pprint
import tempfile
from rembg import remove

# ======
# global
# ======
TEMP_FOLDER = tempfile.gettempdir()

_out_path     = TEMP_FOLDER
_base_image   = "%s/base/base.png"%TEMP_FOLDER

# _prompt            = "1 girls, blue hair, long blue jean , white shirt, empty, black background, short hair"
# _negative_prompt   = "worst quality, low quality:1.2, t-shirt, black shirt, short pant, hat, wide pant, jacket, skirt, long hair"
# _seed              = 88888

_prompt            = "a cute girl, white shirt, red shoes, blue hair, yellow eyes, blue long jean pant"
_negative_prompt   = "(low quality, worst quality:1.4), nsfw"
_seed              = 88888

# ==
# UI
# ==
bl_info = {
    "name": "Blender to Stable Diffusion",
    "author": "anhungxadieu",
    "version": (0, 0, 1),
    "blender": (2, 80, 0),
    "location": "View3D > N",
    "description": "A tool for simplify a workflow from Blender to Stable Diffsion",
    "warning": "",
    "doc_url": "",
    "category": "",
}

class b2sdSettings(PropertyGroup):
    """
    ------------------------------------
    Store properties in the active scene
    ------------------------------------
    """
    isRenAnim : BoolProperty(
        name="is render animation",
        description="b2sd is render animation",
        default = False
        )
    sd_isRembg : BoolProperty(
        name="sd_isRembg",
        description="sd_isRembg",
        default = False
        )
    sd_isImg2img : BoolProperty(
        name="sd_isImg2img",
        description="sd_isImg2img",
        default = False
        )
    sd_prompt : StringProperty(
        name="sd_prompt",
        description="sd_prompt",
        default=_prompt,
        maxlen=1024
        )
    sd_negative_prompt : StringProperty(
        name="sd_negative_prompt",
        description="sd_negative_prompt",
        default=_negative_prompt,
        maxlen=1024
        )
    sd_seed : IntProperty(
        name = "sd_seed",
        description="sd_seed",
        default = _seed,
        min = 10,
        max = 8888888
        )
    sd_out_path : StringProperty(
        name="sd_out_path",
        description="sd_out_path",
        default=_out_path,
        maxlen=1024
        )
    sd_base_image : StringProperty(
        name="sd_base_image",
        description="sd_base_image",
        default=_base_image,
        maxlen=1024
        )

class Button(bpy.types.Operator):
    """
    Make Sure to Select the Armature
    """
    bl_label = "Render"
    bl_idname = "b2sd.main"

    def execute(self, context):
        context = bpy.context
        obj = context.object
        sce = context.scene
        b2sd= sce.b2sd

        print("start b2sd")
        butils = BUtils()
        butils.doit(isanim              = b2sd.isRenAnim,
                    sd_prompt           = b2sd.sd_prompt,
                    sd_negative_prompt  = b2sd.sd_negative_prompt,
                    sd_seed             = b2sd.sd_seed,
                    sd_root_out_path    = b2sd.sd_out_path,
                    sd_isRembg          = b2sd.sd_isRembg,
                    sd_base_image       = b2sd.sd_base_image,
                    sd_isImg2img        = b2sd.sd_isImg2img
                    )

        return {'FINISHED'}

class B2SD_PT_main_pannel(bpy.types.Panel):
    bl_label        = "b2sd"
    bl_idname       = "B2SD_PT_main_pannel"
    bl_space_type   = 'VIEW_3D'
    bl_region_type  = 'UI'
    bl_category     = "anhungxadieu"

    def draw(self, context):
        layout = self.layout

        obj = context.object
        sce = context.scene
        b2sd= sce.b2sd

        row = layout.row()

        # display the properties
        layout.prop(b2sd, "isRenAnim",          text="isRenAnim")
        layout.prop(b2sd, "sd_isRembg",         text="sd_isRembg")
        layout.prop(b2sd, "sd_isImg2img",       text="sd_isImg2img")
        layout.prop(b2sd, "sd_base_image",      text="sd_base_image")
        layout.prop(b2sd, "sd_out_path",        text="sd_out_path")
        layout.prop(b2sd, "sd_prompt",          text="sd_prompt")
        layout.prop(b2sd, "sd_negative_prompt", text="sd_negative_prompt")
        layout.prop(b2sd, "sd_seed",            text="sd_seed")

        row.operator(Button.bl_idname,text=Button.bl_label, icon='MENU_PANEL')

_classes=[
Button,
B2SD_PT_main_pannel,
b2sdSettings
]

def register():
    from bpy.utils import register_class
    for cls in _classes:
        register_class(cls)

    bpy.types.Scene.b2sd = PointerProperty(type=b2sdSettings)

def unregister():
    from bpy.utils import unregister_class
    for cls in reversed(_classes):
        unregister_class(cls)

    del bpy.types.Scene.b2sd

# ==============
# Utils function
# ==============
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

def getDictVal(_dict,key):
    return _dict[key] if key in _dict else ""

def rmbg(input_path):
    # input_path = 'input.png'
    output_path = "%s_rembg.png"%os.path.splitext(input_path)[0]

    _input = Image.open(input_path)
    output = remove(_input)
    output.save(output_path)

    print("rembg img: %s"%output_path)
    return output_path

def run_sd(files, **kwargs):
    """
    main function to connect to api
    kargs:
        sd_base_image = str,
        sd_prompt = str
        sd_negative_prompt = str
        sd_seed=int
        sd_out_path=str
        is_rembg=bool
    """
    # process image
    start = 0
    end   = len(files)
    # end   = 10

    sd_cmd = "txt2img"

    _sd_base_img = ""
    _sd_base_img_path = getDictVal(kwargs,"sd_base_image")
    _sd_isImg2img     = getDictVal(kwargs,"sd_isImg2img")
    if _sd_base_img_path and _sd_isImg2img:
        _sd_base_img = Image.open(_sd_base_img_path)
        _sd_base_img = _sd_base_img.resize((512,512))
        _sd_base_img = raw_b64_img(_sd_base_img)
        sd_cmd = "img2img"

    url = f"http://localhost:7860/sdapi/v1/{sd_cmd}"

    for i in range(start, end):
        # print(files[i])
        cn_img   = raw_b64_img(Image.open(files[i]))
        # cn_mask_img   = b64_img(Image.open(files[i].replace("/in","/in_mask").replace(".png",".jpg")))
        body = {
            "init_images": [_sd_base_img] if _sd_base_img else [],
            "prompt": getDictVal(kwargs,"sd_prompt"),
            "negative_prompt": getDictVal(kwargs,"sd_negative_prompt"),
            "seed": getDictVal(kwargs,"sd_seed") if "sd_seed" in kwargs else 888,
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
                },
                "Cutoff":
                {
                    "args":
                    [
                        {
                            "target_tokens": "white, green, red, blue, yellow, pink",
                            "weight": 2
                        }
                    ]
                }
            }
        }
        res = None
        try:
            res = requests.post(url, json=body).json()
        except Exception as e:
            print(e.message, e.args)

        if not res: return

        if not os.path.exists(getDictVal(kwargs,"sd_out_path")):
            os.makedirs(getDictVal(kwargs,"sd_out_path"))

        img = Image.open(io.BytesIO(base64.b64decode(res["images"][0])))
        sd_out_img = "%s/%s"%(getDictVal(kwargs,"sd_out_path"),os.path.basename(files[i]))
        img.save(sd_out_img)

        if getDictVal(kwargs,"sd_isRembg"):
            rmbg(sd_out_img)

        print("sd_out_img: %s"%sd_out_img)

class BUtils:
    def __init__(self):
        self.DATA = {}

    def displayImg(self, img_path):
        bpy.ops.render.opengl('INVOKE_DEFAULT')
        # load the image into image editor
        try:
            img = bpy.data.images.load(img_path, check_existing=False)
            for window in bpy.data.window_managers['WinMan'].windows:
                for area in window.screen.areas:
                    if area.type == 'IMAGE_EDITOR':
                        area.spaces.active.image = img
        except:
            return print("Couldn't load the image.")

    def bRender(self, outFolder, prefix = "Thuy"):
        if not os.path.exists(outFolder):
            os.makedirs(outFolder)

        s=bpy.context.scene
        timestamp       = int(time.time())
        temp_file       = "%s/"%outFolder+(f"{prefix}_{str(s.frame_current).zfill(4)}.png")
        s.render.filepath = temp_file
        bpy.ops.render.render( #{'dict': "override"},
                                #'INVOKE_DEFAULT',
                                False,            # undo support
                                animation=False,
                                write_still=True
                                )
        # print("render: %s"%temp_file)
        return temp_file

    def doit(self, **kwargs):
        """
        Main Function to connect blender with SD
        isanim : bool
            set it true when you want to render seq
        sd_prompt : str
            sd prompt
        sd_negative_prompt : str
            sd negative prompt
        sd_seed : int
            sd seed
        sd_root_out_path : str
            output folder
        sd_isRembg : bool
            remove bg in sd output img
        sd_base_image : str
            base image for img2img cmd
        """
        root = getDictVal(kwargs,"sd_root_out_path")
        sd_cn_image_folder  = f"{root}/cn_images"
        sd_out_path         = f"{root}/sd_images"
        s=bpy.context.scene
        if not getDictVal(kwargs,"isanim"):
            currentImgPath = self.bRender(sd_cn_image_folder)

            run_sd([currentImgPath],
                sd_prompt           = getDictVal(kwargs,"sd_prompt"),
                sd_negative_prompt  = getDictVal(kwargs,"sd_negative_prompt"),
                sd_seed             = getDictVal(kwargs,"sd_seed"),
                sd_out_path         = sd_out_path,
                sd_isRembg          = getDictVal(kwargs,"sd_isRembg"),
                sd_base_image       = getDictVal(kwargs,"sd_base_image"),
                sd_isImg2img        = getDictVal(kwargs,"sd_isImg2img")
            )

            output_path = currentImgPath.replace(sd_cn_image_folder,sd_out_path)
            if getDictVal(kwargs,"sd_isRembg"):
                output_path = "%s_rembg.png"%os.path.splitext(output_path)[0]
            self.displayImg(output_path)

        else:
            cn_img = []
            for i in range(s.frame_start,s.frame_end):
                s.frame_current = i

                currentImgPath = self.bRender(sd_cn_image_folder)

                run_sd([currentImgPath],
                    sd_prompt           = getDictVal(kwargs,"sd_prompt"),
                    sd_negative_prompt  = getDictVal(kwargs,"sd_negative_prompt"),
                    sd_seed             = getDictVal(kwargs,"sd_seed"),
                    sd_out_path         = sd_out_path,
                    sd_isRembg          = getDictVal(kwargs,"sd_isRembg"),
                    sd_base_image       = getDictVal(kwargs,"sd_base_image"),
                    sd_isImg2img        = getDictVal(kwargs,"sd_isImg2img")
                )

                cn_img.append(currentImgPath)

if __name__ == "__main__":
    register()