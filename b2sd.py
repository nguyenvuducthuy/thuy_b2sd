# from logging import exception
# from ntpath import join
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
# from bpy.app.handlers import persistent
import requests, os, time, math, sys
import base64, io
import tempfile
import re, json
from pprint import pprint

try:
    from rembg import remove
    from PIL import Image
except Exception as e:
    print(e)
    remove = None
    Image = None

# ======
# global
# ======
bl_info = {
    "name": "Blender to Stable Diffusion",
    "author": "anhungxadieu",
    "version": (0, 0, 1),
    "blender": (2, 80, 0),
    "location": "View3D > N",
    "description": "A tool for simplify a workflow from Blender to Stable Diffsion",
    "warning": "",
    "doc_url": "https://github.com/nguyenvuducthuy/thuy_b2sd/wiki",
    "category": "anhungxadieu",
}

TEMP_FOLDER = tempfile.gettempdir()
# TEMP_FOLDER = "J:/thuy_blender/B2SD/OUT/tmp/img2img"

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

_input_parser = """
a cute girl, white shirt with green tie, red shoes, blue hair, yellow eyes, pink skirt Negative prompt: (low quality, worst quality:1.4), nsfw Steps: 20, Sampler: DPM++ 2M Karras, CFG scale: 7, Seed: 88888, Size: 512x512, Model hash: 0b9c8fd3a8, Model: macaronMix_v10, Denoising strength: 0.75, Mask blur: 4, ControlNet-0 Enabled: True, ControlNet-0 Module: hed, ControlNet-0 Model: control_hed-fp16 [13fee50b], ControlNet-0 Weight: 1, ControlNet-0 Guidance Start: 0, ControlNet-0 Guidance End: 1
"""
_input_parser_regex = r'((?P<prompt>(.*))(?P<nprompt>(Negative prompt.*))|)(?P<steps>Steps.*)(?P<sampler_index>Sampler.*)(?P<cfg_scale>CFG scale.*)(?P<seed>Seed.*)(?P<size>Size.*)(?P<modelhash>Model hash.*)(?P<model>Model.*)(?P<denoising_strength>Denoising strength.*)(?P<del>Mask blur)'

_list_sd_Module = [
    "none",
    "canny",
    "depth",
    "hed",
    "mlsd",
    "openpose",
    "scribble",
    "seg"
]

_list_sd_Model = [
    "control_canny-fp16 [e3fe7712]",
    "control_depth-fp16 [400750f6]",
    "control_hed-fp16 [13fee50b]",
    "control_mlsd-fp16 [e3705cfa]",
    "control_openpose-fp16 [9ca67cc5]",
    "control_scribble-fp16 [c508311e]",
    "control_seg-fp16 [b9c1cc12]"
]

# ====
# DATA
# ====
_segData = {
    "idx": [
        "1",
        "2",
        "3",
        "4",
        "5",
        "6",
        "7",
        "8",
        "9",
        "10",
        "11",
        "12",
        "13",
        "14",
        "15",
        "16",
        "17",
        "18",
        "19",
        "20",
        "21",
        "22",
        "23",
        "24",
        "25",
        "26",
        "27",
        "28",
        "29",
        "30",
        "31",
        "32",
        "33",
        "34",
        "35",
        "36",
        "37",
        "38",
        "39",
        "40",
        "41",
        "42",
        "43",
        "44",
        "45",
        "46",
        "47",
        "48",
        "49",
        "50",
        "51",
        "52",
        "53",
        "54",
        "55",
        "56",
        "57",
        "58",
        "59",
        "60",
        "61",
        "62",
        "63",
        "64",
        "65",
        "66",
        "67",
        "68",
        "69",
        "70",
        "71",
        "72",
        "73",
        "74",
        "75",
        "76",
        "77",
        "78",
        "79",
        "80",
        "81",
        "82",
        "83",
        "84",
        "85",
        "86",
        "87",
        "88",
        "89",
        "90",
        "91",
        "92",
        "93",
        "94",
        "95",
        "96",
        "97",
        "98",
        "99",
        "100",
        "101",
        "102",
        "103",
        "104",
        "105",
        "106",
        "107",
        "108",
        "109",
        "110",
        "111",
        "112",
        "113",
        "114",
        "115",
        "116",
        "117",
        "118",
        "119",
        "120",
        "121",
        "122",
        "123",
        "124",
        "125",
        "126",
        "127",
        "128",
        "129",
        "130",
        "131",
        "132",
        "133",
        "134",
        "135",
        "136",
        "137",
        "138",
        "139",
        "140",
        "141",
        "142",
        "143",
        "144",
        "145",
        "146",
        "147",
        "148",
        "149",
        "150"
    ],
    "color": [
        "(120, 120, 120)",
        "(180, 120, 120)",
        "(6, 230, 230)",
        "(80, 50, 50)",
        "(4, 200, 3)",
        "(120, 120, 80)",
        "(140, 140, 140)",
        "(204, 5, 255)",
        "(230, 230, 230)",
        "(4, 250, 7)",
        "(224, 5, 255)",
        "(235, 255, 7)",
        "(150, 5, 61)",
        "(120, 120, 70)",
        "(8, 255, 51)",
        "(255, 6, 82)",
        "(143, 255, 140)",
        "(204, 255, 4)",
        "(255, 51, 7)",
        "(204, 70, 3)",
        "(0, 102, 200)",
        "(61, 230, 250)",
        "(255, 6, 51)",
        "(11, 102, 255)",
        "(255, 7, 71)",
        "(255, 9, 224)",
        "(9, 7, 230)",
        "(220, 220, 220)",
        "(255, 9, 92)",
        "(112, 9, 255)",
        "(8, 255, 214)",
        "(7, 255, 224)",
        "(255, 184, 6)",
        "(10, 255, 71)",
        "(255, 41, 10)",
        "(7, 255, 255)",
        "(224, 255, 8)",
        "(102, 8, 255)",
        "(255, 61, 6)",
        "(255, 194, 7)",
        "(255, 122, 8)",
        "(0, 255, 20)",
        "(255, 8, 41)",
        "(255, 5, 153)",
        "(6, 51, 255)",
        "(235, 12, 255)",
        "(160, 150, 20)",
        "(0, 163, 255)",
        "(140, 140, 140)",
        "(0250, 10, 15)",
        "(20, 255, 0)",
        "(31, 255, 0)",
        "(255, 31, 0)",
        "(255, 224, 0)",
        "(153, 255, 0)",
        "(0, 0, 255)",
        "(255, 71, 0)",
        "(0, 235, 255)",
        "(0, 173, 255)",
        "(31, 0, 255)",
        "(11, 200, 200)",
        "(255 ,82, 0)",
        "(0, 255, 245)",
        "(0, 61, 255)",
        "(0, 255, 112)",
        "(0, 255, 133)",
        "(255, 0, 0)",
        "(255, 163, 0)",
        "(255, 102, 0)",
        "(194, 255, 0)",
        "(0, 143, 255)",
        "(51, 255, 0)",
        "(0, 82, 255)",
        "(0, 255, 41)",
        "(0, 255, 173)",
        "(10, 0, 255)",
        "(173, 255, 0)",
        "(0, 255, 153)",
        "(255, 92, 0)",
        "(255, 0, 255)",
        "(255, 0, 245)",
        "(255, 0, 102)",
        "(255, 173, 0)",
        "(255, 0, 20)",
        "(255, 184, 184)",
        "(0, 31, 255)",
        "(0, 255, 61)",
        "(0, 71, 255)",
        "(255, 0, 204)",
        "(0, 255, 194)",
        "(0, 255, 82)",
        "(0, 10, 255)",
        "(0, 112, 255)",
        "(51, 0, 255)",
        "(0, 194, 255)",
        "(0, 122, 255)",
        "(0, 255, 163)",
        "(255, 153, 0)",
        "(0, 255, 10)",
        "(255, 112, 0)",
        "(143, 255, 0)",
        "(82, 0, 255)",
        "(163, 255, 0)",
        "(255, 235, 0)",
        "(8, 184, 170)",
        "(133, 0, 255)",
        "(0, 255, 92)",
        "(184, 0, 255)",
        "(255, 0, 31)",
        "(0, 184, 255)",
        "(0, 214, 255)",
        "(255, 0, 112)",
        "(92, 255, 0)",
        "(0, 224, 255)",
        "(112, 224, 255)",
        "(70, 184, 160)",
        "(163, 0, 255)",
        "(153, 0, 255)",
        "(71, 255, 0)",
        "(255, 0, 163)",
        "(255, 204, 0)",
        "(255, 0, 143)",
        "(0, 255, 235)",
        "(133, 255, 0)",
        "(255, 0, 235)",
        "(245, 0, 255)",
        "(255, 0, 122)",
        "(255, 245, 0)",
        "(10, 190, 212)",
        "(214, 255, 0)",
        "(0, 204, 255)",
        "(20, 0, 255)",
        "(255, 255, 0)",
        "(0, 153, 255)",
        "(0, 41, 255)",
        "(0, 255, 204)",
        "(41, 0, 255)",
        "(41, 255, 0)",
        "(173, 0, 255)",
        "(0, 245, 255)",
        "(71, 0, 255)",
        "(122, 0, 255)",
        "(0, 255, 184)",
        "(0, 92, 255)",
        "(184, 255, 0)",
        "(0, 133, 255)",
        "(255, 214, 0)",
        "(25, 194, 194)",
        "(102, 255, 0)",
        "(92, 0, 255)"
    ],
    "name": [
        "wall",
        "building;edifice",
        "sky",
        "floor;flooring",
        "tree",
        "ceiling",
        "road;route",
        "bed",
        "windowpane;window",
        "grass",
        "cabinet",
        "sidewalk;pavement",
        "person;individual;someone;somebody;mortal;soul",
        "earth;ground",
        "door;double;door",
        "table",
        "mountain;mount",
        "plant;flora;plant;life",
        "curtain;drape;drapery;mantle;pall",
        "chair",
        "car;auto;automobile;machine;motorcar",
        "water",
        "painting;picture",
        "sofa;couch;lounge",
        "shelf",
        "house",
        "sea",
        "mirror",
        "rug;carpet;carpeting",
        "field",
        "armchair",
        "seat",
        "fence;fencing",
        "desk",
        "rock;stone",
        "wardrobe;closet;press",
        "lamp",
        "bathtub;bathing;tub;bath;tub",
        "railing;rail",
        "cushion",
        "base;pedestal;stand",
        "box",
        "column;pillar",
        "signboard;sign",
        "chest;of;drawers;chest;bureau;dresser",
        "counter",
        "sand",
        "sink",
        "skyscraper",
        "fireplace;hearth;open;fireplace",
        "refrigerator;icebox",
        "grandstand;covered;stand",
        "path",
        "stairs;steps",
        "runway",
        "case;display;case;showcase;vitrine",
        "pool;table;billiard;table;snooker;table",
        "pillow",
        "screen;door;screen",
        "stairway;staircase",
        "river",
        "bridge;span",
        "bookcase",
        "blind;screen",
        "coffee;table;cocktail;table",
        "toilet;can;commode;crapper;pot;potty;stool;throne",
        "flower",
        "book",
        "hill",
        "bench",
        "countertop",
        "stove;kitchen;stove;range;kitchen;range;cooking;stove",
        "palm;palm;tree",
        "kitchen;island",
        "computer;computing;machine;computing;device;data;processor;electronic;computer;information;processing;system",
        "swivel;chair",
        "boat",
        "bar",
        "arcade;machine",
        "hovel;hut;hutch;shack;shanty",
        "bus;autobus;coach;charabanc;double-decker;jitney;motorbus;motorcoach;omnibus;passenger;vehicle",
        "towel",
        "light;light;source",
        "truck;motortruck",
        "tower",
        "chandelier;pendant;pendent",
        "awning;sunshade;sunblind",
        "streetlight;street;lamp",
        "booth;cubicle;stall;kiosk",
        "television;television;receiver;television;set;tv;tv;set;idiot;box;boob;tube;telly;goggle;box",
        "airplane;aeroplane;plane",
        "dirt;track",
        "apparel;wearing;apparel;dress;clothes",
        "pole",
        "land;ground;soil",
        "bannister;banister;balustrade;balusters;handrail",
        "escalator;moving;staircase;moving;stairway",
        "ottoman;pouf;pouffe;puff;hassock",
        "bottle",
        "buffet;counter;sideboard",
        "poster;posting;placard;notice;bill;card",
        "stage",
        "van",
        "ship",
        "fountain",
        "conveyer;belt;conveyor;belt;conveyer;conveyor;transporter",
        "canopy",
        "washer;automatic;washer;washing;machine",
        "plaything;toy",
        "swimming;pool;swimming;bath;natatorium",
        "stool",
        "barrel;cask",
        "basket;handbasket",
        "waterfall;falls",
        "tent;collapsible;shelter",
        "bag",
        "minibike;motorbike",
        "cradle",
        "oven",
        "ball",
        "food;solid;food",
        "step;stair",
        "tank;storage;tank",
        "trade;name;brand;name;brand;marque",
        "microwave;microwave;oven",
        "pot;flowerpot",
        "animal;animate;being;beast;brute;creature;fauna",
        "bicycle;bike;wheel;cycle",
        "lake",
        "dishwasher;dish;washer;dishwashing;machine",
        "screen;silver;screen;projection;screen",
        "blanket;cover",
        "sculpture",
        "hood;exhaust;hood",
        "sconce",
        "vase",
        "traffic;light;traffic;signal;stoplight",
        "tray",
        "ashcan;trash;can;garbage;can;wastebin;ash;bin;ash-bin;ashbin;dustbin;trash;barrel;trash;bin",
        "fan",
        "pier;wharf;wharfage;dock",
        "crt;screen",
        "plate",
        "monitor;monitoring;device",
        "bulletin;board;notice;board",
        "shower",
        "radiator",
        "glass;drinking;glass",
        "clock",
        "flag"
    ]
}

# ========
# OPERATOR
# ========
class SD_render_op(Operator):
    """
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
                    sd_args             = b2sd.sd_args,
                    sd_cn_list          = cn
                    )

        return {'FINISHED'}

class CN_Utils_segmentator_op(Operator):
    """
    Make Sure to Select the Armature
    """
    bl_label = "segmenting"
    bl_idname = "b2sd.segmenting"

    def execute(self, context):
        context = bpy.context
        obj = context.object
        scn = context.scene
        b2sd= scn.b2sd

        objs = bpy.context.selected_objects
        print(b2sd.segmentColor)

        for i in objs:
            obj = i
            mesh = obj.data

            if not mesh.vertex_colors:
                mesh.vertex_colors.new()

            color_layer = mesh.vertex_colors["Col"]

            i = 0
            r, g, b = [float(x)/255 for x in b2sd.segmentColor.replace("(","").replace(")","").split(",")]
            # print(r,g,b)
            for poly in mesh.polygons:
                for idx in poly.loop_indices:
                    color_layer.data[i].color = (r, g, b, 1.0)
                    i += 1

            # set to vertex paint mode to see the result
            # bpy.ops.object.mode_set(mode='VERTEX_PAINT')
        
        return {'FINISHED'}

# ==
# UI
# ==
class B2SD_PG_b2sdSettings(PropertyGroup):
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
    sd_args : StringProperty(
        name="sd_args",
        description="sd_args",
        default=_input_parser,
        maxlen=1024
        )

    def getSegmentColor(self, context):
        # dataFile = os.path.join(sys.path[0], "segmentator_data.json")
        # data = None
        # with open(dataFile) as json_file:
        #     data = json.load(json_file)
        data = _segData
        res = ()
        for i,j in zip(data["name"],data["color"]):
            res += ((j, i, ""),)
        return res

    segmentColor : EnumProperty(
        name="segmentColor",
        description="",
        items=getSegmentColor
        )

class B2SD_OT_actions(Operator):
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

    def traverse_tree(self,t):
        yield t
        for child in t.children:
            yield from self.traverse_tree(child)

    def createCole(self, scn, name = "none"):
        coll = scn.collection
        for c in self.traverse_tree(coll):
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
            # item.render_collection = self.createCole(scn, "none")
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

class B2SD_UL_items(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            split = layout.split(factor=0.3)
            split.label(text="Control net: %d" % (index))
            split.label(text="%s" % re.search(r'_(?P<model>.*?)-',item.model)["model"])
            # static method UILayout.icon returns the integer value of the icon ID
            # "computed" for the given RNA object.
            # split.prop(item, "module", text="", emboss=False)
            # split.prop(item, "model", text="", emboss=False)

        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.label(text="", icon_value=layout.icon(mat))

    def invoke(self, context, event):
        pass

class B2SD_PT_main_pannel(Panel):
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

        row.operator(SD_render_op.bl_idname,text=SD_render_op.bl_label, icon='MENU_PANEL')

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
        layout.prop(b2sd, "sd_args",            text="sd_args")

        rows    = 2
        row     = layout.row()
        row.template_list("B2SD_UL_items", "custom_def_list", scn, "custom", scn, "custom_index", rows=rows)

        col     = row.column(align=True)
        col.operator(B2SD_OT_actions.bl_idname, icon='ADD',       text="").action = 'ADD'
        col.operator(B2SD_OT_actions.bl_idname, icon='REMOVE',    text="").action = 'REMOVE'
        col.separator()
        col.operator(B2SD_OT_actions.bl_idname, icon='TRIA_UP',   text="").action = 'UP'
        col.operator(B2SD_OT_actions.bl_idname, icon='TRIA_DOWN', text="").action = 'DOWN'

        idx     = scn.custom_index
        try:
            cn_item = scn.custom[idx]
            # layout.prop(cn_item, "render_collection" ,   text="render_collection")
            layout.prop(cn_item, "sd_invert_image" ,     text="sd_invert_image")
            layout.prop(cn_item, "module" ,              text="module")
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

class B2SD_PT_CNSegmentator(Panel):
    bl_label = "Utils_segmentator"
    bl_category = "anhungxadieu"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_options = {"DEFAULT_CLOSED"}
    # bl_parent_id = "B2SD_PT_main_pannel"

    def draw(self, context):
        layout = self.layout

        obj = context.object
        scn = context.scene
        b2sd= scn.b2sd

        row = layout.row()

        # row.prop_search(b2sd, "segmentColor", b2sd, "segmentColor")
        row.prop(b2sd, "segmentColor")
        row.operator(CN_Utils_segmentator_op.bl_idname,text=CN_Utils_segmentator_op.bl_label, icon='MENU_PANEL')

class B2SD_PG_ControlNetCollection(PropertyGroup):
    """
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
    """

    def getControlNetModel(self, context):
        res = ()
        for i in _list_sd_Model:
            res += ((i, i, ""),)
        return res

    def getControlNetModule(self, context):
        res = ()
        for i in _list_sd_Module:
            res += ((i, i, ""),)
        return res

    render_collection: PointerProperty(
        name="render_collection",
        type=bpy.types.Collection)
    module : EnumProperty(
        items=getControlNetModule,
        name="module",
        description="module",
        )
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
    sd_invert_image : BoolProperty(
        name="sd_invert_image",
        description="sd_invert_image",
        default = False
        )

# ========
# REGISTER
# ========
_classes=[
SD_render_op,
CN_Utils_segmentator_op,
B2SD_PT_main_pannel,
B2SD_PT_CNSegmentator,
B2SD_PG_b2sdSettings,
B2SD_OT_actions,
B2SD_UL_items,
B2SD_PG_ControlNetCollection
]

def register():
    from bpy.utils import register_class
    for cls in _classes:
        register_class(cls)

    bpy.types.Scene.b2sd = PointerProperty(type=B2SD_PG_b2sdSettings)
    bpy.types.Scene.custom = CollectionProperty(type=B2SD_PG_ControlNetCollection)
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
def b64_img(image):
    buffered = io.BytesIO()
    image.save(buffered, format="PNG")
    img_base64 = 'data:image/png;base64,' + str(base64.b64encode(buffered.getvalue()), 'utf-8')
    return img_base64

def raw_b64_img(image):
    buffered = io.BytesIO()
    image.save(buffered, format="PNG")
    img_base64 = str(base64.b64encode(buffered.getvalue()), 'utf-8')
    return img_base64

def decode_b64(base64_img):
    try:
        res = None
        if not Image:
            res = base64.b64decode(base64_img.replace("data:image/png;base64,", ""))
        else:
            res = Image.open(io.BytesIO(base64.b64decode(base64_img)))
        return res
    except:
        print("Couldn't decode base64 image.")
        return

def encode_b64(in_img):
    try:
        res = None
        if Image:
            res = Image.open(in_img)
            res = raw_b64_img(res)
        else:
            img_file = open(in_img, 'rb')
            res = base64.b64encode(img_file.read()).decode()
            img_file.close()
        return res
    except:
        print("Couldn't encode base64 image.")
        return

def save_b64(path, img):
    if Image:
        img.save(path)
    else:
        with open(path, 'wb') as file:
            file.write(img)

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

def _rembg(input_path):
    output_path = "%s_rembg.png"%os.path.splitext(input_path)[0]
    try:
        _input = Image.open(input_path)
        output = remove(_input)
        output.save(output_path)

        print("rembg img: %s"%output_path)

    except Exception as e:
        print(e)
    return output_path

def parseCN(cn_list):
    res = []
    for i in cn_list:
        cn_cur = {
            "input_image": encode_b64(i.sd_cn_img),
            "module": i.module,
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
            "invert_image": i.sd_invert_image,
        }
        res.append(cn_cur)

    return res

def parseSDArgs(args):
    """
    'cfg_scale': '7',
    'del': 'Mask blur',
    'denoising_strength': '0.75',
    'model': 'macaronMix_v10',
    'modelhash': '0b9c8fd3a8',
    'nprompt': None,
    'prompt': None,
    'sampler_index': 'Euler a',
    'seed': '88888',
    'size': '512x512',
    'steps': '20'
    """
    args = args.replace('\n', '').replace('\r', '')
    regex = re.compile(_input_parser_regex)
    re_match = regex.match(args)
    if not re_match: return
    res = re_match.groupdict()
    # pprint(res)
    for k, v in res.items():
        try:
            res[k]=re.sub(r'(^.*?:(\s)|,.*?$)',"",v)
            if k == "nprompt" or k == "prompt":
                res[k]=re.sub(r'^.*?:',"",v)
        except:
            continue
    # pprint(res)
    return res

def run_sd(fimg, kwargs):
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
    _sd_base_img_path = kwargs["sd_base_image"]
    _sd_isImg2img     = kwargs["sd_isImg2img"]
    if _sd_base_img_path and _sd_isImg2img:
        isExists = os.path.isfile(_sd_base_img_path)
        if not isExists:
            print("%s is not exists"%_sd_base_img_path)
            return
        # _sd_base_img = Image.open(_sd_base_img_path)
        # _sd_base_img = _sd_base_img.resize((512,512))
        _sd_base_img = encode_b64(_sd_base_img)
        sd_cmd = "img2img"

    url = f"http://localhost:7860/sdapi/v1/{sd_cmd}"

    cn_units = parseCN(kwargs["sd_cn_list"]) if kwargs["sd_cn_list"] else []

    body = {
        "init_images":          [_sd_base_img] if _sd_base_img else [],
        "prompt":               kwargs["sd_prompt"],
        "negative_prompt":      kwargs["sd_negative_prompt"],
        "seed":                 int(kwargs["sd_seed"]),
        "subseed":              -1,
        "subseed_strength":     0,
        "denoising_strength":   kwargs["sd_args"]["denoising_strength"],
        "batch_size":           1,
        "n_iter":               1,
        "steps":                kwargs["sd_args"]["steps"],
        "cfg_scale":            kwargs["sd_args"]["cfg_scale"],
        "width":                int(kwargs["sd_rw"]),
        "height":               int(kwargs["sd_rh"]),
        "restore_faces":        False,
        "eta":                  0,
        "sampler_index":        kwargs["sd_args"]["sampler_index"],
        "alwayson_scripts":
        {
            "ControlNet":
            {
                "args": cn_units
            },
            "Cutoff":
            {
                "args": [
                    True, # enabled: bool
                    "white, green, red, blue, yellow, pink",  # targets: string
                    2,  # weight: float
                    False,  # disable_neg: bool
                    False,  # strong: bool (Cutoff strongly)
                    "",  # padding: string or int (Padding token (ID or single token))
                    "Lerp",  # inpt: string (Interpolation method) Possible values: ["Lerp", "SLerp" ]
                    False,  #debug: bool (useful if you want to make sure it's working, check the output below)
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


    sd_out_path = kwargs["sd_out_path"]
    if not sd_out_path:
        print("%s fail"%sd_out_path)
        return
    if not os.path.exists(sd_out_path):
        os.makedirs(sd_out_path)

    sd_out_img_path = "%s/%s"%(sd_out_path,os.path.basename(fimg))
    save_b64(sd_out_img_path, decode_b64(res["images"][0]))

    if kwargs["sd_isRembg"]:
        _rembg(sd_out_img_path)

    print("sd_out_img: %s"%sd_out_img_path)

# =====
# class
# =====
class BUtils:
    def __init__(self):
        self.scn = bpy.context.scene
        self.DATA = {
            "sd_rw"  : self.scn.render.resolution_x,
            "sd_rh"  : self.scn.render.resolution_y
        }

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
        # s.render.filepath = "//" # todo
        # bpy.ops.render.render( #{'dict': "override"},
        #                         #'INVOKE_DEFAULT',
        #                         False,            # undo support
        #                         animation=False,
        #                         write_still=True
        #                         )

        bpy.ops.render.render(
            animation=False,
            write_still=True,
            use_viewport=False,
            layer=subfix
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

    def getRenderLayer(self, scn, name):
        # render_layers = scn.view_layers
        try:
            match_name = None
            for i in scn.view_layers:
                n = i.name
                re_match = name.lower() == n.lower()
                if re_match:
                    match_name = n
                    print("found a render layer: %s"%n)
                    break
            if not match_name:
                print("cannot find a render layer: %s"%name)
                return

            # vl = scn.view_layers[match_name]
            # bpy.context.window.view_layer = vl
            # bpy.context.window.view_layer.use = True
            # print("show %s"%name)

            return match_name
        except Exception as e:
            print(e)
            return

    def getControlNetList(self, scn, sd_cn_image_folder, sd_cn_list):
        res = []
        for j in range(len(sd_cn_list)):
            # if not sd_cn_list[j].render_collection:
            #     print("%s have render_collection parameter is empty"%sd_cn_list[j].model)
            #     continue
            # coleName = sd_cn_list[j].render_collection.name

            modelName = re.search(r'_(?P<model>.*?)-',sd_cn_list[j].model)["model"]

            renderLayerName = self.getRenderLayer(scn, modelName)
            if not renderLayerName: continue
            # self.hideColeByname(scn, coleName) #todo this is wrong
            currentImgPath            = self.bRender(sd_cn_image_folder, subfix = renderLayerName)
            sd_cn_list[j].sd_cn_img   = currentImgPath
            res.append(sd_cn_list[j])
        return res

    def __sd_run(self, kwargs):
        currentImgPath = kwargs["sd_cn_list"][0].sd_cn_img
        run_sd(currentImgPath, kwargs)
        return currentImgPath

    def doit(self, **kwargs):
        """
        isRenAnim : bool
            set it true when you want to render seq
        sd_isImg2img : bool
            set it true when you want to use img2img
        sd_base_image : str
            a base image for imag2img cmd
        sd_prompt : str
            sd prompt
        sd_negative_prompt : str
            sd negative prompt
        sd_seed : int
            sd seed
        sd_root_out_path : str
            output folder
        sd_isrembg : bool
            remove bg in sd output img
        sd_rw: int
            render width
        sd_rh: int
            render height
        sd_args : string
            some parameters from stable diffusion webui
            ex:
                Steps: 20, Sampler: DPM++ 2M Karras, CFG scale: 7, Seed: 88888, Size: 512x512, Model hash: 0b9c8fd3a8, Model: macaronMix_v10, Denoising strength: 0.75
        """
        kwargs["sd_args"]       = parseSDArgs(kwargs["sd_args"])
        root                    = kwargs["sd_root_out_path"]
        sd_cn_image_folder      = f"{root}/cn_images"
        kwargs["sd_out_path"]   = f"{root}/sd_images"
        kwargs["sd_rw"]         = self.DATA["sd_rw"]
        kwargs["sd_rh"]         = self.DATA["sd_rh"]

        if not kwargs["isanim"]:
            sd_cn_list = self.getControlNetList(self.scn, sd_cn_image_folder, kwargs["sd_cn_list"])

            if not sd_cn_list:
                print("control net is fail")
                return
            kwargs["sd_cn_list"]  = sd_cn_list
            currentImgPath = self.__sd_run(kwargs)

            output_path = currentImgPath.replace(sd_cn_image_folder,kwargs["sd_out_path"])
            if kwargs["sd_isRembg"]:
                output_path = "%s_rembg.png"%os.path.splitext(output_path)[0]
            self.displayImg(output_path)

        else:
            for i in range(self.scn.frame_start,self.scn.frame_end):
                self.scn.frame_current = i

                sd_cn_list = self.getControlNetList(self.scn, sd_cn_image_folder, kwargs["sd_cn_list"])

                if not sd_cn_list:
                    print("control net is fail")
                    return
                kwargs["sd_cn_list"]  = sd_cn_list
                currentImgPath = self.__sd_run(kwargs)

if __name__ == "__main__":
    register()
