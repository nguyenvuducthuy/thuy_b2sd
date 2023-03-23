import bpy
from bpy.types import ( Panel,
                        Operator,
                        PropertyGroup,
                        UIList
                        )
from bpy.props import (StringProperty,
                       BoolProperty,
                       IntProperty,
                       FloatProperty,
                       FloatVectorProperty,
                       EnumProperty,
                       CollectionProperty,
                       PointerProperty
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
_webui_root   = ""

# _prompt            = "1 girls, blue hair, long blue jean , white shirt, empty, black background, short hair"
# _negative_prompt   = "worst quality, low quality:1.2, t-shirt, black shirt, short pant, hat, wide pant, jacket, skirt, long hair"
# _seed              = "88888"

# _prompt            = "a cute girl, white shirt, red shoes, blue hair, yellow eyes, blue long jean pant"
# _negative_prompt   = "(low quality, worst quality:1.4), nsfw"
# _seed              = "88888"

_prompt            = "a cute girl, shirt, shoes, hair, eyes, long jean pant,monochrome, lineart, doodles, sketch, <lora:animeLineartStyle_v20Offset:1>"
_negative_prompt   = "(low quality, worst quality:1.4), nsfw, EasyNegative"
_seed              = "88888"

_listModule = [
    "none",        
    "canny",       
    "depth",       
    "hed",         
    "mlsd",        
    "openpose",    
    "scribble",    
    "seg"         
]

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
    sd_seed : StringProperty(
        name = "sd_seed",
        description="sd_seed",
        default = _seed,
        maxlen=1024
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
    sd_webui_root : StringProperty(
        name="sd_webui_root",
        description="sd_webui_root",
        default="",
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
        scn = context.scene
        b2sd= scn.b2sd
        cn  = scn.custom

        print("start b2sd")
        butils = BUtils()
        butils.doit(isanim              = b2sd.isRenAnim,
                    sd_prompt           = b2sd.sd_prompt,
                    sd_negative_prompt  = b2sd.sd_negative_prompt,
                    sd_seed             = b2sd.sd_seed,
                    sd_root_out_path    = b2sd.sd_out_path,
                    sd_isRembg          = b2sd.sd_isRembg,
                    sd_base_image       = b2sd.sd_base_image,
                    sd_isImg2img        = b2sd.sd_isImg2img,
                    sd_cn_list          = cn
                    )

        return {'FINISHED'}

def traverse_tree(t):
    yield t
    for child in t.children:
        yield from traverse_tree(child)

class CUSTOM_OT_actions(Operator):
    """Move items up and down, add and remove"""
    bl_idname = "custom.list_action"
    bl_label = "List Actions"
    bl_description = "Move items up and down, add and remove"
    bl_options = {'REGISTER'}

    action: bpy.props.EnumProperty(
        items=(
            ('UP', "Up", ""),
            ('DOWN', "Down", ""),
            ('REMOVE', "Remove", ""),
            ('ADD', "Add", "")))

    def random_color(self):
        from mathutils import Color
        from random import random
        return Color((random(), random(), random()))

    def createCole(self, scn, name = "none"):
        coll = scn.collection
        for c in traverse_tree(coll):
            if c.name == name:
                # c.hide_render = not c.hide_render
                return c
        
        cole = bpy.data.collections.new(name)
        scn.collection.children.link(cole)
        return cole

    def invoke(self, context, event):
        scn = context.scene
        idx = scn.custom_index

        try:
            item = scn.custom[idx]
        except IndexError:
            pass
        else:
            if self.action == 'DOWN' and idx < len(scn.custom) - 1:
                item_next = scn.custom[idx+1].name
                scn.custom.move(idx, idx+1)
                scn.custom_index += 1
                info = 'Item "%s" moved to position %d' % (item.name, scn.custom_index + 1)
                self.report({'INFO'}, info)

            elif self.action == 'UP' and idx >= 1:
                item_prev = scn.custom[idx-1].name
                scn.custom.move(idx, idx-1)
                scn.custom_index -= 1
                info = 'Item "%s" moved to position %d' % (item.name, scn.custom_index + 1)
                self.report({'INFO'}, info)

            elif self.action == 'REMOVE':
                item = scn.custom[scn.custom_index]
                info = 'Item %s removed from scene' % (item)
                scn.custom.remove(idx)
                if scn.custom_index == 0:
                    scn.custom_index = 0
                else:
                    scn.custom_index -= 1
                self.report({'INFO'}, info)

        if self.action == 'ADD':
            item = scn.custom.add()
            item.id = len(scn.custom)
            item.sd_module = self.createCole(scn, "none")
            item.name = item.model
            col = self.random_color()
            scn.custom_index = (len(scn.custom)-1)
            info = '%s added to list' % (item.name)
            self.report({'INFO'}, info)
        return {"FINISHED"}

def printItem(self, value):
    context = value
    scn = context.scene
    print(scn.custom[scn.custom_index])

def checkModule(m):
    res = m in _listModule
    if not res:
        print("module %s not in %s"%(m,_listModule))
        return False
    return True

class CUSTOM_UL_items(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            split = layout.split(factor=0.3)
            split.label(text="Control net: %d" % (index))
            split.label(text="module: %s" % (item.sd_module.name if item.sd_module else ""))
            # static method UILayout.icon returns the integer value of the icon ID
            # "computed" for the given RNA object.
            # split.prop(item, "module", text="", emboss=False)
            # split.prop(item, "model", text="", emboss=False)

        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.label(text="", icon_value=layout.icon(mat))

    def invoke(self, context, event):
        pass

class B2SD_PT_main_pannel(bpy.types.Panel):
    bl_label        = "b2sd"
    bl_idname       = "B2SD_PT_main_pannel"
    bl_space_type   = 'VIEW_3D'
    bl_region_type  = 'UI'
    bl_category     = "anhungxadieu"

    def draw(self, context):
        layout = self.layout

        obj = context.object
        scn = context.scene
        b2sd= scn.b2sd

        row = layout.row()

        row.operator(Button.bl_idname,text=Button.bl_label, icon='MENU_PANEL')

        # display the properties
        layout.prop(b2sd, "isRenAnim",          text="isRenAnim")
        layout.prop(b2sd, "sd_isRembg",         text="sd_isRembg")
        layout.prop(b2sd, "sd_isImg2img",       text="sd_isImg2img")
        # layout.prop(b2sd, "sd_webui_root",      text="sd_webui_root")
        layout.prop(b2sd, "sd_base_image",      text="sd_base_image")
        layout.prop(b2sd, "sd_out_path",        text="sd_out_path")
        layout.prop(b2sd, "sd_prompt",          text="sd_prompt")
        layout.prop(b2sd, "sd_negative_prompt", text="sd_negative_prompt")
        layout.prop(b2sd, "sd_seed",            text="sd_seed")

        rows    = 2
        row     = layout.row()
        row.template_list("CUSTOM_UL_items", "custom_def_list", scn, "custom", scn, "custom_index", rows=rows)

        col     = row.column(align=True)
        col.operator(CUSTOM_OT_actions.bl_idname, icon='ADD',       text="").action = 'ADD'
        col.operator(CUSTOM_OT_actions.bl_idname, icon='REMOVE',    text="").action = 'REMOVE'
        col.separator()
        col.operator(CUSTOM_OT_actions.bl_idname, icon='TRIA_UP',   text="").action = 'UP'
        col.operator(CUSTOM_OT_actions.bl_idname, icon='TRIA_DOWN', text="").action = 'DOWN'

        idx     = scn.custom_index
        try:
            cn_item = scn.custom[idx]
            layout.prop(cn_item, "sd_module" ,             text="sd_module")
            layout.prop(cn_item, "model" ,               text="model")
            layout.prop(cn_item, "resize_mode" ,         text="resize_mode")
            layout.prop(cn_item, "weight" ,              text="weight")
            layout.prop(cn_item, "sd_guidance" ,         text="sd_guidance")
            layout.prop(cn_item, "sd_guidance_start" ,   text="sd_guidance_start")
            layout.prop(cn_item, "sd_guidance_end" ,     text="sd_guidance_end")
            layout.prop(cn_item, "sd_guessmode" ,        text="sd_guessmode")
            layout.prop(cn_item, "sd_lowvram" ,          text="sd_lowvram")
        except IndexError:
            pass

class CUSTOM_PG_ControlNetCollection(PropertyGroup):

    # def getControlNetModel(self, context):
    #     scn     = bpy.context.scene
    #     r = scn.sd_webui_root
    #     files = [os.path.join(dp, f) for dp, dn, filenames in os.walk(r) for f in filenames if os.path.splitext(f)[1] == '.safetensors']
    #     res = ()
    #     for i in files:
    #         n = os.path.splitext(os.path.basename(i))[0]
    #         res+=((n, n, ""),)
    #     return res

    def getControlNetModel(self, context):
        return (
            ("control_canny-fp16 [e3fe7712]",    "control_canny-fp16 [e3fe7712]",     ""),
            ("control_depth-fp16 [400750f6]",    "control_depth-fp16 [400750f6]",     ""),
            ("control_hed-fp16 [13fee50b]",      "control_hed-fp16 [13fee50b]",       ""),
            ("control_mlsd-fp16 [e3705cfa]",     "control_mlsd-fp16 [e3705cfa]" ,     ""),
            ("control_openpose-fp16 [9ca67cc5]", "control_openpose-fp16 [9ca67cc5]" , ""),
            ("control_scribble-fp16 [c508311e]", "control_scribble-fp16 [c508311e]" , ""),
            ("control_seg-fp16 [b9c1cc12]",      "control_seg-fp16 [b9c1cc12]",       "")
        )

    def getControlNetModule(self, context):
        return (
            ("none",        "none",     ""),
            ("canny",       "canny",    ""),
            ("depth",       "depth",    ""),
            ("hed",         "hed",      ""),
            ("mlsd",        "mlsd" ,    ""),
            ("openpose",    "openpose" ,""),
            ("scribble",    "scribble" ,""),
            ("seg",         "seg",      "")
        )

    sd_module: PointerProperty(
        name="sd_module",
        type=bpy.types.Collection)

    # module : EnumProperty(
    #     items=getControlNetModule,
    #     name="module",
    #     description="module",
    #     )
    
    model : EnumProperty(
        items=getControlNetModel,
        name="model",
        description="model",
        )
    
    weight : FloatProperty(
        name = "weight",
        description="weight",
        default = 1,
        min = 0,
        max = 1
        )

    resize_mode : EnumProperty(
        items=(
            ("Scale to Fit (Inner Fit)", "Scale to Fit (Inner Fit)", ""),
            ("Just Resize", "Just Resize", ""),
            ("Envelope (Outer Fit)", "Envelope (Outer Fit)", "")
            ),
        name="resize_mode",
        description="resize_mode",
        update=None,
        get=None,
        set=None
        )
    sd_cn_img : StringProperty(
        name="sd_cn_img",
        description="sd_cn_img",
        default=_webui_root,
        maxlen=1024
        )
    sd_guessmode : BoolProperty(
        name="sd_guessmode",
        description="sd_guessmode",
        default = False
        )
    sd_lowvram : BoolProperty(
        name="sd_lowvram",
        description="sd_lowvram",
        default = False
        )
    sd_guidance : FloatProperty(
        name = "sd_guidance",
        description="sd_guidance",
        default = 1,
        min = 0,
        max = 1
        )
    sd_guidance_start : FloatProperty(
        name = "sd_guidance_start",
        description="sd_guidance_start",
        default = 0,
        min = 0,
        max = 1
        )
    sd_guidance_end : FloatProperty(
        name = "sd_guidance_end",
        description="sd_guidance_end",
        default = 1,
        min = 0,
        max = 1
        )
    # "input_image": cn_img,
    # "module": "none",
    # "model": "control_openpose-fp16 [9ca67cc5]",
    # "weight": 1,
    # "resize_mode": "Scale to Fit (Inner Fit)",
    # "lowvram": False,
    # "processor_res": 512,
    # "threshold_a": 64,
    # "threshold_b": 64,
    # "guidance": 1.0,
    # "guidance_start": 0.0,
    # "guidance_end": 1.0,
    # "guessmode": False,

_classes=[
Button,
B2SD_PT_main_pannel,
b2sdSettings,
CUSTOM_OT_actions,
CUSTOM_UL_items,
CUSTOM_PG_ControlNetCollection
]

def register():
    from bpy.utils import register_class
    for cls in _classes:
        register_class(cls)

    bpy.types.Scene.b2sd = PointerProperty(type=b2sdSettings)
    bpy.types.Scene.custom = CollectionProperty(type=CUSTOM_PG_ControlNetCollection)
    bpy.types.Scene.custom_index = IntProperty()

def unregister():
    from bpy.utils import unregister_class
    for cls in reversed(_classes):
        unregister_class(cls)

    del bpy.types.Scene.b2sd
    del bpy.types.Scene.custom
    del bpy.types.Scene.custom_index

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

def parseCN(cn_list):
    res = []
    for i in cn_list:
        cn_cur = {
            "input_image": raw_b64_img(Image.open(i.sd_cn_img)),
            "module": i.sd_module.name,
            "model": i.model,
            "weight": i.weight,
            "resize_mode": i.resize_mode,
            "lowvram": i.sd_lowvram,
            "processor_res": 512,
            "threshold_a": 64,
            "threshold_b": 64,
            "guidance": i.sd_guidance,
            "guidance_start": i.sd_guidance_start,
            "guidance_end": i.sd_guidance_end,
            "guessmode": i.sd_guessmode,
        }
        res.append(cn_cur)
    
    return res

def run_sd(fimg, **kwargs):
    """
    main function to connect to api
    kargs:
        sd_base_image = str,
        sd_prompt = str
        sd_negative_prompt = str
        sd_seed=int
        sd_out_path=str
        is_rembg=bool
        sd_base_image = String
        sd_isImg2img  = bool
        sd_cn_list    = array of cn
    """
    # process image
    # start = 0
    # end   = len(files)
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

    # for i in range(start, end):
        # print(files[i])
        # cn_img   = raw_b64_img(Image.open(files[i]))
        # cn_mask_img   = b64_img(Image.open(files[i].replace("/in","/in_mask").replace(".png",".jpg")))
        
    cn_units = parseCN(getDictVal(kwargs,"sd_cn_list")) if getDictVal(kwargs,"sd_cn_list") else []

    body = {
        "init_images": [_sd_base_img] if _sd_base_img else [],
        "prompt": getDictVal(kwargs,"sd_prompt"),
        "negative_prompt": getDictVal(kwargs,"sd_negative_prompt"),
        "seed": int(getDictVal(kwargs,"sd_seed")) if "sd_seed" in kwargs else 888,
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
                "args": cn_units
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
    sd_out_img = "%s/%s"%(getDictVal(kwargs,"sd_out_path"),os.path.basename(fimg))
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

    def bRender(self, outFolder, prefix = "Thuy", subfix = "openpose"):
        if not os.path.exists(outFolder):
            os.makedirs(outFolder)

        s=bpy.context.scene
        timestamp       = int(time.time())
        temp_file       = "%s/"%outFolder+(f"{prefix}_{subfix}_{str(s.frame_current).zfill(4)}.png")
        s.render.filepath = temp_file
        bpy.ops.render.render( #{'dict': "override"},
                                #'INVOKE_DEFAULT',
                                False,            # undo support
                                animation=False,
                                write_still=True
                                )
        # print("render: %s"%temp_file)
        return temp_file

    def hideColeByname(self, scn, name):
        coll = scn.collection
        for c in traverse_tree(coll):
            if c.name != name:
                c.hide_render = True
            else:
                c.hide_render = False

    def getControlNetList(self, scn, sd_cn_image_folder, sd_cn_list):
        res = []
        for j in range(len(sd_cn_list)):
            module = sd_cn_list[j].sd_module.name if sd_cn_list[j].sd_module else "none"
            self.hideColeByname(scn, module)
            if not checkModule(module): continue
            currentImgPath            = self.bRender(sd_cn_image_folder, subfix = sd_cn_list[j].model.split("-")[0])
            sd_cn_list[j].sd_cn_img    = currentImgPath
            res.append(sd_cn_list[j])
        return res

    def __sd_run(self, kwargs, sd_out_path, sd_cn_list):
        currentImgPath = sd_cn_list[0].sd_cn_img
        run_sd(currentImgPath,
            sd_prompt           = getDictVal(kwargs,"sd_prompt"),
            sd_negative_prompt  = getDictVal(kwargs,"sd_negative_prompt"),
            sd_seed             = getDictVal(kwargs,"sd_seed"),
            sd_out_path         = sd_out_path,
            sd_isRembg          = getDictVal(kwargs,"sd_isRembg"),
            sd_base_image       = getDictVal(kwargs,"sd_base_image"),
            sd_isImg2img        = getDictVal(kwargs,"sd_isImg2img"),
            sd_cn_list          = sd_cn_list
        )
        return currentImgPath

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
        s                   = bpy.context.scene

        if not getDictVal(kwargs,"isanim"):
            sd_cn_list = self.getControlNetList(s, sd_cn_image_folder, getDictVal(kwargs,"sd_cn_list"))

            if not sd_cn_list: return
            currentImgPath = self.__sd_run(kwargs, sd_out_path, sd_cn_list)

            output_path = currentImgPath.replace(sd_cn_image_folder,sd_out_path)
            if getDictVal(kwargs,"sd_isRembg"):
                output_path = "%s_rembg.png"%os.path.splitext(output_path)[0]
            self.displayImg(output_path)

        else:
            for i in range(s.frame_start,s.frame_end):
                s.frame_current = i

                sd_cn_list = self.getControlNetList(s, sd_cn_image_folder, getDictVal(kwargs,"sd_cn_list"))

                if not sd_cn_list: return
                currentImgPath = self.__sd_run(kwargs, sd_out_path, sd_cn_list)

if __name__ == "__main__":
    register()